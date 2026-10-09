"""
migrate_060_unificar_expreso_demonte.py
=======================================
S883 (09/10/2026), pedido de Carlos: en el padron de transportes de P hay dos fichas del mismo transporte, con el mismo CUIT 30-70965125-7:
  - «Expreso Damonte»       (b26c8617...): inactiva, mal escrita, con el sitio de seguimiento y un telefono (379 5001507, que en el sitio figura como WhatsApp);
  - «EXPRESO DEMONTE SRL»   (db42f9b0...): activa, con WhatsApp y telefono principal (0379 497-8888).
El nombre correcto, segun el sitio de la empresa (expresodemonte.com) es «Expreso Demonte»; la razon social en el padron de ARCA es «TRANSPORTE A DEMONTE SRL» (domicilio legal en Ruta 11 Km 1007,5, Resistencia, Chaco;
sucursal central en Ruta 12 Km 1026, Corrientes).

QUE HACE (una sola ficha activa):
  - la ficha ACTIVA (db42f9b0...) queda como la unica: nombre «Expreso Demonte», con el sitio de seguimiento de la otra, la razon social y el CUIT en observaciones y el otro telefono anotado ahi;
  - todo lo que apuntaba a la ficha duplicada (domicilios, domicilios_legacy, clientes, pedidos, remitos) pasa a apuntar a la unica;
  - la ficha duplicada NO se borra: queda inactiva, con una nota [SISTEMA] que dice en cual se fusiono (se puede deshacer; ademas impide volver a crear «Expreso Damonte» a mano por el control de nombre).
QUE NO HACE: no toca otros transportes ni ningun pedido, remito o cliente mas que cambiar el transporte al que apuntan; no inventa direcciones.

SEGURIDAD: se hace backup antes (auto_migrar), SAVEPOINT, guardas por id + CUIT (si las fichas no son las esperadas no se toca nada), idempotente (marca en observaciones + registro), siempre sale 0.

MIGRATION_ID = "060_unificar_expreso_demonte"
NRO_SESION = 883
"""
import os
import sqlite3

MIGRATION_ID = "060_unificar_expreso_demonte"
NRO_SESION = 883
CUIT = "30709651257"
ID_ACTIVA = "db42f9b049394c16b3ab93e1a3b5f6ae"      # EXPRESO DEMONTE SRL
ID_DUPLICADA = "b26c8617e8734c2c94194e0ee537ba5a"   # Expreso Damonte
NOMBRES_CONOCIDOS = ("EXPRESO DEMONTE SRL", "Expreso Damonte", "Expreso Demonte")
NOMBRE_FINAL = "Expreso Demonte"
MARCA = "migrate_060"
# (tabla, columna) que pueden apuntar a una empresa de transporte
REFERENCIAS = [("domicilios", "transporte_id"), ("domicilios", "intermediario_id"), ("domicilios_legacy", "transporte_id"), ("domicilios_legacy", "intermediario_id"),
               ("clientes", "transporte_habitual_id"), ("pedidos", "transporte_id"), ("remitos", "transporte_id")]

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_060] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='empresas_transporte'").fetchone():
    print("[migrate_060] AVISO -- falta la tabla 'empresas_transporte': no se hace nada y la migracion NO se registra.")
    conn.close()
    raise SystemExit(0)

print(f"[migrate_060] Iniciando {MIGRATION_ID}...")
COLS = [r[1] for r in cur.execute("PRAGMA table_info(empresas_transporte)")]


def ficha(id_):
    r = cur.execute("SELECT * FROM empresas_transporte WHERE id = ?", (id_,)).fetchone()
    return dict(zip(COLS, r)) if r else None


activa, duplicada = ficha(ID_ACTIVA), ficha(ID_DUPLICADA)
motivo = None
if activa is None or duplicada is None:
    motivo = "no estan las dos fichas (esta base no es P o ya se unificaron a mano)"
