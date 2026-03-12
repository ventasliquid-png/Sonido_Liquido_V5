import sqlite3
import pandas as pd
import os

def compare_dbs(db_a_path, db_b_path, output_path):
    """
    Compara dos bases de datos SQLite y genera un reporte de diferencias.
    A = pilot_pre_purge.db (270 items)
    B = pilot.db (173 items)
    """
    print(f"--- Comparando {db_a_path} vs {db_b_path} ---")
    
    conn_a = sqlite3.connect(db_a_path)
    conn_b = sqlite3.connect(db_b_path)
    
    # Cargar productos
    df_a = pd.read_sql_query("SELECT id, sku, nombre, rubro_id, activo FROM productos", conn_a)
    df_b = pd.read_sql_query("SELECT id, sku, nombre, rubro_id, activo FROM productos", conn_b)
    
    # Identificar diferencias usando merge
    merged = pd.merge(df_a, df_b, on='sku', how='outer', suffixes=('_old', '_new'), indicator=True)
    
    # 1. Desaparecidos (Están en Old pero no en New)
    missing = merged[merged['_merge'] == 'left_only'].copy()
    missing['motivo'] = "Eliminado (Estaba en la de 270, no está en la de 173)"
    
    # 2. Nuevos (Están en New pero no en Old)
    new = merged[merged['_merge'] == 'right_only'].copy()
    new['motivo'] = "Nuevo (Está en la de 173, no estaba en la de 270)"
    
    # 3. Cambios de estado (Están en ambos pero cambió 'activo' o 'nombre')
    both = merged[merged['_merge'] == 'both'].copy()
    changed = both[(both['activo_old'] != both['activo_new']) | 
                  (both['nombre_old'] != both['nombre_new'])].copy()
    changed['motivo'] = "Diferente (Cambió nombre o estado activo)"
    
    # Consolidar reporte
    final_report = pd.concat([
        missing[['sku', 'nombre_old', 'motivo']].rename(columns={'nombre_old': 'nombre'}),
        new[['sku', 'nombre_new', 'motivo']].rename(columns={'nombre_new': 'nombre'}),
        changed[['sku', 'nombre_new', 'motivo']].rename(columns={'nombre_new': 'nombre'})
    ])
    
    final_report.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"✅ Reporte generado: {output_path}")
    print(f"📊 Resumen:")
    print(f"   - Desaparecidos: {len(missing)}")
    print(f"   - Nuevos: {len(new)}")
    print(f"   - Modificados: {len(changed)}")
    
    conn_a.close()
    conn_b.close()

if __name__ == "__main__":
    db_pre = "pilot_pre_purge.db"
    db_now = "pilot.db"
    out = "REPORTE_DISCREPANCIA_BASES.csv"
    
    if os.path.exists(db_pre) and os.path.exists(db_now):
        compare_dbs(db_pre, db_now, out)
    else:
        print("Error: No se encuentran los archivos .db")
