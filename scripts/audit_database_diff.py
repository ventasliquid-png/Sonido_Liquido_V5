import sqlite3
import pandas as pd
import os

def audit_diff(db_a_path, db_b_path, output_path):
    print(f"Auditando: {db_a_path} (A) vs {db_b_path} (B)")
    
    conn_a = sqlite3.connect(db_a_path)
    conn_b = sqlite3.connect(db_b_path)
    
    # 1. Cargar datos básicos
    df_a = pd.read_sql_query("SELECT id, sku, nombre FROM productos", conn_a)
    df_b = pd.read_sql_query("SELECT id, sku, nombre FROM productos", conn_b)
    
    # Limpieza básica para comparación
    df_a['sku_clean'] = df_a['sku'].fillna('').str.strip()
    df_b['sku_clean'] = df_b['sku'].fillna('').str.strip()
    df_a['nombre_clean'] = df_a['nombre'].fillna('').str.strip().str.upper()
    df_b['nombre_clean'] = df_b['nombre'].fillna('').str.strip().str.upper()

    # Identificar registros con SKU vacío
    empty_sku_a = df_a[df_a['sku_clean'] == '']
    empty_sku_b = df_b[df_b['sku_clean'] == '']
    
    print(f"Total registros A: {len(df_a)} (Vacíos SKU: {len(empty_sku_a)})")
    print(f"Total registros B: {len(df_b)} (Vacíos SKU: {len(empty_sku_b)})")

    # 2. Comparación por SKU (para los que tienen SKU)
    sku_a = df_a[df_a['sku_clean'] != '']
    sku_b = df_b[df_b['sku_clean'] != '']
    
    missing_sku = sku_a[~sku_a['sku_clean'].isin(sku_b['sku_clean'])].copy()
    missing_sku['motivo'] = "SKU eliminado"
    
    # 3. Comparación por Nombre (para los que no tienen SKU o por si el SKU cambió)
    # Buscamos nombres en B que ya no están
    missing_nombre = df_a[~df_a['nombre_clean'].isin(df_b['nombre_clean'])].copy()
    missing_nombre['motivo'] = "Nombre eliminado"

    # Consolidar (Evitar duplicados)
    diffs = pd.concat([missing_sku, missing_nombre]).drop_duplicates(subset=['nombre_clean'])
    
    # Solo nos interesan los que estaban en A (270) y no están en B (173)
    # Un total de ~97 registros
    
    # Añadir detalle de 'Lo que hay en 173 que no estaba en 270'
    new_in_b = df_b[~df_b['nombre_clean'].isin(df_a['nombre_clean'])].copy()
    new_in_b['motivo'] = "Producto nuevo en V6"

    report = pd.concat([diffs, new_in_b])
    report[['sku', 'nombre', 'motivo']].to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ Reporte final generado: {output_path} ({len(report)} registros)")
    
    conn_a.close()
    conn_b.close()

if __name__ == "__main__":
    audit_diff("pilot_pre_purge.db", "pilot.db", "REPORTE_TECNICO_DATOS.csv")
