# NODO Tienda — arquitectura integrada con NODO Gestión

Estado: diseño inicial para implementación en QA.
Fecha: 2026-09-15.

## Objetivo

Convertir `nodo-herramientas` en una tienda virtual operativa, conectada a NODO Gestión como sistema de registro para catálogo, precios, stock propio, pedidos, reservas, clientes y abastecimiento. La tienda no mantiene una segunda verdad comercial.

## Principio central

- NODO Gestión es la fuente de verdad interna.
- NODO Tienda es el canal público de venta.
- Lüsqtoff B2B es una fuente externa de disponibilidad/costo, nunca el stock físico propio.
- La web pública de Lüsqtoff puede aportar PVP, ficha, descripción e imágenes cuando esté permitido y sea técnicamente estable.
- IA ayuda a interpretar cambios, descripciones y anomalías; no inventa stock ni reemplaza validaciones determinísticas.

## Flujo objetivo

```text
Lüsqtoff B2B / web pública
          |
          v
Sincronizador proveedor
          |
          v
Fuente proveedor + historial de sync
          |
          +----> reglas de precio ----> item.precio / propuesta de cambio
          |
          +----> disponibilidad proveedor
          |
          v
NODO Gestión (Supabase)
 item / proveedor / stock / pedidos / reservas
          |
          v
API pública controlada
          |
          v
NODO Tienda (Next.js / Vercel)
 catálogo -> carrito -> checkout -> pedido
          |
          v
pedido_comercial -> NODO Gestión
```

## Modelo de disponibilidad

No sobrescribir `movimiento_stock` con stock del proveedor.

- `stock propio`: saldo real de NODO Gestión por sucursal.
- `stock reservado`: `reserva_stock`.
- `stock disponible propio`: saldo menos reservas.
- `stock proveedor`: señal externa separada, con fecha de consulta y nivel de confianza.
- `disponibilidad web`: regla comercial derivada de ambos.

Estados sugeridos en tienda:

- `entrega_inmediata`: stock propio disponible > 0.
- `disponible_proveedor`: sin stock propio pero proveedor reporta disponibilidad.
- `consultar`: dato externo viejo, ambiguo o sin confirmación.
- `sin_stock`: sin stock propio y proveedor reporta no disponible.

Un pedido que depende sólo de stock de proveedor debe quedar pendiente de confirmación/abastecimiento y no simular una reserva física propia.

## Extensión de datos propuesta

Agregar en NODO Gestión, mediante migración revisada y probada en QA:

### `canal_tienda_item`

Metadatos públicos que no corresponden al núcleo `item`:

- `organizacion_id`
- `item_id`
- `slug`
- `publicado`
- `descripcion_corta`
- `descripcion_larga`
- `categoria_publica`
- `marca`
- `imagen_principal_url`
- `imagenes_json`
- `destacado`
- `seo_title`
- `seo_description`
- timestamps

### `proveedor_item`

Mapeo entre un ítem interno y el código del proveedor:

- `organizacion_id`
- `proveedor_id`
- `item_id`
- `codigo_proveedor`
- `url_producto`
- `activo`
- unique por proveedor + código.

### `proveedor_disponibilidad`

Último estado externo y trazabilidad:

- `organizacion_id`
- `proveedor_id`
- `item_id`
- `codigo_proveedor`
- `estado` (`disponible`, `sin_stock`, `consultar`)
- `cantidad` nullable: sólo si B2B entrega cantidad confiable.
- `costo_proveedor` nullable.
- `pvp_proveedor` nullable.
- `observado_en`
- `fuente`
- `hash_fuente`

### `proveedor_sync_ejecucion`

Auditoría de cada corrida:

- inicio/fin
- origen
- cantidad revisada
- cambios
- errores
- estado
- detalle resumido

## Regla de precios

La automatización no debe cambiar precios sin límites.

Configurable por organización:

- estrategia: `margen_sobre_costo`, `seguir_pvp`, `manual`.
- margen mínimo.
- redondeo comercial.
- máximo cambio automático por corrida.
- diferencia mayor al umbral => propuesta para aprobar, no publicación automática.

Nunca exponer costo de compra en la API pública.

## Catálogo público

La tienda sólo puede leer una proyección segura con:

- id público / slug
- código/SKU comercial
- nombre
- descripción
- categoría
- imágenes
- precio final
- estado de disponibilidad
- entrega estimada

