
import sqlite3
import pandas as pd
import os
from datetime import datetime

# Config
DB_PATH = r"c:\dev\Sonido_Liquido_V5\BUILD_PILOTO\produccion.db"
OUTPUT_DIR = r"c:\dev\Sonido_Liquido_V5\SEMILLAS_MAESTRAS"

def export_seeds():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # --- CLIENTES ---
    print("🌱 Exporting Clientes Master Seed...")
    # Listamos explicitamente columnas V5 para asegurar estandar
    # (En SQLite obtenemos lo que haya, pero podemos inyectar columnas vacias si faltan)
    df_cli = pd.read_sql_query("SELECT * FROM clientes", conn)
    
    # Guardar con Timestamp (Backup) y como 'MAESTRO' (Referencia)
    path_cli_backup = os.path.join(OUTPUT_DIR, f"clientes_master_{timestamp}.csv")
    path_cli_current = os.path.join(OUTPUT_DIR, "CLIENTES_MAESTRO_LATEST.csv")
    
    df_cli.to_csv(path_cli_backup, index=False, encoding='utf-8-sig')
    df_cli.to_csv(path_cli_current, index=False, encoding='utf-8-sig')
    
    # --- PRODUCTOS ---
    print("🌱 Exporting Productos Master Seed...")
    df_prod = pd.read_sql_query("SELECT * FROM productos", conn)
    
    path_prod_backup = os.path.join(OUTPUT_DIR, f"productos_master_{timestamp}.csv")
    path_prod_current = os.path.join(OUTPUT_DIR, "PRODUCTOS_MAESTRO_LATEST.csv")
    
    df_prod.to_csv(path_prod_backup, index=False, encoding='utf-8-sig')
    df_prod.to_csv(path_prod_current, index=False, encoding='utf-8-sig')
    
    # --- MAESTROS ADICIONALES (EXPANSIÓN) ---
    tables_to_export = [
        "empresas_transporte", "nodos_transporte", 
        "vendedores", "segmentos", 
        "condiciones_iva", "provincias", 
        "rubros", "domicilios", "contactos" # Si existe 'contactos' o 'personas'
    ]
    
    # Verificamos existencia antes de exportar para no romper
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [r[0] for r in cursor.fetchall()]
    
    for table in tables_to_export:
        if table in existing_tables:
            print(f"🌱 Exporting {table}...")
            try:
                df_t = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                if not df_t.empty:
                    path_t_current = os.path.join(OUTPUT_DIR, f"{table.upper()}_MAESTRO_LATEST.csv")
                    df_t.to_csv(path_t_current, index=False, encoding='utf-8-sig')
            except Exception as e:
                print(f"⚠️ Error exporting {table}: {e}")
        else:
            print(f"ℹ️ Table {table} not found in DB.")

    conn.close()
    print(f"✅ Semillas Maestras guardadas en: {OUTPUT_DIR}")

if __name__ == "__main__":
    export_seeds()
