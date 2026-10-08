"""
migrate_058_remito_2562_jomax_10.py
===================================
Plan de saneamiento, Fase 4 (S882, 08/10/2026; Cards #164, #165): remito 0016-2562 de Jomax Insumos Hospitalarios, enganchado al pedido equivocado y con la cantidad equivocada.

QUE PASO: el 06/07 la ingesta vieja proceso el PDF de la factura 2562 (10 bolsas de guantes veterinarios, pedido #69) y armo el remito espejo 0016-2562 con la cantidad COMPLETA de OTRO pedido
de Jomax, el #4 (20 bolsas, de abril): quedo en el #4 con 20 bolsas, impreso con 20. Es el mismo patron que Poblet (2576) y Cassara: el remito espejo toma la cantidad de un pedido, no la de lo que salio.
Carlos confirmo el 08/10: lo pedido y lo entregado a Jomax fueron 10 bolsas (las de la factura 2562 y el pedido #69). (La factura 2561 quedo anulada por las NC 69 y 70 y la 2591 de
septiembre es otra venta; no se tocan.)

QUE HACE: pasa el remito al pedido #69 y su renglon al renglon de ese pedido, con remitida 10 y declarada 20 (lo que decia el papel impreso); la cantidad recibida queda sin cargar (llego lo que salio).
Deja una nota [SISTEMA] y recalcula los Bits 20/21 del #4 (pierde la entrega) y del #69 (queda completa). El #4 no se toca en nada mas: su estado es otra decision (Fase 3).

SEGURIDAD: SAVEPOINT unico, con guardas (si P ya no esta como se audito no toca nada y avisa; se reintenta); idempotente por contenido; sale 0.

MIGRATION_ID = "058_remito_2562_jomax_10"
NRO_SESION = 882
"""
import os
import re
import sqlite3

MIGRATION_ID = "058_remito_2562_jomax_10"
NRO_SESION = 882
EPS = 0.001
B_PARCIAL, B_COMPLETA, B_NO_COMERCIAL, B_FACTURADO = 1 << 20, 1 << 21, 1 << 11, 1 << 23
CUIT_JOMAX = "30716491494"
NUMERO_LEGAL = "0016-00002562"
PEDIDO_MAL, RENGLON_MAL, PEDIDO_BIEN, RENGLON_BIEN = 4, 6, 69, 122
IMPRESO, ENTREGADO = 20.0, 10.0

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_058] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("remitos", "remitos_items", "remitos_notas", "pedidos", "pedidos_items", "clientes", "facturas", "facturas_items"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_058] ERROR -- no existe la tabla '{t}': no es una base de V5.")
        conn.close()
        raise SystemExit(1)


def terminar(msg, registrar):
    if registrar:
        cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    print(msg)
    conn.close()
    raise SystemExit(0)


def abortar(motivo):
    terminar(f"[migrate_058] AVISO -- no se toca nada: {motivo}. {MIGRATION_ID} NO se registra (se reintenta en el proximo arranque).", False)


