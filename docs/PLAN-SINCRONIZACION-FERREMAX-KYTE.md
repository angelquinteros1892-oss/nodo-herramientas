# Plan de sincronización Ferremax/Kyte → NODO

Fecha: 2026-09-15
Estado: diseño de implementación

## Fuente del proveedor

Categoría LUSQTOFF de Ferremax Córdoba:
https://ferremaxcordoba.kyte.site/es/c/lusqtoff/1759248769072-tbLdd

Esta fuente representa disponibilidad del PROVEEDOR. No reemplaza el stock físico propio de NODO Gestión.

## Regla central

Mantener dos dimensiones independientes:

- `stock_nodo`: existencia física propia, gobernada por NODO Gestión / movimientos de stock.
- `stock_proveedor`: disponibilidad observada en Ferremax/Kyte.

La tienda deriva un `estado_comercial` sin adulterar el libro de stock de Gestión:

1. stock_nodo > 0 → `ENTREGA_INMEDIATA`.
2. stock_nodo = 0 y proveedor disponible → `DISPONIBLE_A_PEDIDO`.
3. stock_nodo = 0 y proveedor no disponible confirmado → `SIN_STOCK`.
4. lectura del proveedor vencida/fallida → `CONSULTAR` o conservar último estado con advertencia interna; nunca inferir SIN_STOCK por un error técnico.

## Fase 1 — Descubrimiento técnico de Kyte

Objetivo: encontrar el dato estructurado que alimenta el catálogo público.

1. Abrir la categoría LUSQTOFF en navegador real.
2. Inspeccionar Network (Fetch/XHR) y registrar las solicitudes que devuelven productos.
3. Identificar por producto: id Kyte, nombre, SKU/código, precio, imagen, categoría, disponibilidad/stock y URL.
4. Validar paginación/carga incremental.
5. Probar tres casos reales: disponible, sin stock y producto retirado/no publicado.
6. Guardar una muestra JSON de respuesta como fixture de desarrollo, sin credenciales ni tokens sensibles.

Preferencia de integración:

- A: endpoint público estructurado usado por el propio catálogo.
- B: HTML/datos embebidos estables.
- C: navegador automatizado (Playwright/Work) como fallback.

No depender de selectores visuales si existe una fuente JSON estructurada.

## Fase 2 — Modelo proveedor

Agregar en NODO Gestión/QA un adaptador de proveedor con entidades equivalentes a:

- proveedor_fuente
- proveedor_producto
- proveedor_lectura
- proveedor_precio_historial
- proveedor_sync_run

Campos mínimos por producto:

- proveedor = FERREMAX
- fuente_url
- external_id
- sku/codigo normalizado
- nombre_origen
- precio_proveedor observado
- disponible observado
- stock_cantidad, sólo si Kyte realmente lo expone
- imagen_url
- producto_url
- visto_en
- sincronizado_en
- hash_datos
- estado_lectura

La vinculación con `item` de NODO debe hacerse preferentemente por SKU/código explícito. Los matches por nombre son sugerencias a revisar, no escritura automática.

## Fase 3 — Sincronizador

Crear job idempotente:

`Ferremax/Kyte → extractor → normalizador → validador → staging → comparación → persistencia`

Frecuencia inicial: cada 2 horas durante la etapa de observación. Cuando haya estabilidad medida, ajustar según necesidad.

Guardas:

- si falla la descarga, NO marcar todo sin stock;
- si cae >20% del catálogo en una sola corrida, bloquear publicación automática y alertar;
- si un precio cambia >15% en una corrida, guardar cambio pero requerir revisión antes de repercutir en precio de venta;
- registrar cantidad leída, altas, bajas aparentes, cambios, errores y duración por ejecución;
- conservar el último dato válido y su antigüedad.

## Fase 4 — NODO Tienda

La tienda NO consulta Kyte directamente desde el navegador del cliente. Consulta una API pública controlada por NODO.

Por producto publicar solamente:

- nombre comercial
- descripción
- imágenes autorizadas
- precio de venta NODO
- estado comercial
- plazo/retiro/envío
- disponibilidad apta para cliente

Nunca publicar costo proveedor, margen, identificadores internos ni credenciales.

## Fase 5 — Pedidos

Checkout de NODO Tienda crea `pedido_comercial` en NODO Gestión con `canal_origen = web` (o el valor canónico que defina Gestión).

Antes de confirmar:

- si hay stock propio, reservar stock propio;
- si depende del proveedor, etiquetar el pedido como sujeto a abastecimiento hasta confirmar disponibilidad;
- guardar snapshot de precio y disponibilidad usados en la compra.

## Fase 6 — Precios

Separar:

- costo/valor observado del proveedor;
- costo de reposición contable de Gestión;
- precio de venta NODO.

El sincronizador NO debe pisar automáticamente el costo histórico/contable de una compra recibida. Puede alimentar un `costo_proveedor_observado` para decisiones de reposición y sugerencias de precio.

## Fase 7 — IA / Work

La IA supervisa y explica; no inventa stock.

Usos:

- detectar anomalías de sincronización;
- resumir productos que aparecieron/desaparecieron;
- señalar subas/bajas de precio;
- sugerir revisión de márgenes;
- generar descripción comercial para productos nuevos;
- preparar alertas de abastecimiento.

## Criterio para activar automatización plena

No publicar automáticamente `SIN_STOCK` o cambios de precio hasta completar varias corridas de observación y verificar manualmente una muestra de productos contra la página de Ferremax.
