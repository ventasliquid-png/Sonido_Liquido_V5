"""
migrate_045_facturas_ajustes.py
====================================
Etapa 7d del Circuito PR (PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md §9) -- tabla puente
`facturas_ajustes` entre una NC/ND y la(s) factura(s) que ajusta. Dictamen de Nike, 29/09/2026
(Sello de Oro), BIBLIOTECA_NIKE.md Modulo 2 "Como se modela NC/ND...":

  - NC y ND son filas de la MISMA tabla `facturas`, distinguidas por tipo_comprobante -- no hay
    tabla nueva de comprobantes, la UNIQUE(tipo_comprobante, punto_venta, numero_comprobante) que
    ya existe evita colision de numeracion con una Factura.
  - La relacion de ajuste es esta tabla puente, no una FK en `facturas`: ARCA permite que una sola
    NC ajuste varias facturas a la vez. `factura_ajustada_id` es nullable: una ND puede ir suelta.
  - No se agrega ninguna columna a `facturas` ni a `remitos_items`: los bits TIENE_NC/TIENE_ND/
    ES_NC/ES_ND (17-20) ya existian en FacturaFlags, y el neto de cantidad_facturada es una @property.

Solo agrega una tabla nueva y vacia (+ indices): no toca ninguna fila existente. Idempotente.
Nota: el arranque del backend tambien la crea (Base.metadata.create_all) si el modelo ya esta en el
codigo; el CREATE TABLE IF NOT EXISTS de aca hace que el orden no importe.

MIGRATION_ID = "045_facturas_ajustes"
NRO_SESION = 875
"""
import sqlite3
import os

MIGRATION_ID = "045_facturas_ajustes"
NRO_SESION = 875

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db"
)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (
        id VARCHAR PRIMARY KEY,
        nro_sesion INTEGER,
        aplicada_en DATETIME DEFAULT (datetime('now'))
    )
""")

ya_aplicada = cur.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()

if ya_aplicada:
    print(f"[migrate_045] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_045] Iniciando {MIGRATION_ID}...")

    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='facturas'").fetchone():
        raise RuntimeError("No existe la tabla 'facturas' en esta base: no es una base de V5 o esta desactualizada.")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS facturas_ajustes (
            id                   INTEGER  PRIMARY KEY AUTOINCREMENT,
            factura_nc_nd_id     CHAR(32) NOT NULL REFERENCES facturas(id),
            factura_ajustada_id  CHAR(32)          REFERENCES facturas(id),
            monto_aplicado       FLOAT,
            fecha_vinculo        DATETIME,
            CONSTRAINT uq_factura_ajuste UNIQUE (factura_nc_nd_id, factura_ajustada_id)
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS ix_facturas_ajustes_id ON facturas_ajustes(id)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_facturas_ajustes_factura_nc_nd_id ON facturas_ajustes(factura_nc_nd_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_facturas_ajustes_factura_ajustada_id ON facturas_ajustes(factura_ajustada_id)")

    cur.execute(
        "INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION),
    )
    conn.commit()
    print(f"[migrate_045] OK -- facturas_ajustes creada y {MIGRATION_ID} registrada.")

except Exception as e:
    conn.rollback()
    print(f"[migrate_045] ERROR -- se deshizo todo, la base quedo como estaba: {e}")
    conn.close()
    exit(1)

conn.close()
