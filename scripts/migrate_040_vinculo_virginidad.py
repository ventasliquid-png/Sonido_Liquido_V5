import sqlite3
import os

MIGRATION_ID = "040_vinculo_virginidad"
NRO_SESION = 861

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db"
)

# Dictamen Nike 20260908, enmendado 20260909 v2 (ratificado). Corrige el drift de
# origen: el ORM declaraba default=0 mientras la tabla real tenia DEFAULT 1 -- los
# vinculos nacidos por esa via quedaron con EXISTENCE (Bit 0) apagado. Verificado
# contra datos reales (2026-09-09): ninguno de los vinculos existentes tiene
# historia operativa real (sin FK real que los referencie), son genuinamente
# virgenes -- por eso el patch prende EXISTENCE Y IS_VIRGIN (|3), no solo
# EXISTENCE (|1). Prender solo Bit 0 hubiera marcado registros virgenes como
# "con historia" de forma irreversible (Bit 1 apagado = borrado fisico prohibido
# para siempre), un dano real evitado antes de ejecutar esto.

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

ya_aplicada = cur.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()

if ya_aplicada:
    print(f"[migrate_040] SKIP — {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_040] Iniciando {MIGRATION_ID}...")
    cur.execute(
        "UPDATE vinculos SET flags_estado = flags_estado | 3 WHERE (flags_estado & 1) = 0"
    )
    filas_corregidas = cur.rowcount
    cur.execute(
        "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION),
    )
    conn.commit()
    print(f"[migrate_040] OK — {MIGRATION_ID} aplicada. Vinculos corregidos: {filas_corregidas}")
except sqlite3.OperationalError as e:
    print(f"[migrate_040] ERROR: {e}")
    conn.rollback()
finally:
    conn.close()
