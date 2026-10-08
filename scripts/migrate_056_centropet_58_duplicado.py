"""
migrate_056_centropet_58_duplicado.py
=====================================
Plan de saneamiento, Fase 4 (S882, 08/10/2026; Cards #164, #165): un duplicado que dejo la ingesta vieja.

PARTE C -- Centro Pet: el pedido #58 (12/06, 240 Surgizime, sin bonificacion) lo creo la INGESTA al procesar el PDF de la factura 2549, 0,08 s antes de
  su remito y su registro de factura. El pedido real es el #53 (08/06, 5 % de bonificacion). Se anula el #58 -- cuando la migrate_051 ya le saco el
  remito 0016-2549 (si todavia lo tiene, no se toca y se reintenta en el proximo arranque).

QUE NO HACE: no toca facturas ni otros pedidos, no borra nada.

SEGURIDAD: SAVEPOINT por parte; cada parte con guardas (si P ya no esta como se audito, no toca nada y avisa); idempotente por contenido; sale 0. Si una parte
queda pendiente la migracion NO se registra y se reintenta en el proximo arranque.

MIGRATION_ID = "056_centropet_58_duplicado"
NRO_SESION = 882
"""
import os
import re
import sqlite3

MIGRATION_ID = "056_centropet_58_duplicado"
NRO_SESION = 882
EPS = 0.001
B_PARCIAL, B_COMPLETA, B_NO_COMERCIAL, B_FACTURADO = 1 << 20, 1 << 21, 1 << 11, 1 << 23
ES_ANULADO = 1 << 35
STATE_MASK = (1 << 32) | (1 << 33) | (1 << 34) | (1 << 35)
CUIT_POBLET, CUIT_CENTROPET = "33660726859", "30715138707"

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_056] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("facturas", "facturas_items", "pedidos", "pedidos_items", "remitos", "remitos_items", "remitos_notas", "clientes"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_056] ERROR -- no existe la tabla '{t}': no es una base de V5.")
        conn.close()
        raise SystemExit(1)


def digitos(x):
    return re.sub(r"\D", "", str(x or ""))


def recalcular_bits(pedido_id):
    """Misma regla que RemitosService._recalcular_bits_entrega: OFF/OFF sin entrega, bit 20 parcial, bit 21 completa."""
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


def anular_pedido(pedido_id, nota):
    cur.execute("""UPDATE pedidos SET estado = 'ANULADO', flags_estado = (COALESCE(flags_estado, 0) & ?) | ?, nota = COALESCE(nota, '') || ? WHERE id = ?""",
                (~STATE_MASK, ES_ANULADO, "\n[SISTEMA] " + nota, pedido_id))


def nota_remito(remito_id, texto):
    cur.execute("INSERT INTO remitos_notas (remito_id, remito_item_id, fecha, autor_id, texto) VALUES (?, NULL, datetime('now'), NULL, ?)", (remito_id, "[SISTEMA] " + texto))


def cliente_cuit(pedido_id):
    r = cur.execute("SELECT c.cuit FROM pedidos p JOIN clientes c ON c.id = p.cliente_id WHERE p.id = ?", (pedido_id,)).fetchone()
    return digitos(r[0]) if r else None


resultados = []   # (parte, 'hecho'|'ya'|'pendiente', detalle)


def parte(nombre):
    def deco(fn):
        try:
            cur.execute("SAVEPOINT parte")
            estado, detalle = fn()
            cur.execute("RELEASE parte")
        except Exception as e:  # noqa: BLE001
            cur.execute("ROLLBACK TO parte"); cur.execute("RELEASE parte")
            estado, detalle = "pendiente", f"ERROR {type(e).__name__}: {e}"
        resultados.append((nombre, estado, detalle))
        return fn
    return deco


print(f"[migrate_056] Iniciando {MIGRATION_ID}: Centro Pet #58...")


