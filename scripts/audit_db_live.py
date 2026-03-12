
import sys
import os
import sqlite3
import pandas as pd
from decimal import Decimal

# Helper to print tables
def print_table(df, title):
    print(f"\n--- {title} ---")
    if df.empty:
        print("(Empty)")
    else:
        print(df.to_markdown(index=False))

def audit_db():
    # LOCATE DB
    # Based on main.py logic, pilot.db is in ROOT or BACKEND.
    # We will try ROOT first.
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(root_dir, 'pilot.db')
    
    if not os.path.exists(db_path):
        print(f"❌ DB not found at {db_path}. Trying backend...")
        db_path = os.path.join(root_dir, 'backend', 'pilot.db')
        if not os.path.exists(db_path):
            print(f"❌ DB not found at {db_path}. Abort.")
            return

    print(f"✅ Scanning Database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    
    # 1. CLIENTES AUDIT
    print("\n🔍 --- AUDITORÍA CLIENTES ---")
    
    # Schema check
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(clientes)")
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Campos Detectados: {columns}")
    
    # Data check
    query_cli = """
    SELECT 
        razon_social, 
        cuit, 
        segmento_id, 
        condicion_iva_id, 
        estrategia_precio 
    FROM clientes 
    LIMIT 5
    """
    try:
        df_cli = pd.read_sql_query(query_cli, conn)
        print_table(df_cli, "Muestreo Clientes (Top 5)")
        
        # Check nulls
        null_seg = pd.read_sql_query("SELECT count(*) as count FROM clientes WHERE segmento_id IS NULL", conn)['count'][0]
        null_iva = pd.read_sql_query("SELECT count(*) as count FROM clientes WHERE condicion_iva_id IS NULL", conn)['count'][0]
        print(f"\nAlertas Clientes:")
        print(f"- Segmentos Nulos: {null_seg}")
        print(f"- Condición IVA Nulos: {null_iva}")
        
    except Exception as e:
        print(f"❌ Error leyendo clientes: {e}")

    # 2. PRODUCTOS AUDIT
    print("\n🔍 --- AUDITORÍA PRODUCTOS ---")
    
    query_prod = """
    SELECT 
        p.id, 
        p.nombre, 
        pc.costo_reposicion, 
        pc.rentabilidad_target, 
        pc.precio_roca 
    FROM productos p
    LEFT JOIN productos_costos pc ON p.id = pc.producto_id
    LIMIT 5
    """
    try:
        df_prod = pd.read_sql_query(query_prod, conn)
        print_table(df_prod, "Muestreo Productos (Top 5)")
        
        # Check zeros
        zeros = pd.read_sql_query("SELECT count(*) as count FROM productos_costos WHERE costo_reposicion = 0 OR costo_reposicion IS NULL", conn)['count'][0]
        print(f"\nAlertas Productos:")
        print(f"- Costos Cero/Null: {zeros}")
        
    except Exception as e:
        print(f"❌ Error leyendo productos: {e}")

    # 3. SEGMENTOS AUDIT
    print("\n🔍 --- AUDITORÍA SEGMENTOS ---")
    try:
        # Check if 'nivel' exists
        cursor.execute("PRAGMA table_info(segmentos)")
        seg_cols = [info[1] for info in cursor.fetchall()]
        print(f"Campos en Segmentos: {seg_cols}")
        
        if 'nivel' in seg_cols:
            df_seg = pd.read_sql_query("SELECT id, nombre, nivel FROM segmentos", conn)
            print_table(df_seg, "Segmentos Configurados")
        else:
            print("⚠️ CAMPO 'NIVEL' NO EXISTE EN DB (Requiere Migración)")
            df_seg = pd.read_sql_query("SELECT id, nombre FROM segmentos", conn)
            print_table(df_seg, "Segmentos (Sin Nivel)")
            
    except Exception as e:
        print(f"❌ Error leyendo segmentos: {e}")

    conn.close()

if __name__ == "__main__":
    audit_db()
