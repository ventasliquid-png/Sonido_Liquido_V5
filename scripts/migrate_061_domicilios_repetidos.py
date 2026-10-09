"""
migrate_061_domicilios_repetidos.py
===================================
S883 (09/10/2026), pedido de Carlos ("eso no me gusta"): dos clientes de P tienen el MISMO domicilio cargado dos veces (misma calle, numero y localidad):
  - CENTRO PET ARGENTINA S.R.L.: Vieytes 1549, CABA -> dcc42381... (entrega principal) y e1a12cf3... (sin ningun rol);
  - INAPYR S.R.L.: Diagonal 74 N° 80, La Plata    -> 0358b5a6... (fiscal y entrega, lo usa un pedido) y 3d561b71... (solo entrega, no lo usa nadie).
El sobrante sale de la bifurcacion espuria de la Card #158 (un domicilio nuevo de un solo cliente se clonaba al primer guardado; arreglado en backend/clientes/service.py).

QUE HACE: deja inactivo el domicilio SOBRANTE de cada par (activo = 0, is_active = 0) con una nota [SISTEMA] en observaciones que dice cual es el que queda, y desactiva su vinculo geografico si lo tiene.
El sobrante NO se borra (se recupera reactivandolo) y su vinculo con el cliente queda: aparece entre los inactivos de la ficha.
QUE NO HACE: no toca el domicilio que queda, ni otros clientes, ni pedidos o remitos.

GUARDAS (por par; si algo no cierra se informa y ese par queda como estaba): los dos domicilios existen y son del MISMO unico cliente, la direccion normalizada (calle|numero|localidad) coincide, el sobrante no es fiscal ni
predeterminado, ningun pedido ni remito lo usa como domicilio de entrega, el que queda esta activo y el sobrante no tiene la nota de esta migracion (idempotente).

SEGURIDAD: SAVEPOINT por par, despues del backup de auto_migrar, sale siempre 0.

MIGRATION_ID = "061_domicilios_repetidos"
NRO_SESION = 883
"""
import os
import re
import sqlite3

MIGRATION_ID = "061_domicilios_repetidos"
NRO_SESION = 883
MARCA = "migrate_061"
# (nombre para el log, cliente, domicilio que QUEDA, domicilio SOBRANTE)
PARES = [
    ("CENTRO PET ARGENTINA S.R.L. - Vieytes 1549", "069bd7c5be294d88a1df92c856239a7f", "dcc423810a45424e8a29202e85b97349", "e1a12cf398264bf7aeb1c5a7ed3f7458"),
    ("INAPYR S.R.L. - Diagonal 74 N° 80", "65ae103173c04371bdf7f4cd5567598e", "0358b5a6d2ec461caec2c3978930499a", "3d561b71aa15479e914dddfd8fe950d8"),
]

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_061] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("domicilios", "domicilios_clientes", "pedidos", "remitos"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_061] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)


def norm(x):
    return re.sub(r"[^A-Z0-9]+", " ", str(x or "").upper()).strip()


def direccion(dom_id):
    r = cur.execute("SELECT calle, numero, localidad, calle_entrega FROM domicilios WHERE id = ?", (dom_id,)).fetchone()
    return None if r is None else norm(r[0] or r[3]) + "|" + norm(r[1]) + "|" + norm(r[2])


print(f"[migrate_061] Iniciando {MIGRATION_ID}...")
hechos, saltados, errores = [], [], []
for nombre, cli, queda, sobra in PARES:
    try:
        cur.execute("SAVEPOINT par")
        motivo = None
        d_queda = cur.execute("SELECT activo, is_active FROM domicilios WHERE id = ?", (queda,)).fetchone()
        d_sobra = cur.execute("SELECT activo, is_active, es_fiscal, observaciones FROM domicilios WHERE id = ?", (sobra,)).fetchone()
        if d_queda is None or d_sobra is None:
            motivo = "no estan los dos domicilios"
        elif MARCA in str(d_sobra[3] or ""):
            motivo = "ya tiene la marca de la migracion"
        elif not (d_queda[0] and d_queda[1]):
            motivo = "el domicilio que queda no esta activo"
        elif d_sobra[2]:
            motivo = "el sobrante es el fiscal"
        elif direccion(queda) != direccion(sobra) or not direccion(queda).strip("|"):
            motivo = "las direcciones ya no coinciden"
        else:
            for dom in (queda, sobra):
                clientes = [r[0] for r in cur.execute("SELECT cliente_id FROM domicilios_clientes WHERE domicilio_id = ?", (dom,))]
                if clientes != [cli]:
                    motivo = f"el domicilio {dom[:8]} no es solo de este cliente"
                    break
            if motivo is None and cur.execute("SELECT es_predeterminado FROM domicilios_clientes WHERE cliente_id = ? AND domicilio_id = ?", (cli, sobra)).fetchone()[0]:
                motivo = "el sobrante es el predeterminado del cliente"
            if motivo is None:
                usos = cur.execute("SELECT (SELECT count(*) FROM pedidos WHERE domicilio_entrega_id = ?) + (SELECT count(*) FROM remitos WHERE domicilio_entrega_id = ?)", (sobra, sobra)).fetchone()[0]
                if usos:
                    motivo = f"el sobrante lo usan {usos} pedido(s) o remito(s)"
        if motivo:
            saltados.append((nombre, motivo)); cur.execute("RELEASE par"); continue
        nota = f"[SISTEMA] Domicilio repetido: queda {queda[:8]}; este se deja inactivo, no se borra ({MARCA}, S{NRO_SESION}, Card #158)."
        cur.execute("UPDATE domicilios SET activo = 0, is_active = 0, observaciones = CASE WHEN observaciones IS NULL OR trim(observaciones) = '' THEN ? ELSE observaciones || ' ' || ? END WHERE id = ?", (nota, nota, sobra))
        if cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='vinculos_geograficos'").fetchone():
            cur.execute("UPDATE vinculos_geograficos SET activo = 0 WHERE entidad_tipo = 'CLIENTE' AND entidad_id = ? AND domicilio_id = ?", (cli, sobra))
        hechos.append(nombre)
        cur.execute("RELEASE par")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO par"); cur.execute("RELEASE par")
        errores.append((nombre, f"{type(e).__name__}: {e}"))

if errores:
    print("[migrate_061] ERROR -- algun par fallo (ese par quedo como estaba); no se registra y se reintenta en el proximo arranque")
    for n, m in errores:
        print(f"[migrate_061]   {n}: {m}")
else:
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    print(f"[migrate_061] OK -- sobrantes dejados inactivos: {len(hechos)}; sin tocar: {len(saltados)}; {MIGRATION_ID} registrada.")
    for n in hechos:
        print(f"[migrate_061]   {n}: sobrante inactivo")
    for n, m in saltados:
        print(f"[migrate_061] AVISO -- {n}: {m} (queda como estaba)")
conn.close()