@parte("A: pedido #97 y remito 0015-3015 (Poblet)")
def parte_a():
    p97 = cur.execute("SELECT estado, oc FROM pedidos WHERE id = 97").fetchone()
    if p97 is None:
        return "pendiente", "no existe el pedido #97"
    if p97[0] == "ANULADO":
        return "ya", "el #97 ya esta anulado"
    p82 = cur.execute("SELECT oc, estado, cliente_id FROM pedidos WHERE id = 82").fetchone()
    if cliente_cuit(97) != CUIT_POBLET or str(p97[1]).strip() != "3502" or p97[0] != "PENDIENTE" or p82 is None or str(p82[0]).strip() != "3502" or p82[1] == "ANULADO":
        return "pendiente", "el #97 / #82 ya no son los auditados (Poblet, OC 3502, #97 pendiente, #82 vigente)"
    it97 = cur.execute("SELECT id, cantidad FROM pedidos_items WHERE pedido_id = 97").fetchall()
    if len(it97) != 1 or abs(it97[0][1] - 100) > EPS:
        return "pendiente", "el #97 ya no tiene un unico renglon de 100 bolsas"
    if cur.execute("SELECT 1 FROM facturas WHERE CAST(pedido_id AS TEXT) = '97' AND cae IS NOT NULL AND trim(cae) != ''").fetchone():
        return "pendiente", "el #97 tiene facturas con CAE"
    rems = cur.execute("SELECT id, numero_legal, estado FROM remitos WHERE pedido_id = 97 AND estado != 'ANULADO'").fetchall()
    if [(r[1], r[2]) for r in rems] != [("0015-00003015", "BORRADOR")]:
        return "pendiente", f"los remitos vigentes del #97 ya no son solo el 0015-3015 en BORRADOR ({[r[1] for r in rems]})"
    rid = rems[0][0]
    if [(r[0], r[1]) for r in cur.execute("SELECT pedido_item_id, cantidad_remitida FROM remitos_items WHERE remito_id = ?", (rid,)).fetchall()] != [(it97[0][0], 100.0)]:
        return "pendiente", "el renglon del remito 0015-3015 ya no es el auditado (100 bolsas)"
    cur.execute("UPDATE remitos SET estado = 'ANULADO' WHERE id = ?", (rid,))
    nota_remito(rid, "Remito anulado: el papel con el numero 0015-3015 fue a Laboratorio de Medicina (impreso desde OF, 03/09); esta impresion del 14/08 para Poblet (100 bolsas) no fue una entrega. "
                     "Confirmado por Carlos el 08/10. S882, migrate_054.")
    anular_pedido(97, "Anulado por duplicado: la OC 3502 pide 200 bolsas y el pedido #82 ya las cubre (100 facturadas con la 2577 + 100 por entregar). Su remito 0015-3015 no fue una entrega. S882, migrate_054.")
    recalcular_bits(97)
    return "hecho", "#97 y su remito 0015-3015 anulados"


@parte("B: renglones del remito 0016-2577 (pedido #82)")
def parte_b():
    r = cur.execute("SELECT id, estado FROM remitos WHERE numero_legal = '0016-00002577' AND pedido_id = 82").fetchall()
    if len(r) != 1 or r[0][1] == "ANULADO":
        return "pendiente", "no hay un unico remito 0016-2577 vigente en el pedido #82"
    rid = r[0][0]
    if cur.execute("SELECT COUNT(*) FROM remitos_items WHERE remito_id = ?", (rid,)).fetchone()[0] > 0:
        return "ya", "el remito 0016-2577 ya tiene renglones"
    if cliente_cuit(82) != CUIT_POBLET:
        return "pendiente", "el pedido #82 ya no es de Poblet"
    facs = cur.execute("SELECT id FROM facturas WHERE numero_comprobante = 2577 AND cae IS NOT NULL AND trim(cae) != '' AND estado != 'ANULADA'").fetchall()
    if len(facs) != 1:
        return "pendiente", f"la factura 2577 esta registrada {len(facs)} veces"
    lineas = cur.execute("""SELECT fi.pedido_item_id, fi.cantidad, pi.cantidad FROM facturas_items fi LEFT JOIN pedidos_items pi ON pi.id = fi.pedido_item_id AND pi.pedido_id = 82
                            WHERE fi.factura_id = ? ORDER BY fi.pedido_item_id""", (facs[0][0],)).fetchall()
    # lo que dice el remito impreso (PDF de P): 100 veterinarios + 80 nitrilo L + 40 nitrilo M = lo que facturo la 2577
    if sorted(l[1] for l in lineas) != [40.0, 80.0, 100.0] or any(l[0] is None or l[2] is None or l[1] > l[2] + EPS for l in lineas):
        return "pendiente", "los renglones de la factura 2577 ya no son 100/80/40 enlazados al #82"
    for pid_item, cant, _ in lineas:
        cur.execute("INSERT INTO remitos_items (remito_id, pedido_item_id, cantidad_remitida, cantidad_declarada) VALUES (?, ?, ?, ?)", (rid, pid_item, cant, cant))
    nota_remito(rid, "Renglones cargados desde el remito impreso (100 bolsas veterinarias, 80 nitrilo L, 40 nitrilo M = la factura 2577): el registro estaba vacio y el pedido #82 figuraba con 0 entregado. S882, migrate_054.")
    recalcular_bits(82)
    return "hecho", "renglones 100/80/40 cargados en el 0016-2577"


