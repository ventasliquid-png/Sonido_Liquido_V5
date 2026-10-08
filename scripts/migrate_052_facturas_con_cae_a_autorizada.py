"""
migrate_052_facturas_con_cae_a_autorizada.py
============================================
Plan de saneamiento, Fase 3 (S882, 08/10/2026; Card #165): la ingesta vieja ("MODO ESPEJO V5.5") guardaba la factura con su CAE real pero en estado
BORRADOR. Un BORRADOR "no es una factura" para el sistema: no cuenta como facturado en los renglones del pedido (backend/pedidos/cantidades.py),
no entra en el informe de facturado, y borrar su remito la borraba tambien (delete_remito).

La migrate_049 ya corrigio de estas facturas el tipo, la fecha y los importes contra el CSV de ARCA, pero no el estado. Esta les cambia SOLO el
estado, de BORRADOR a AUTORIZADA_AFIP -- y solo las que figuran en el archivo de correcciones de la 049 (validadas una por una contra ARCA) y
siguen coincidiendo hoy: mismo numero y CAE, Factura A, mismo total. No toca flags, pedido, cliente, importes, renglones ni remitos.

QUE NO HACE: no toca la 2576 (registrada dos veces, se decide a mano), ninguna factura que no este en el archivo de la 049, ni estados de pedidos
(la regla de estado del pedido es otra decision). Tampoco cambia el codigo de la ingesta vieja.

SEGURIDAD: por factura con SAVEPOINT, tras el backup de auto_migrar, idempotente (una factura ya AUTORIZADA no se vuelve a tocar), sale 0.

MIGRATION_ID = "052_facturas_con_cae_a_autorizada"
NRO_SESION = 882
"""
import json
import os
import sqlite3

MIGRATION_ID = "052_facturas_con_cae_a_autorizada"
NRO_SESION = 882
QUIEN = os.path.dirname(os.path.abspath(__file__))
ARCHIVO = os.path.join(QUIEN, "data", "correcciones_facturas_s881.json")

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(QUIEN, "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_052] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='facturas'").fetchone():
    print("[migrate_052] ERROR -- no existe la tabla 'facturas': no es una base de V5.")
    conn.close()
    raise SystemExit(1)

correcciones = json.load(open(ARCHIVO, encoding="utf-8"))["correcciones"]
pasadas, ya, saltadas, errores = [], 0, [], []
print(f"[migrate_052] Iniciando {MIGRATION_ID}: {len(correcciones)} factura(s) validadas contra ARCA a revisar...")
for c in correcciones:
    num, cae, total_arca = c["numero"], c["cae"], c["despues"]["total"]
    ident = f"{c['pv']:05d}-{num:08d}"
    try:
        cur.execute("SAVEPOINT fac")
        filas = cur.execute("SELECT id, estado, tipo_comprobante, total, notas_auditoria FROM facturas WHERE punto_venta = ? AND numero_comprobante = ? AND cae = ?",
                            (c["pv"], num, cae)).fetchall()
        if not filas:
            saltadas.append((ident, "no esta en la base (o no tiene ese CAE)")); cur.execute("RELEASE fac"); continue
        if len(filas) != 1:
            saltadas.append((ident, f"esta registrada {len(filas)} veces con ese CAE: se decide a mano")); cur.execute("RELEASE fac"); continue
        fid, estado, tipo, total, notas = filas[0]
        if estado == "AUTORIZADA_AFIP":
            ya += 1; cur.execute("RELEASE fac"); continue
        if estado != "BORRADOR":
            saltadas.append((ident, f"esta en estado {estado}, no BORRADOR")); cur.execute("RELEASE fac"); continue
        if tipo != "FACTURA_A" or abs((total or 0.0) - total_arca) > 0.01:
            saltadas.append((ident, f"cambio desde la correccion de la 049 (tipo {tipo}, total {total} vs ARCA {total_arca})")); cur.execute("RELEASE fac"); continue
        marca = "[SISTEMA] Pasada de BORRADOR a AUTORIZADA_AFIP: tiene CAE real y sus datos coinciden con ARCA (S882, migrate_052)."
        cur.execute("UPDATE facturas SET estado = 'AUTORIZADA_AFIP', notas_auditoria = ? WHERE id = ?",
                    ((notas + " | " if notas else "") + marca, fid))
        pasadas.append(ident)
        cur.execute("RELEASE fac")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO fac"); cur.execute("RELEASE fac")
        errores.append((ident, f"{type(e).__name__}: {e}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_052] OK -- pasadas a AUTORIZADA_AFIP {len(pasadas)}, ya estaban {ya}, saltadas {len(saltadas)}, con error {len(errores)}; {MIGRATION_ID} registrada.")
for ident, m in saltadas:
    print(f"[migrate_052] AVISO -- {ident}: {m}")
for ident, m in errores:
    print(f"[migrate_052] ERROR -- {ident}: {m} (esa factura quedo como estaba)")
conn.close()
