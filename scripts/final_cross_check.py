import sqlite3
import hashlib

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

print(f"--- COMPARATIVA FINAL ---")
print(f"DB1: {db1} ({f1['tables']} tablas)")
print(f"DB2: {db2} ({f2['tables']} tablas)")

if f1 == f2:
    print("\n[OK] LAS BASES ESTÁN 100% ESPEJADAS (Esquema y Tablas).")
    # Check specific critical columns
    critical_cols = [
        ("clientes", "transporte_habitual_id"),
        ("domicilios", "flags_estado"),
        ("productos_costos", "margen_sugerido")
    ]
    for t, c in critical_cols:
        if c in f1["columns"].get(t, []):
            print(f"[OK] Columna '{c}' presente en '{t}'.")
        else:
            print(f"[ERR] FALTANTE: '{c}' en '{t}'.")
else:
    print("\n[ALERTA] Diferencia en esquema detectada.")
