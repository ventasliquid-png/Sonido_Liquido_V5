import sqlite3
import os

DEV_DB = r"C:\dev\Sonido_Liquido_V5\pilot_v5x.db"
PROD_DB = r"C:\dev\V5-LS\data\V5_LS_MASTER.db"

def get_schema(db_path):
    if not os.path.exists(db_path):
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = {row[1]: {"type": row[2], "notnull": row[3], "pk": row[5]} for row in cursor.fetchall()}
        schema[table] = columns
    
    conn.close()
    return schema

def compare_schemas():
    print("=== AUDITORÍA DE ESQUEMA DE BASE DE DATOS ===")
    
    schema_dev = get_schema(DEV_DB)
    schema_prod = get_schema(PROD_DB)
    
    if not schema_dev:
        print(f" [!] Error: No se encontró DB de DEV en {DEV_DB}")
        return
    if not schema_prod:
        print(f" [!] Error: No se encontró DB de PROD en {PROD_DB}")
        return
    
    # Tables check
    tables_dev = set(schema_dev.keys())
    tables_prod = set(schema_prod.keys())
    
    only_dev = tables_dev - tables_prod
    only_prod = tables_prod - tables_dev
    common = tables_dev & tables_prod
    
    print(f"\n[TABLAS]")
    print(f" Comunes: {len(common)}")
    if only_dev: print(f" [!] Solo en DEV: {only_dev}")
    if only_prod: print(f" [!] Solo en PROD: {only_prod}")
    
    # Columns check in common tables
    found_diff = False
    for table in sorted(common):
        cols_dev = set(schema_dev[table].keys())
        cols_prod = set(schema_prod[table].keys())
        
        diff_dev = cols_dev - cols_prod
        diff_prod = cols_prod - cols_dev
        
        if diff_dev or diff_prod:
            found_diff = True
            print(f"\n[DIVERGENCIA EN TABLA: {table}]")
            if diff_dev: print(f"  [<] Columnas solo en DEV: {diff_dev}")
            if diff_prod: print(f"  [>] Columnas solo en PROD: {diff_prod}")

    if not found_diff:
        print("\n [OK] Los esquemas de las tablas comunes son idénticos.")

if __name__ == "__main__":
    compare_schemas()
