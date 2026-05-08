import sqlite3

MIGRATION_ID = "029_facturas_notas_auditoria"
NRO_SESION = 799

DB_PATH = "C:/dev/Sonido_Liquido_V5/pilot_v5x.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

try:
    cur.execute("ALTER TABLE facturas ADD COLUMN notas_auditoria TEXT")
    print(f"[migrate_029] Columna 'notas_auditoria' agregada a facturas.")
except Exception as e:
    if "duplicate column" in str(e).lower():
        print(f"[migrate_029] SKIP — columna ya existe.")
    else:
        raise

cur.execute(
    "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
    (MIGRATION_ID, NRO_SESION)
)
conn.commit()
conn.close()
print(f"[migrate_029] OK — registrado en _migraciones_aplicadas.")
