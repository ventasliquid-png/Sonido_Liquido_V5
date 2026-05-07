# scripts/migrate_027_facturas_schema_fix.py
import sqlite3

DB_PATH = 'C:/dev/Sonido_Liquido_V5/pilot_v5x.db'

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1. Renombrar vto_cae → cae_vencimiento (SQLite 3.25+)
cur.execute("ALTER TABLE facturas RENAME COLUMN vto_cae TO cae_vencimiento")

# 2. Columnas faltantes
cur.execute("ALTER TABLE facturas ADD COLUMN cuit_comprador VARCHAR")
cur.execute("ALTER TABLE facturas ADD COLUMN pdf_path VARCHAR")
cur.execute("ALTER TABLE facturas ADD COLUMN flags_estado BIGINT NOT NULL DEFAULT 3")

conn.commit()

# Verificación
cur.execute("PRAGMA table_info(facturas)")
cols = [r[1] for r in cur.fetchall()]
print("[migrate_027] Columnas finales:", cols)

# Registro en control
cur.execute(
    "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
    ("027_facturas_schema_fix", 798)
)
conn.commit()
conn.close()
print("[migrate_027] OK")
