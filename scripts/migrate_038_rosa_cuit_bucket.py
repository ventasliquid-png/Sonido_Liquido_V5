import sqlite3
import os

MIGRATION_ID = "038_rosa_cuit_bucket"
NRO_SESION = 858

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db"
)

# Palabras que identifican al Mostrador/Generico REAL -- nunca se tocan.
# Coincidencia por SUBSTRING, no exacta: el nombre real en produccion es
# "MOSTRADOR / GENERICO" (con separador), una comparacion exacta contra
# "MOSTRADOR" solo NO lo captura -- confirmado en vivo (bug real, ya revertido
# en D antes de escribir esta version). Todo lo demas que comparte
# '00000000000' es un Rosa que quedo mal asignado al CUIT reservado
# (REGLA 1/2 -- Nike 806) y pasa al bucket generico de contingencia AFIP.
PALABRAS_MOSTRADOR = ("MOSTRADOR", "GENERICO", "GENÉRICO", "CONSUMIDOR FINAL")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

ya_aplicada = cur.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()

if ya_aplicada:
    print(f"[migrate_038] SKIP — {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_038] Iniciando {MIGRATION_ID}...")
    cur.execute("SELECT id, razon_social FROM clientes WHERE cuit = '00000000000'")
    candidatos = cur.fetchall()

    migrados = []
    for cid, razon in candidatos:
        nombre = (razon or "").strip().upper()
        if any(palabra in nombre for palabra in PALABRAS_MOSTRADOR):
            continue  # Mostrador/Generico real -- no se toca
        cur.execute("UPDATE clientes SET cuit = '11111111119' WHERE id = ?", (cid,))
        migrados.append((cid, razon))

    cur.execute(
        "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION),
    )
    conn.commit()

    print(f"[migrate_038] OK — {MIGRATION_ID} aplicada. {len(migrados)} clientes Rosa migrados:")
    for cid, razon in migrados:
        print(f"    {cid} | {razon}")
except Exception as e:
    print(f"[migrate_038] ERROR: {e}")
    conn.rollback()
finally:
    conn.close()
