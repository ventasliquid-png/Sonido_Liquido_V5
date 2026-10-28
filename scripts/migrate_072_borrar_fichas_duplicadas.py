"""
migrate_072_borrar_fichas_duplicadas.py
=======================================
S894 (28/10/2026). Carlos: «Si se puede, eliminemos físicamente DAI solo y M&M Insumos solo (1974)». Son dos fichas sueltas, sin pedidos,
facturas ni remitos: «DAI» se dio de alta el 31/07 19:45 y «DAI SALOMÉ» cuatro minutos después (la que tiene los pedidos); «M&M INSUMOS» se
dio de alta el 26/08 con el mismo domicilio que «M&M ODONTOLÓGICOS LA PLATA» (en una copia propia) y nunca se usó. Las dos son VÍRGENES
(ClientFlags.IS_VIRGIN, bit 1: «borrado físico permitido»).

QUÉ HACE: por cada una (por id y nombre exactos), SOLO si sigue virgen y nada más la referencia: borra la ficha y, de M&M Insumos, su
vínculo geográfico, su enlace en domicilios_clientes y su domicilio propio (copia que solo usa ella; el de M&M Odontológicos es otro). Antes
de borrar recorre TODAS las tablas buscando el id: si aparece en cualquier otra parte, no borra y avisa.
QUÉ NO HACE: no toca a DAI SALOMÉ ni a M&M Odontológicos, ni pedidos, ni nada compartido.
SEGURIDAD: corre después del backup de auto_migrar (único lugar donde quedan las dos fichas); SAVEPOINT por ficha; idempotente; sale 0.

MIGRATION_ID = "072_borrar_fichas_duplicadas"
NRO_SESION = 894
"""
import os
import sqlite3

MIGRATION_ID = "072_borrar_fichas_duplicadas"
NRO_SESION = 894
IS_VIRGIN = 1 << 1
FICHAS = (("64bffd58570446019580b1e68b573210", "DAI"), ("3d314dbe40f445adb6f4f55761ca34f3", "M&M INSUMOS"))
# Referencias propias que se borran junto con la ficha (todo lo demás frena el borrado)
PROPIAS = {("clientes", "id"), ("clientes", "cliente_origen_id"), ("vinculos_geograficos", "entidad_id"),
           ("domicilios", "cliente_id"), ("domicilios_clientes", "cliente_id")}

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_072] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)

TABLAS = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall()]


def referencias(valor):
    """(tabla, columna, cantidad) de cada columna de cada tabla que contiene `valor`."""
    hallado = []
    for t in TABLAS:
        for col in [r[1] for r in cur.execute(f"PRAGMA table_info('{t}')").fetchall()]:
            try:
                n = cur.execute(f"SELECT COUNT(*) FROM '{t}' WHERE \"{col}\" = ?", (valor,)).fetchone()[0]
            except sqlite3.Error:
                continue
            if n:
                hallado.append((t, col, n))
    return hallado


print(f"[migrate_072] Iniciando {MIGRATION_ID}: {len(FICHAS)} ficha(s) duplicadas a borrar si siguen vírgenes y sin uso...")
borradas, saltadas, errores = [], [], []
for cid, nombre in FICHAS:
    try:
        cur.execute("SAVEPOINT ficha")
        fila = cur.execute("SELECT razon_social, flags_estado FROM clientes WHERE id = ?", (cid,)).fetchone()
        if fila is None:
            saltadas.append((nombre, "no existe en esta base")); cur.execute("RELEASE ficha"); continue
        if fila[0] != nombre or not int(fila[1] or 0) & IS_VIRGIN:
            saltadas.append((nombre, f"ya no es la ficha auditada (nombre «{fila[0]}», marcas {fila[1]}): no se borra")); cur.execute("RELEASE ficha"); continue
        ajenas = [r for r in referencias(cid) if (r[0], r[1]) not in PROPIAS]
        if ajenas:
            saltadas.append((nombre, f"la referencian {ajenas}: no se borra")); cur.execute("RELEASE ficha"); continue
        # domicilios propios: solo si nada más que esta ficha los usa
        doms = [r[0] for r in cur.execute("SELECT id FROM domicilios WHERE cliente_id = ?", (cid,)).fetchall()]
        doms += [r[0] for r in cur.execute("SELECT domicilio_id FROM vinculos_geograficos WHERE entidad_tipo = 'CLIENTE' AND entidad_id = ?", (cid,)).fetchall()]
        doms = sorted(set(doms))
        compartidos = []
        for d in doms:
            usos = [r for r in referencias(d) if r[:2] != ("domicilios", "id")]
            propios = {("vinculos_geograficos", "domicilio_id"), ("domicilios_clientes", "domicilio_id")}
            if any((t, c) not in propios for t, c, _ in usos) or sum(n for _, _, n in usos) > 2:
                compartidos.append(d)
        if compartidos:
            saltadas.append((nombre, f"su domicilio {compartidos} lo usa otro: no se borra")); cur.execute("RELEASE ficha"); continue
        cur.execute("DELETE FROM vinculos_geograficos WHERE entidad_tipo = 'CLIENTE' AND entidad_id = ?", (cid,))
        cur.execute("DELETE FROM domicilios_clientes WHERE cliente_id = ?", (cid,))
        for d in doms:
            cur.execute("DELETE FROM domicilios WHERE id = ?", (d,))
        cur.execute("DELETE FROM clientes WHERE id = ?", (cid,))
        borradas.append((nombre, len(doms)))
        cur.execute("RELEASE ficha")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO ficha"); cur.execute("RELEASE ficha")
        errores.append((nombre, f"{type(e).__name__}: {e}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_072] OK -- borradas {len(borradas)}, saltadas {len(saltadas)}, con error {len(errores)}; {MIGRATION_ID} registrada.")
for n, k in borradas:
    print(f"[migrate_072]   {n}: borrada" + (f" con {k} domicilio(s) propio(s)" if k else ""))
for n, m in saltadas:
    print(f"[migrate_072] AVISO -- {n}: {m}")
for n, m in errores:
    print(f"[migrate_072] ERROR -- {n}: {m} (esa ficha quedó como estaba)")
conn.close()
