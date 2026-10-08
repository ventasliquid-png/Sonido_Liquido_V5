"""
migrate_057_remito_2597_cassara_1480.py
=======================================
Plan de saneamiento, Fase 4 (S882, 08/10/2026; Cards #164, #165): remito 0016-2597 del pedido #109 (Laboratorio Pablo Cassara, OC 19211) cargado SIN renglones.

QUE PASO (relato de Carlos 08/10 + mails con Sergio Machuca, "Entrega OC 19211"): la OC pedia 1.500 bolsas (anticipo 50 %; se facturo el 37 %, factura 2570). Tomy
armo el remito por lo que decia la OC (1.500) ANTES de que existiera la factura; habia que esperar a terminar el faconeo para saber cuantas salian. Salieron 1.480 (dentro de
la tolerancia de ingreso). Carlos llevo el remito sin notar que decia 1.500 y quien recibio tacho y escribio 1.480. La factura 2597 se emitio despues por la OC completa
(1.500); se corrigio con la NC 72 (20 bolsas a $1.435) y la NC 73 (aplica el adelanto de la 2570, solo importe). El pedido #109 quedo en 1.480.

QUE HACE: carga el unico renglon del remito 0016-2597 con las TRES cantidades que el modelo separa justamente para esto: declarada 1.500 (lo que decia el papel impreso), remitida 1.480
(lo que salio) y recibida 1.480 (lo que confirmo el receptor, a mano). Deja una nota [SISTEMA] con el relato y recalcula los Bits 20/21 del #109. Con la migrate_055 (NC 72 y 73) el
renglon queda 1.480 pedidas / 1.480 entregadas / 1.480 facturadas netas: OC cerrada con menos de lo que decia, sin tocar la cantidad del pedido.

SEGURIDAD: SAVEPOINT unico, con guardas (si P ya no esta como se audito, no toca nada y avisa; se reintenta en el proximo arranque); idempotente; sale 0.

MIGRATION_ID = "057_remito_2597_cassara_1480"
NRO_SESION = 882
"""
import os
import re
import sqlite3

MIGRATION_ID = "057_remito_2597_cassara_1480"
NRO_SESION = 882
EPS = 0.001
B_PARCIAL, B_COMPLETA, B_NO_COMERCIAL, B_FACTURADO = 1 << 20, 1 << 21, 1 << 11, 1 << 23
CUIT_CASSARA, OC = "30525858274", "19211"
PEDIDO, RENGLON, NUMERO_LEGAL = 109, 215, "0016-00002597"
IMPRESO, ENTREGADO = 1500.0, 1480.0

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_057] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("remitos", "remitos_items", "remitos_notas", "pedidos", "pedidos_items", "clientes"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_057] ERROR -- no existe la tabla '{t}': no es una base de V5.")
        conn.close()
        raise SystemExit(1)


def terminar(msg, registrar):
    if registrar:
        cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    print(msg)
    conn.close()
    raise SystemExit(0)


def abortar(motivo):
    terminar(f"[migrate_057] AVISO -- no se toca nada: {motivo}. {MIGRATION_ID} NO se registra (se reintenta en el proximo arranque).", False)


print(f"[migrate_057] Iniciando {MIGRATION_ID}: remito {NUMERO_LEGAL} del pedido #{PEDIDO} (OC {OC})...")
rem = cur.execute("SELECT id, estado FROM remitos WHERE numero_legal = ? AND pedido_id = ?", (NUMERO_LEGAL, PEDIDO)).fetchall()
if len(rem) != 1 or rem[0][1] == "ANULADO":
    abortar(f"no hay un unico remito {NUMERO_LEGAL} vigente en el pedido #{PEDIDO}")
rid = rem[0][0]
if cur.execute("SELECT COUNT(*) FROM remitos_items WHERE remito_id = ?", (rid,)).fetchone()[0] > 0:
    terminar(f"[migrate_057] OK -- nada que hacer: el remito {NUMERO_LEGAL} ya tiene renglones; {MIGRATION_ID} registrada.", True)
ped = cur.execute("SELECT p.estado, p.oc, c.cuit FROM pedidos p JOIN clientes c ON c.id = p.cliente_id WHERE p.id = ?", (PEDIDO,)).fetchone()
if ped is None or ped[0] == "ANULADO" or str(ped[1]).strip() != OC or re.sub(r"\D", "", str(ped[2] or "")) != CUIT_CASSARA:
    abortar(f"el pedido #{PEDIDO} ya no es el auditado (Cassara, OC {OC}, no anulado)")
