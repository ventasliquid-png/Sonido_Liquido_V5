import sqlite3
import os
import uuid

MIGRATION_ID = "044_condicion_iva_cliente_interno"
NRO_SESION = 875

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db"
)

# [S875, traspaso AG punto A / DISENO_MODULO_INFORMES_S875_2026-09-26.md] Condicion de IVA
# nueva, dedicada, para forzar Rosa sin depender de CUIT -- ver clientes/service.py
# _audit_sovereignty, chequeo "CLIENTE INTERNO". Solo master data (una fila en
# condiciones_iva), no toca esquema.

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

ya_aplicada = cur.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()

if ya_aplicada:
    print(f"[migrate_044] SKIP — {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_044] Iniciando {MIGRATION_ID}...")
    existente = cur.execute(
        "SELECT id FROM condiciones_iva WHERE UPPER(nombre) = 'CLIENTE INTERNO'"
    ).fetchone()
    if existente:
        print(f"[migrate_044] 'Cliente Interno' ya existe (id={existente[0]}), no se duplica.")
    else:
        nuevo_id = uuid.uuid4().hex
        cur.execute(
            "INSERT INTO condiciones_iva (id, nombre) VALUES (?, ?)",
            (nuevo_id, "Cliente Interno"),
        )
        print(f"[migrate_044] Insertada 'Cliente Interno' (id={nuevo_id}).")
    cur.execute(
        "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION),
    )
    conn.commit()
    print(f"[migrate_044] OK — {MIGRATION_ID} aplicada.")
except sqlite3.OperationalError as e:
    print(f"[migrate_044] ERROR: {e}")
    conn.rollback()
finally:
    conn.close()
