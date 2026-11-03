"""
migrate_077_cf_sin_cuit_comodin.py
==================================
H21 (S898, 03/11/2026; decision de Carlos: «H21, solo mascara»). Regla de oro de Nike del 28/10: el CUIT comodin del Consumidor Final (11111111119) vive SOLO en el comprobante, nunca en
la ficha. La ficha de la S897 lo guardaba (se tipeaba o se apretaba el boton y quedaba escrito en la ficha); desde ahora el 11111111119 es solo una mascara de la pantalla: la ficha de un
Consumidor Final guarda el CUIT VACIO y la condicion de IVA «Consumidor Final».

QUE HACE: a los clientes con el CUIT 11111111119 guardado Y la condicion de IVA «Consumidor Final» (hoy en P: M&M Odontologicos La Plata y Elizabeth Paola Roca) les deja el CUIT vacio (NULL,
como los demas clientes sin CUIT). Nada mas: ni los bits (siguen Blanco), ni la condicion de IVA, ni los pedidos ni los remitos.
QUE NO HACE: no toca el 00000000000 (el CUIT del Mostrador/Generico, que si se guarda), ni el 11111111111 (reservado Rosa), ni un 11111111119 con otra condicion de IVA.

SEGURIDAD: SAVEPOINT, despues del backup de auto_migrar; idempotente (registro en _migraciones_aplicadas y el criterio de estado); sale 0.

MIGRATION_ID = "077_cf_sin_cuit_comodin"
NRO_SESION = 898
"""
import os
import sqlite3

MIGRATION_ID = "077_cf_sin_cuit_comodin"
NRO_SESION = 898
COMODIN = "11111111119"

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_077] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("clientes", "condiciones_iva"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_077] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)

print(f"[migrate_077] Iniciando {MIGRATION_ID}...")
resultado = "saltado"
try:
    cur.execute("SAVEPOINT cf")
    filas = cur.execute("""SELECT c.id, c.razon_social FROM clientes c JOIN condiciones_iva i ON i.id = c.condicion_iva_id
                           WHERE REPLACE(REPLACE(COALESCE(c.cuit, ''), '-', ''), ' ', '') = ? AND UPPER(i.nombre) LIKE '%CONSUMIDOR FINAL%'
                           ORDER BY c.razon_social""", (COMODIN,)).fetchall()
    if not filas:
        resultado = "ya estaba"
        print("[migrate_077] Ningun Consumidor Final con el 11111111119 guardado: nada que hacer.")
    else:
        for cid, razon in filas:
            cur.execute("UPDATE clientes SET cuit = NULL WHERE id = ?", (cid,))
            print(f"[migrate_077] OK -- {razon}: CUIT 11111111119 -> vacio (sigue Consumidor Final y Blanco).")
        resultado = f"{len(filas)} ficha(s)"
    cur.execute("RELEASE cf")
except Exception as e:  # noqa: BLE001
    cur.execute("ROLLBACK TO cf"); cur.execute("RELEASE cf")
    print(f"[migrate_077] ERROR -- {type(e).__name__}: {e} (las fichas quedaron como estaban)")

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_077] {MIGRATION_ID} registrada ({resultado}).")
conn.close()