it = cur.execute("SELECT cantidad FROM pedidos_items WHERE id = ? AND pedido_id = ?", (RENGLON, PEDIDO)).fetchone()
if it is None or abs(it[0] - ENTREGADO) > EPS or cur.execute("SELECT COUNT(*) FROM pedidos_items WHERE pedido_id = ?", (PEDIDO,)).fetchone()[0] != 1:
    abortar(f"el pedido #{PEDIDO} ya no tiene un unico renglon de {ENTREGADO:g} bolsas")
previas = cur.execute("""SELECT COALESCE(SUM(ri.cantidad_remitida), 0) FROM remitos_items ri JOIN remitos r ON r.id = ri.remito_id AND r.estado != 'ANULADO'
                         WHERE ri.pedido_item_id = ?""", (RENGLON,)).fetchone()[0]
if previas > EPS:
    abortar(f"el renglon ya tiene {previas:g} bolsas remitidas en otros remitos")
fac = cur.execute("""SELECT COALESCE(SUM(fi.cantidad), 0) FROM facturas_items fi JOIN facturas f ON f.id = fi.factura_id
                     WHERE f.numero_comprobante = 2597 AND f.cae IS NOT NULL AND trim(f.cae) != '' AND f.estado != 'ANULADA' AND fi.pedido_item_id = ?""", (RENGLON,)).fetchone()[0]
if abs(fac - IMPRESO) > EPS:
    abortar(f"la factura 2597 ya no tiene {IMPRESO:g} bolsas en ese renglon ({fac:g})")

cur.execute("SAVEPOINT todo")
try:
    cur.execute("INSERT INTO remitos_items (remito_id, pedido_item_id, cantidad_remitida, cantidad_declarada, cantidad_recibida) VALUES (?, ?, ?, ?, ?)",
                (rid, RENGLON, ENTREGADO, IMPRESO, ENTREGADO))
    cur.execute("INSERT INTO remitos_notas (remito_id, remito_item_id, fecha, autor_id, texto) VALUES (?, NULL, datetime('now'), NULL, ?)",
                (rid, "[SISTEMA] Renglon cargado (S882, migrate_057). El remito se imprimio con 1.500 bolsas, como decia la OC 19211, antes de que existiera la factura; "
                      "salieron 1.480 y quien recibio tacho y escribio 1.480 (confirmado por Carlos el 08/10; mails con Sergio Machuca). Declarada 1.500, remitida 1.480, recibida 1.480. "
                      "La factura 2597 salio por 1.500: la corrige la NC 72 (20 bolsas) y la NC 73 aplica el adelanto de la factura 2570."))
    items = cur.execute("""SELECT pi.cantidad, COALESCE((SELECT SUM(ri.cantidad_remitida) FROM remitos_items ri JOIN remitos r ON r.id = ri.remito_id AND r.estado != 'ANULADO'
                                                          WHERE ri.pedido_item_id = pi.id), 0) FROM pedidos_items pi WHERE pi.pedido_id = ?""", (PEDIDO,)).fetchall()
    flags = cur.execute("SELECT COALESCE(flags_estado, 0) FROM pedidos WHERE id = ?", (PEDIDO,)).fetchone()[0]
    if all(e >= c - EPS for c, e in items):
        flags = (flags | B_COMPLETA) & ~B_PARCIAL
        if flags & B_NO_COMERCIAL:
            flags |= B_FACTURADO
    cur.execute("UPDATE pedidos SET flags_estado = ? WHERE id = ?", (flags, PEDIDO))
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    cur.execute("RELEASE todo")
except Exception as e:  # noqa: BLE001
    cur.execute("ROLLBACK TO todo"); cur.execute("RELEASE todo")
    print(f"[migrate_057] ERROR -- {type(e).__name__}: {e} (no se toco nada; se reintenta en el proximo arranque).")
    conn.close()
    raise SystemExit(0)
print(f"[migrate_057] OK -- remito {NUMERO_LEGAL} cargado: declarada {IMPRESO:g}, remitida {ENTREGADO:g}, recibida {ENTREGADO:g}; {MIGRATION_ID} registrada.")
conn.close()
