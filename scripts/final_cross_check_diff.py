import sqlite3

def get_db_fingerprint(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = sorted([t[0] for t in cursor.fetchall()])
    fingerprint = {"tables": len(tables), "columns": {}}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        fingerprint["columns"][table] = sorted([col[1] for col in cursor.fetchall()])
    conn.close()
    return fingerprint

db1 = r"C:\dev\Sonido_Liquido_V5\pilot_v5x.db"
db2 = r"C:\dev\V5-LS\data\V5_LS_MASTER.db"

f1 = get_db_fingerprint(db1)
f2 = get_db_fingerprint(db2)

print(f"--- DETALLE DE DIFERENCIAS ---")
if f1["tables"] != f2["tables"]:
    print(f"TABLAS: DB1 tiene {f1['tables']}, DB2 tiene {f2['tables']}")
    t1 = set(f1["columns"].keys())
    t2 = set(f2["columns"].keys())
    print(f"  Solo en DB1: {t1 - t2}")
    print(f"  Solo en DB2: {t2 - t1}")

for table in f1["columns"]:
    if table in f2["columns"]:
        c1 = set(f1["columns"][table])
        c2 = set(f2["columns"][table])
        if c1 != c2:
            print(f"TABLA '{table}':")
            print(f"  Solo en DB1: {c1 - c2}")
            print(f"  Solo en DB2: {c2 - c1}")
