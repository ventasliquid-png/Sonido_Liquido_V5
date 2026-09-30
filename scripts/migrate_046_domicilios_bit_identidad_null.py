"""
migrate_046_domicilios_bit_identidad_null.py
====================================
Prueba funcional S875 sobre la copia de P (30/09/2026): GET /clientes/hub/list daba 500 y la pantalla
Gestion Domicilios no cargaba. Causa: una fila de `domicilios` (Zuviria 5747, CABA) tiene
bit_identidad NULL. El modelo lo declara NOT NULL default 0, pero la columna de la base heredada
se creo sin NOT NULL, y el esquema de respuesta exige un entero.

Criterio de Carlos para datos viejos de P (30/09): completar el hueco con un valor coherente, sin
precision forense. Coherente = el Bit 0 (ACTIVO) sale de la columna is_active, que es la misma regla
que aplica ClienteService al editar un domicilio (sincroniza bit_identidad[0] con is_active). Solo se
tocan las filas con NULL; las que ya tienen un numero (incluidos los 0) quedan como estan.

Un escaneo de todas las columnas NOT NULL del modelo contra la copia de P encontro este como el
unico hueco de toda la base.

MIGRATION_ID = "046_domicilios_bit_identidad_null"
NRO_SESION = 876
"""
import sqlite3
import os

MIGRATION_ID = "046_domicilios_bit_identidad_null"
NRO_SESION = 876

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
    print(f"[migrate_046] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_046] Iniciando {MIGRATION_ID}...")

    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='domicilios'").fetchone():
        raise RuntimeError("No existe la tabla 'domicilios' en esta base: no es una base de V5 o esta desactualizada.")

    antes = cur.execute("SELECT COUNT(*) FROM domicilios WHERE bit_identidad IS NULL").fetchone()[0]
    cur.execute("""
        UPDATE domicilios
           SET bit_identidad = CASE WHEN COALESCE(is_active, activo, 1) THEN 1 ELSE 0 END
         WHERE bit_identidad IS NULL
    """)
    despues = cur.execute("SELECT COUNT(*) FROM domicilios WHERE bit_identidad IS NULL").fetchone()[0]
    if despues:
        raise RuntimeError(f"Quedaron {despues} filas con bit_identidad NULL despues del UPDATE.")

    cur.execute(
        "INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION),
    )
    conn.commit()
    print(f"[migrate_046] OK -- {antes} domicilio(s) con bit_identidad NULL completado(s); {MIGRATION_ID} registrada.")

except Exception as e:
    conn.rollback()
    print(f"[migrate_046] ERROR -- se deshizo todo, la base quedo como estaba: {e}")
    conn.close()
    exit(1)

conn.close()
