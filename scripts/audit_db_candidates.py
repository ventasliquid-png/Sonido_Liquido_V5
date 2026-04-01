import sqlite3
import os

db_files = [f for f in os.listdir('.') if f.endswith('.db')]
# Add the master from V5-LS
master_path = r"C:\dev\V5-LS\data\V5_LS_MASTER.db"
if os.path.exists(master_path):
    db_files.append(master_path)

def get_db_info(path):
    info = {"path": path, "size": os.path.getsize(path), "tables": {}, "missing_columns": []}
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            info["tables"][table] = [col[1] for col in cursor.fetchall()]
        
        # Check target columns specifically
        if "clientes" in info["tables"]:
            if "transporte_habitual_id" not in info["tables"]["clientes"]:
                info["missing_columns"].append("clientes.transporte_habitual_id")
        else:
             info["missing_columns"].append("MISSING 'clientes' table")
             
        if "domicilios" in info["tables"]:
            if "flags_estado" not in info["tables"]["domicilios"]:
                info["missing_columns"].append("domicilios.flags_estado")
        
        if "productos_costos" in info["tables"]:
            if "margen_sugerido" not in info["tables"]["productos_costos"]:
                info["missing_columns"].append("productos_costos.margen_sugerido")

        conn.close()
    except Exception as e:
        info["error"] = str(e)
    return info

print("--- DIAGNÓSTICO FORENSE DE BASES DE DATOS ---")
for f in db_files:
    # Resolve relative paths
    full_path = os.path.abspath(f) if not os.path.isabs(f) else f
    info = get_db_info(full_path)
    print(f"\nBASE: {os.path.basename(full_path)}")
    print(f" PATH: {full_path}")
    print(f" SIZE: {info['size']} bytes")
    if "error" in info:
        print(f" ERROR: {info['error']}")
    else:
        print(f" TABLAS: {len(info['tables'])}")
        if info["missing_columns"]:
            print(f" COLUMNAS FALTANTES: {', '.join(info['missing_columns'])}")
        else:
            print(f" ESTADO: NOMINAL GOLD (Columnas OK)")
