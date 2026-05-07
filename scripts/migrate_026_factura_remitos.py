"""
migrate_026_factura_remitos.py
Reemplaza la tabla simple facturas_remitos (PK compuesta, sin id propio)
por la versión completa con id GUID, fecha_vinculo y flags_estado.
"""
import sqlite3
import os

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or "C:/dev/Sonido_Liquido_V5/pilot_v5x.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print(f"[migrate_026] Conectado a: {DB_PATH}")

cur.executescript("""
    DROP TABLE IF EXISTS facturas_remitos;

    CREATE TABLE facturas_remitos (
        id CHAR(32) PRIMARY KEY,
        factura_id CHAR(32) NOT NULL REFERENCES facturas(id),
        remito_id  CHAR(32) NOT NULL REFERENCES remitos(id),
        fecha_vinculo DATETIME,
        flags_estado BIGINT NOT NULL DEFAULT 1,
        UNIQUE(factura_id, remito_id)
    );

    CREATE INDEX IF NOT EXISTS ix_facturas_remitos_factura_id ON facturas_remitos(factura_id);
    CREATE INDEX IF NOT EXISTS ix_facturas_remitos_remito_id  ON facturas_remitos(remito_id);
""")

conn.commit()
conn.close()
print("[migrate_026] OK — tabla facturas_remitos recreada con id/fecha_vinculo/flags_estado.")
