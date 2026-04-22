# [IDENTIDAD] - scripts/pricing_auditor.py
# Misión: Saneamiento de Precios V5.9.1
# ---------------------------------------------------------
import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = 'pilot_v5x.db'

def run_audit():
    print(f"--- SONIDO LIQUIDO V5: AUDITORÍA DE PRECIOS [{datetime.now().strftime('%Y-%m-%d %H:%M')}] ---")
    
    if not os.path.exists(DB_PATH):
        print(f"ERROR: No se encuentra la base de datos en {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # query de orfandad
    query = """
    SELECT 
        p.id, 
        p.sku, 
        p.nombre, 
        p.activo,
        p.rubro_id,
        r.nombre as rubro_nombre,
        pc.costo_reposicion,
        pc.rentabilidad_target,
        pc.precio_roca
    FROM productos p
    LEFT JOIN productos_costos pc ON p.id = pc.producto_id
    LEFT JOIN rubros r ON p.rubro_id = r.id
    WHERE pc.costo_reposicion IS NULL OR pc.costo_reposicion = 0
    ORDER BY p.id ASC
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    total_prods = df.shape[0]
    
    if total_prods == 0:
        print("ESTADO: NOMINAL GOLD. No se detectaron productos sin costo.")
        return

    print(f"ALERTA: Se detectaron {total_prods} productos con costo $0 o Nulo.")
    print("-" * 60)
    
    # Resumen por rubro
    rubro_stats = df['rubro_nombre'].value_counts()
    print("RESUMEN POR RUBRO:")
    for rubro, count in rubro_stats.items():
        print(f"  > {rubro or 'SIN RUBRO'}: {count}")
    
    print("-" * 60)
    print("DETALLE DE PRODUCTOS AFECTADOS:")
    for _, row in df.iterrows():
        status = "ACTIVO" if row['activo'] else "BAJA"
        print(f"[{row['id']:4}] SKU-{row['sku']:8} | {row['nombre'][:40]:40} | {status}")

    # Exportar para saneamiento
    csv_name = f"AUDITORIA_PRECIOS_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    df.to_csv(csv_name, index=False)
    print("-" * 60)
    print(f"EXPORTADO: Se ha generado {csv_name} para saneamiento masivo.")
    print("TIP: Use este archivo para cargar los costos y realice un 'UPDATE' masivo.")

if __name__ == "__main__":
    run_audit()