@parte("C: pedido #58 (Centro Pet), duplicado del #53")
def parte_c():
    p58 = cur.execute("SELECT estado, oc FROM pedidos WHERE id = 58").fetchone()
    if p58 is None:
        return "pendiente", "no existe el pedido #58"
    if p58[0] == "ANULADO":
        return "ya", "el #58 ya esta anulado"
    p53 = cur.execute("SELECT estado FROM pedidos WHERE id = 53").fetchone()
    if cliente_cuit(58) != CUIT_CENTROPET or cliente_cuit(53) != CUIT_CENTROPET or p58[0] != "PENDIENTE" or p53 is None or p53[0] == "ANULADO":
        return "pendiente", "el #58 / #53 ya no son los auditados (Centro Pet, #58 pendiente, #53 vigente)"
    it58 = cur.execute("SELECT cantidad FROM pedidos_items WHERE pedido_id = 58").fetchall()
    it53 = cur.execute("SELECT cantidad FROM pedidos_items WHERE pedido_id = 53").fetchall()
    if [x[0] for x in it58] != [240.0] or [x[0] for x in it53] != [240.0]:
        return "pendiente", "los renglones del #58 / #53 ya no son 240 / 240"
    if cur.execute("SELECT 1 FROM facturas WHERE CAST(pedido_id AS TEXT) = '58' AND cae IS NOT NULL AND trim(cae) != '' AND estado != 'ANULADA'").fetchone():
        return "pendiente", "el #58 tiene facturas con CAE"
    if not cur.execute("SELECT 1 FROM facturas WHERE numero_comprobante = 2549 AND CAST(pedido_id AS TEXT) = '53' AND cae IS NOT NULL").fetchone():
        return "pendiente", "la factura 2549 todavia no esta en el pedido #53"
    rem = cur.execute("SELECT numero_legal FROM remitos WHERE pedido_id = 58 AND estado != 'ANULADO'").fetchall()
    if rem:
        return "pendiente", f"el #58 todavia tiene remitos vigentes ({[r[0] for r in rem]}): corre despues de la migrate_051"
    anular_pedido(58, "Anulado por duplicado del pedido #53 (Centro Pet, 5 % de bonificacion): lo creo la ingesta del PDF de la factura 2549 el 12/06. Las NC 67 y 68 anularon la 2548; la 2549 es la valida. S882, migrate_056.")
    recalcular_bits(58)
    return "hecho", "#58 anulado"


pendientes = [r for r in resultados if r[1] == "pendiente"]
if not pendientes:
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
for nombre, estado, detalle in resultados:
    print(f"[migrate_056]   {nombre}: {estado.upper()} -- {detalle}")
if pendientes:
    print(f"[migrate_056] AVISO -- {len(pendientes)} parte(s) pendiente(s): {MIGRATION_ID} NO se registra (se reintenta en el proximo arranque; lo hecho no se repite).")
else:
    print(f"[migrate_056] OK -- hechas {sum(1 for r in resultados if r[1] == 'hecho')}, ya estaban {sum(1 for r in resultados if r[1] == 'ya')}; {MIGRATION_ID} registrada.")
conn.close()