elif str(activa["cuit"] or "").replace("-", "") != CUIT or str(duplicada["cuit"] or "").replace("-", "") != CUIT:
    motivo = "el CUIT de alguna de las dos fichas no es el esperado"
elif activa["nombre"] not in NOMBRES_CONOCIDOS or duplicada["nombre"] not in NOMBRES_CONOCIDOS:
    motivo = "el nombre de alguna de las dos fichas ya no es el conocido (alguien las edito)"
elif not (int(activa["flags_estado"] or 0) & 2):
    motivo = "la ficha que iba a quedar no esta activa"
elif cur.execute("SELECT 1 FROM empresas_transporte WHERE nombre = ? AND id != ?", (NOMBRE_FINAL, ID_ACTIVA)).fetchone():
    motivo = f"ya existe otra ficha llamada «{NOMBRE_FINAL}»"
elif MARCA in str(activa["observaciones"] or ""):
    motivo = "la ficha ya tiene la marca de la migracion"

if motivo:
    print(f"[migrate_060] AVISO -- no se toca nada: {motivo}.")
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    print(f"[migrate_060] OK -- {MIGRATION_ID} registrada (sin cambios).")
    conn.close()
    raise SystemExit(0)

try:
    cur.execute("SAVEPOINT unif")
    movidas = []
    for tabla, col in REFERENCIAS:
        if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (tabla,)).fetchone():
            continue
        if col not in [r[1] for r in cur.execute(f"PRAGMA table_info('{tabla}')")]:
            continue
        n = cur.execute(f"UPDATE {tabla} SET {col} = ? WHERE {col} = ?", (ID_ACTIVA, ID_DUPLICADA)).rowcount
        if n:
            movidas.append((f"{tabla}.{col}", n))
    notas = [f"Razón social en ARCA: TRANSPORTE A DEMONTE SRL (CUIT 30-70965125-7). Domicilio legal: Ruta 11 Km 1007,5, Resistencia (Chaco); sucursal central: Ruta 12 Km 1026, Corrientes. Sitio: expresodemonte.com."]
    if duplicada["telefono_reclamos"] and duplicada["telefono_reclamos"] != activa["telefono_reclamos"]:
        notas.append(f"Otro teléfono (WhatsApp en el sitio): {duplicada['telefono_reclamos']}.")
    notas.append(f"[SISTEMA] Unificada con la ficha duplicada «{duplicada['nombre']}» ({MARCA}, S{NRO_SESION}).")
    obs = ((activa["observaciones"] + " ") if activa["observaciones"] else "") + " ".join(notas)
    web = activa["web_tracking"] or duplicada["web_tracking"] or None
    cur.execute("UPDATE empresas_transporte SET nombre = ?, web_tracking = ?, observaciones = ? WHERE id = ?", (NOMBRE_FINAL, web, obs, ID_ACTIVA))
    obs_dup = ((duplicada["observaciones"] + " ") if duplicada["observaciones"] else "") + f"[SISTEMA] Duplicada: se unificó en «{NOMBRE_FINAL}» (id {ID_ACTIVA}) por {MARCA}, S{NRO_SESION}. Se deja inactiva, no se borra."
    # inactiva: se apaga el bit 2 (activo) y se conserva el resto de los bits
    cur.execute("UPDATE empresas_transporte SET flags_estado = (COALESCE(flags_estado, 0) & ~2), observaciones = ? WHERE id = ?", (obs_dup, ID_DUPLICADA))
    cur.execute("RELEASE unif")
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    print(f"[migrate_060] OK -- «{duplicada['nombre']}» y «{activa['nombre']}» quedan en una sola ficha activa: «{NOMBRE_FINAL}». Referencias movidas: {movidas or 'ninguna'}. {MIGRATION_ID} registrada.")
except Exception as e:  # noqa: BLE001
    cur.execute("ROLLBACK TO unif"); cur.execute("RELEASE unif")
    print(f"[migrate_060] ERROR -- {type(e).__name__}: {e} (no se cambió nada; no se registra y se reintenta en el próximo arranque)")
conn.close()
