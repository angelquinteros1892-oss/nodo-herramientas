# 🛠️ NODO HERRAMIENTAS — Catálogo Digital Lusqtoff

Catálogo web completo para **NODO HERRAMIENTAS**, distribuidor oficial de Lusqtoff en Córdoba.  
181 productos con precios mayoristas y minoristas, buscador, filtros por categoría y consulta directa por WhatsApp.

---

## 📁 Estructura del Proyecto

```
nodo-herramientas/
├── index.html              ← Página principal del catálogo
├── admin.html              ← Panel de administración
├── exportar.py             ← Script para regenerar JSON desde Excel
├── README.md               ← Este archivo
├── css/
│   └── styles.css          ← Todos los estilos (tema naranja/negro Lusqtoff)
├── js/
│   └── app.js              ← Lógica completa: filtros, modal, WhatsApp
├── data/
│   └── productos.json      ← Base de datos de productos (generada desde Excel)
│   └── backups/            ← Backups automáticos del JSON
└── assets/
    └── imagenes/           ← Imágenes de productos (agregar manualmente)
```

---

## 🚀 Cómo usar

### Ver el catálogo localmente
Abrí una terminal en la carpeta del proyecto y ejecutá:
```bash
# Python 3
python -m http.server 8080

# Luego abrí en el navegador:
# http://localhost:8080
```
> ⚠️ No abras `index.html` directo con doble clic — el JSON no cargará sin un servidor.

---

## 💰 Cómo modificar precios

### Opción 1 — Modificar el JSON directamente (simple)
1. Abrí `data/productos.json` con cualquier editor de texto (VSCode, Notepad++, etc.)
2. Buscá el producto por código (Ctrl+F → escribí el código, ej: `AB-550`)
3. Modificá `precio_mayorista`, `precio_minorista` o `precio_transferencia`
4. Guardá el archivo y subilo al hosting

### Opción 2 — Regenerar desde Excel (recomendado)
1. Editá los precios en el Excel → hoja `Base_Costos` → columna F (Precio compra)
2. Los precios se calculan automáticamente con los márgenes configurados
3. Ejecutá el script de exportación:
```bash
pip install openpyxl       # solo la primera vez
python exportar.py
```
4. Subí el nuevo `data/productos.json` al hosting

---

## 🖼️ Cómo agregar imágenes de productos

1. Guardá la imagen con el nombre del código del producto:  
   Ejemplo: `AB-550.jpg`, `L-820.png`, `ATG18-7.webp`

2. Subila a la carpeta `assets/imagenes/`

3. Editá `data/productos.json` y buscá el producto:
```json
{
  "codigo": "AB-550",
  "imagen": "assets/imagenes/AB-550.jpg",
  ...
}
```

**Tamaño recomendado:** 400×400 px, fondo blanco o transparente  
**Formatos:** `.jpg`, `.jpeg`, `.png`, `.webp`

---

## 📱 Cambiar número de WhatsApp

Abrí `js/app.js` y editá las primeras líneas:
```javascript
const CONFIG = {
  wsp: '5493511234567',  // Sin + ni espacios
  wsp_display: '+54 9 351 123-4567',
  ...
};
```

**Formato Argentina:** `54` + `9` + código de área sin `0` + número sin `15`  
Ejemplo: para `0351 15-123-4567` → `5493511234567`

---

## 🌐 Publicar en GitHub Pages (gratis)

1. Creá una cuenta en [github.com](https://github.com)
2. Creá un repositorio nuevo: `nodo-herramientas` (público)
3. Subí todos los archivos al repositorio
4. Andá a **Settings → Pages → Source** → elegí `main` branch → **Save**
5. Tu sitio estará en: `https://tuusuario.github.io/nodo-herramientas`

---

## 🌐 Publicar en Hostinger

1. Contratá un plan en [hostinger.com.ar](https://hostinger.com.ar)
2. Accedé al **hPanel → Administrador de Archivos**
3. Entrá a la carpeta `public_html`
4. **Subí todos los archivos** (index.html, admin.html, css/, js/, data/, assets/)
5. El sitio estará activo en tu dominio

---

## 🎨 Personalización de estilos

Editá las variables en `css/styles.css` (primeras líneas):
```css
:root {
  --negro: #111111;        /* Color de fondo */
  --naranja: #FF6A00;      /* Color principal */
  --naranja-dark: #CC5500; /* Hover naranja */
  --blanco: #FFFFFF;       /* Textos */
}
```

---

## ➕ Agregar nuevos productos

Abrí `data/productos.json` y agregá un nuevo objeto al array:
```json
{
  "id": 182,
  "codigo": "NUEVO-001",
  "nombre": "NOMBRE DEL PRODUCTO",
  "detalle": "Descripción comercial del producto.",
  "categoria": "Amoladoras y Corte",
  "precio_compra": 50000,
  "precio_mayorista": 62500,
  "precio_minorista": 72500,
  "precio_transferencia": 68900,
  "pagina_pdf": 0,
  "estado": "OK",
  "imagen": ""
}
```

**Categorías disponibles:**
- `Amoladoras y Corte`
- `Taladros / 220V / Batería / Accesorios`
- `Set de Herramientas Completos / Individuales`
- `Carpintería y Madera`
- `Soldadoras / Accesorios`
- `Compresores y Neumática`
- `Jardinería / Camping / Exterior`
- `Estética y Accesorios Automotor`
- `Generadores / Bomba de Agua`
- `Accesorios / Consumibles`
- `Y Más Herramientas`

---

## 🔧 Funcionalidades incluidas

| Función | Descripción |
|---|---|
| 🔍 Buscador | Por código, nombre y descripción |
| 📂 Filtro categoría | 11 categorías Lusqtoff |
| 💰 Filtro precio | Rango mín/máx |
| 🔄 Modo precio | Minorista / Mayorista |
| 💬 WhatsApp | Mensaje automático por producto |
| 👁️ Modal detalle | Vista completa del producto |
| 📱 Responsive | PC, tablet y celular |
| ⚡ Lazy loading | Carga rápida de imágenes |
| 🎯 SEO | Títulos, meta, Open Graph, Schema.org |
| ⬆️ Scroll top | Botón para volver arriba |

---

## 📊 Datos del catálogo

- **Total productos:** 181
- **Categorías:** 11
- **Fuente:** Lusqtoff Catálogo N°1 Rev.01
- **Precios:** Actualizados a junio 2026

---

## 📞 Soporte

Para consultas sobre el sitio: revisá `admin.html` en el navegador para guías paso a paso.

---

**NODO HERRAMIENTAS** — Distribuidor Oficial Lusqtoff — Córdoba, Argentina  
*"Calidad que se siente. Tecnología que avanza."*