def recalcular_bits(pedido_id):
    items = cur.execute("""SELECT pi.id, pi.cantidad, COALESCE((SELECT SUM(ri.cantidad_remitida) FROM remitos_items ri JOIN remitos r ON r.id = ri.remito_id
                                                                 AND r.estado != 'ANULADO' WHERE ri.pedido_item_id = pi.id), 0)
                           FROM pedidos_items pi WHERE pi.pedido_id = ?""", (pedido_id,)).fetchall()
    if not items:
        return
    has_any = any(e > 0 for _, _, e in items)
    is_full = has_any and all(e >= c - EPS for _, c, e in items)
    flags = cur.execute("SELECT COALESCE(flags_estado, 0) FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()[0]
    if is_full:
        flags |= B_COMPLETA
        flags &= ~B_PARCIAL
        if flags & B_NO_COMERCIAL:
            flags |= B_FACTURADO
    else:
        flags &= ~B_COMPLETA
        flags = (flags | B_PARCIAL) if (has_any and not is_full) else (flags & ~B_PARCIAL)
    cur.execute("UPDATE pedidos SET flags_estado = ? WHERE id = ?", (flags, pedido_id))


print(f"[migrate_058] Iniciando {MIGRATION_ID}: remito {NUMERO_LEGAL} (Jomax) del pedido #{PEDIDO_MAL} al #{PEDIDO_BIEN}, con 10 bolsas...")
rem = cur.execute("SELECT id, pedido_id, estado FROM remitos WHERE numero_legal = ?", (NUMERO_LEGAL,)).fetchall()
if len(rem) != 1 or rem[0][2] == "ANULADO":
    abortar(f"no hay un unico remito {NUMERO_LEGAL} vigente")
rid, pedido_actual = rem[0][0], rem[0][1]
if pedido_actual == PEDIDO_BIEN:
    terminar(f"[migrate_058] OK -- nada que hacer: el remito {NUMERO_LEGAL} ya esta en el pedido #{PEDIDO_BIEN}; {MIGRATION_ID} registrada.", True)
if pedido_actual != PEDIDO_MAL:
    abortar(f"el remito {NUMERO_LEGAL} esta en el pedido #{pedido_actual}, no en el #{PEDIDO_MAL} auditado")
items = cur.execute("SELECT id, pedido_item_id, cantidad_remitida, cantidad_declarada, cantidad_recibida FROM remitos_items WHERE remito_id = ?", (rid,)).fetchall()
if len(items) != 1 or items[0][1] != RENGLON_MAL or abs(items[0][2] - IMPRESO) > EPS or items[0][4] is not None:
    abortar(f"el renglon del remito ya no es el auditado ({IMPRESO:g} bolsas en el renglon #{RENGLON_MAL}, sin recibida)")
ri_id = items[0][0]
for pid, cant in ((PEDIDO_MAL, IMPRESO), (PEDIDO_BIEN, ENTREGADO)):
    p = cur.execute("SELECT p.estado, c.cuit FROM pedidos p JOIN clientes c ON c.id = p.cliente_id WHERE p.id = ?", (pid,)).fetchone()
    if p is None or p[0] == "ANULADO" or re.sub(r"\D", "", str(p[1] or "")) != CUIT_JOMAX:
        abortar(f"el pedido #{pid} ya no es el auditado (Jomax, no anulado)")
r_mal = cur.execute("SELECT producto_id, cantidad FROM pedidos_items WHERE id = ? AND pedido_id = ?", (RENGLON_MAL, PEDIDO_MAL)).fetchone()
r_bien = cur.execute("SELECT producto_id, cantidad FROM pedidos_items WHERE id = ? AND pedido_id = ?", (RENGLON_BIEN, PEDIDO_BIEN)).fetchone()
if r_mal is None or r_bien is None or r_mal[0] != r_bien[0] or abs(r_bien[1] - ENTREGADO) > EPS:
    abortar(f"los renglones #{RENGLON_MAL} / #{RENGLON_BIEN} ya no son el mismo producto, o el #{PEDIDO_BIEN} ya no pide {ENTREGADO:g}")
if cur.execute("SELECT 1 FROM remitos r JOIN remitos_items ri ON ri.remito_id = r.id WHERE ri.pedido_item_id = ? AND r.estado != 'ANULADO'", (RENGLON_BIEN,)).fetchone():
    abortar(f"el renglon #{RENGLON_BIEN} del pedido #{PEDIDO_BIEN} ya tiene otro remito")
fac = cur.execute("""SELECT COALESCE(SUM(fi.cantidad), 0) FROM facturas_items fi JOIN facturas f ON f.id = fi.factura_id
                     WHERE f.numero_comprobante = 2562 AND f.cae IS NOT NULL AND trim(f.cae) != '' AND f.estado != 'ANULADA' AND fi.pedido_item_id = ?""", (RENGLON_BIEN,)).fetchone()[0]
if abs(fac - ENTREGADO) > EPS:
    abortar(f"la factura 2562 ya no tiene {ENTREGADO:g} bolsas en el renglon #{RENGLON_BIEN} ({fac:g})")

cur.execute("SAVEPOINT todo")
try:
    cur.execute("UPDATE remitos SET pedido_id = ? WHERE id = ?", (PEDIDO_BIEN, rid))
    cur.execute("UPDATE remitos_items SET pedido_item_id = ?, cantidad_remitida = ? WHERE id = ?", (RENGLON_BIEN, ENTREGADO, ri_id))
    cur.execute("INSERT INTO remitos_notas (remito_id, remito_item_id, fecha, autor_id, texto) VALUES (?, NULL, datetime('now'), NULL, ?)",
                (rid, "[SISTEMA] Remito pasado del pedido #4 al #69 y de 20 a 10 bolsas (S882, migrate_058). La ingesta del 06/07 lo armo con la cantidad completa de otro pedido de Jomax (el #4, 20 bolsas) "
                      "en vez de las 10 de la factura 2562. Carlos confirmo el 08/10: lo pedido y lo entregado fueron 10 bolsas. Declarada 20 (lo que decia el papel impreso), remitida 10."))
    recalcular_bits(PEDIDO_MAL)
    recalcular_bits(PEDIDO_BIEN)
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    cur.execute("RELEASE todo")
except Exception as e:  # noqa: BLE001
    cur.execute("ROLLBACK TO todo"); cur.execute("RELEASE todo")
    print(f"[migrate_058] ERROR -- {type(e).__name__}: {e} (no se toco nada; se reintenta en el proximo arranque).")
    conn.close()
    raise SystemExit(0)
print(f"[migrate_058] OK -- remito {NUMERO_LEGAL} pasado al pedido #{PEDIDO_BIEN} con {ENTREGADO:g} bolsas (declarada {IMPRESO:g}); {MIGRATION_ID} registrada.")
conn.close()