No debe tener acceso anónimo a `item.costo`, compras, proveedores, usuarios ni libros contables.

## Pedidos web

El checkout debe crear `pedido_comercial` con `canal_origen = web` (o valor equivalente aprobado por el CHECK vigente), sucursal elegida y líneas congeladas con precio vigente.

Datos mínimos del comprador:

- nombre
- WhatsApp/teléfono
- email opcional
- modalidad: retiro/envío
- dirección cuando corresponda
- observaciones

La confirmación del pedido debe respetar el flujo actual de NODO Gestión y sus reglas de reserva. No duplicar lógica de stock en la tienda.

## Sincronización con Lüsqtoff

Orden de preferencia técnica:

1. API/endpoint B2B estable, si existe y se puede usar con la cuenta comercial.
2. Lectura HTTP de datos estructurados autenticados.
3. Automatización de navegador (Playwright) autenticada.
4. Importación de archivo XLSX/CSV como contingencia.

La web pública se usa como fuente secundaria de PVP y contenido. El portal oficial de clientes está en `b2b.lusqtoff.com.ar`.

Credenciales: nunca versionarlas. Guardarlas como secretos del entorno que ejecute el sincronizador.

## Scheduler

Frecuencia inicial recomendada:

- disponibilidad: cada 2 horas durante horario comercial.
- precios/costos: 2 veces al día.
- catálogo público: 1 vez al día.
- ejecución manual disponible desde administración.

Si el proveedor cambia la interfaz, el job debe fallar cerrado: conservar el último dato conocido, marcarlo como vencido y avisar. No interpretar un error de scraping como `sin_stock`.

## IA / Cowork

Usos correctos:

- detectar que cambió la estructura del proveedor;
- proponer nuevo selector/parser;
- comparar descripciones/fichas;
- generar copy comercial a partir de datos verificables;
- resumir cambios de precio/stock;
- priorizar qué productos revisar;
- avisar anomalías.

No usar IA para inventar un número de stock ni para confirmar una venta cuando la fuente no lo confirmó.

## Tecnología

- Frontend/SSR/API: Next.js App Router.
- Hosting: Vercel.
- Datos/autenticación/RLS: Supabase de NODO Gestión.
- Sync B2B: job Node/Playwright o endpoint estructurado, según auditoría del portal.
- Observabilidad: tabla de ejecuciones + logs + alertas.
- Pagos etapa posterior: Mercado Pago Checkout/Webhook, con idempotencia.

## Fases de implementación

### Fase A — tienda base contra QA

- Migrar `nodo-herramientas` de HTML estático a Next.js.
- Crear catálogo responsive con búsqueda/categorías.
- Importar catálogo existente y mapear códigos.
- Conectar sólo a Supabase QA.
- Crear carrito y checkout sin cobro online.
- Alta de pedido real en Gestión.

### Fase B — proveedor

- Auditar B2B con sesión comercial real.
- Identificar API o endpoints de catálogo/stock.
- Implementar adaptador.
- Guardar disponibilidad externa separada.
- Mostrar `entrega inmediata`, `disponible proveedor`, `consultar`, `sin stock`.

### Fase C — precios

- Reglas de margen/PVP.
- historial y propuesta de cambios.
- límites de seguridad.
- actualización automática sólo dentro de tolerancias.

### Fase D — operación comercial

- Mercado Pago.
- avisos de pedido nuevo.
- estados del pedido visibles al cliente.
- envío/retiro.
- promociones y destacados.

### Fase E — IA operativa

- resumen diario de cambios.
- contenido comercial asistido.
- diagnóstico de fallos del sincronizador.
- sugerencias de reposición en función de ventas, stock propio y disponibilidad proveedor.

## Criterio de salida a producción

Antes de producción deben quedar probados en QA:

- un producto publicado no expone costo;
- un precio cambiado en Gestión aparece en Tienda;
- el stock propio nunca se reemplaza con stock del proveedor;
- dos checkouts concurrentes no sobre-reservan stock propio;
- un pedido web aparece en Gestión con sus líneas y origen;
- reintentar checkout no duplica el pedido;
- caída del B2B no convierte todo a `sin_stock`;
- credenciales del proveedor no aparecen en repo, cliente ni logs;
- RLS/advisors sin hallazgos críticos.
