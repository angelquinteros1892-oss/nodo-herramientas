#!/usr/bin/env python3
"""
NODO HERRAMIENTAS - Script para regenerar productos.json desde Excel
Uso: python exportar.py
Requiere: pip install openpyxl
"""

import openpyxl
import json
import os
import shutil
from datetime import datetime

EXCEL_FILE = 'Nodo_Herramientas_Lusqtoff_Listas_Mayorista_Minorista.xlsx'
OUTPUT_FILE = 'data/productos.json'
BACKUP_DIR = 'data/backups'

def formatear_precio(valor):
    """Formatea el precio como entero redondeado."""
    if valor is None or valor == '':
        return 0
    try:
        return int(round(float(valor)))
    except (ValueError, TypeError):
        return 0

def limpiar_texto(texto):
    """Limpia y normaliza texto."""
    if texto is None:
        return ''
    return str(texto).strip().replace("'", "")

def exportar_productos():
    """Lee el Excel y genera el JSON de productos."""
    
    print("=" * 50)
    print("  NODO HERRAMIENTAS - Exportador de Productos")
    print("=" * 50)
    
    # Verificar que existe el Excel
    if not os.path.exists(EXCEL_FILE):
        print(f"\n❌ ERROR: No se encontró el archivo '{EXCEL_FILE}'")
        print("   Asegurate de que el Excel esté en la misma carpeta que este script.")
        return False
    
    print(f"\n📊 Leyendo: {EXCEL_FILE}")
    
    # Crear backup del JSON existente
    os.makedirs(BACKUP_DIR, exist_ok=True)
    if os.path.exists(OUTPUT_FILE):
        fecha = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup = os.path.join(BACKUP_DIR, f'productos_{fecha}.json')
        shutil.copy2(OUTPUT_FILE, backup)
        print(f"💾 Backup guardado: {backup}")
    
    # Cargar Excel
    try:
        wb = openpyxl.load_workbook(EXCEL_FILE, data_only=True)
    except Exception as e:
        print(f"\n❌ ERROR al abrir el Excel: {e}")
        return False
    
    if 'Base_Costos' not in wb.sheetnames:
        print(f"\n❌ ERROR: No se encontró la hoja 'Base_Costos' en el Excel.")
        print(f"   Hojas disponibles: {', '.join(wb.sheetnames)}")
        return False
    
    ws = wb['Base_Costos']
    print(f"   Hoja 'Base_Costos': {ws.max_row - 1} filas de datos")
    
    productos = []
    errores = 0
    
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        
        try:
            id_prod = int(row[0])
            categoria = limpiar_texto(row[1]) or 'Y Más Herramientas'
            codigo = limpiar_texto(row[2]) or f'PROD-{id_prod}'
            nombre = limpiar_texto(row[3])
            detalle = limpiar_texto(row[4])
            precio_compra = float(row[5]) if row[5] else 0
            precio_mayorista = formatear_precio(row[7])
            precio_minorista = formatear_precio(row[9])
            precio_transferencia = formatear_precio(row[10])
            pagina_pdf = int(row[14]) if row[14] else 0
            estado = limpiar_texto(row[13]) or 'OK'
            
            # Calcular márgenes si los precios calculados son 0
            if precio_mayorista == 0 and precio_compra > 0:
                margen_may = float(row[6]) if row[6] and isinstance(row[6], float) else 0.25
                precio_mayorista = int(round(precio_compra * (1 + margen_may) / 100) * 100)
            
            if precio_minorista == 0 and precio_compra > 0:
                margen_min = float(row[8]) if row[8] and isinstance(row[8], float) else 0.45
                precio_minorista = int(round(precio_compra * (1 + margen_min) / 100) * 100)
            
            if precio_transferencia == 0 and precio_minorista > 0:
                precio_transferencia = int(round(precio_minorista * 0.95 / 100) * 100)
            
            productos.append({
                "id": id_prod,
                "codigo": codigo,
                "nombre": nombre,
                "detalle": detalle,
                "categoria": categoria,
                "precio_compra": round(precio_compra, 2),
                "precio_mayorista": precio_mayorista,
                "precio_minorista": precio_minorista,
                "precio_transferencia": precio_transferencia,
                "pagina_pdf": pagina_pdf,
                "estado": estado,
                "imagen": ""
            })
        except Exception as e:
            errores += 1
            print(f"   ⚠️ Error en fila {row[0]}: {e}")
    
    # Guardar JSON
    os.makedirs('data', exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(productos, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Exportación completada!")
    print(f"   📦 Productos exportados: {len(productos)}")
    print(f"   ⚠️  Errores: {errores}")
    
    # Resumen por categoría
    cats = {}
    for p in productos:
        cats[p['categoria']] = cats.get(p['categoria'], 0) + 1
    
    print(f"\n📂 Resumen por categoría:")
    for cat, n in sorted(cats.items()):
        print(f"   {cat}: {n} productos")
    
    print(f"\n💾 Archivo guardado: {OUTPUT_FILE}")
    print("\n🌐 Ahora subí el archivo actualizado a tu hosting.")
    print("=" * 50)
    
    return True

if __name__ == '__main__':
    exportar_productos()
