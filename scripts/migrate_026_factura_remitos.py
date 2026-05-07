"""
migrate_026_factura_remitos.py
====================================
PATRÓN ESTÁNDAR DE MIGRACIONES — Sonido Líquido V5
Ver migrate_000_control_migraciones.py para documentación del patrón.
====================================
Reemplaza la tabla simple facturas_remitos (PK compuesta, sin id propio)
por la versión completa con id GUID, fecha_vinculo y flags_estado.
"""
import sqlite3, os

MIGRATION_ID = "026_factura_remitos"
NRO_SESION = 797

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") \
          or "C:/dev/Sonido_Liquido_V5/pilot_v5x.db"

conn = sqlite3.connect(DB_PATH)

# Verificar si ya se aplicó
existe = conn.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()
if existe:
    print(f"[migrate_026] SKIP — {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

# Ejecutar migración
conn.executescript("""
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

# Registrar
conn.execute(
    "INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
    (MIGRATION_ID, NRO_SESION)
)
conn.commit()
conn.close()
print(f"[migrate_026] OK — facturas_remitos recreada y migración registrada.")
