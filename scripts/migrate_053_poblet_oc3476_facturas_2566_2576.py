"""
migrate_053_poblet_oc3476_facturas_2566_2576.py
===============================================
Plan de saneamiento, Fase 2/4 (S882, 08/10/2026; Cards #164, #165): Lacteos de Poblet, OC 3476 (100 bolsas de guantes veterinarios).

QUE PASO (conversacion "Conciliacion Lacteos" del 07/10 + datos de P): la OC 3476 pidio 100 bolsas y se entregaron en dos tandas de 50:
  - 06/07: factura 2566 (50) -- pedido #72, remito 0015-3010 (50).
  - 28/07: factura 2576 (50) -- remito 0016-2576. El 28/07 Tomy imprimio ese remito DOS veces, con 75 segundos de diferencia (PDF de P):
  - 12:46 (registro del pedido #72): 100 bolsas y domicilio de CABA (Vuelta de Obligado, el de la 2577) -- version ERRONEA.
  - 12:47 (registro del pedido #83): 50 bolsas, domicilio de la planta de Poblet y valor declarado $487.500 -- la CORRECTA (coincide con la factura).
La segunda impresion creo ademas un pedido #83 (misma OC 3476, 50 bolsas) y quedaron DOS registros de la factura (FACTURA_B BORRADOR en el #72 y
PRESUPUESTO_X en el #83, los dos por $487.500 sin IVA; la real es Factura A por $589.875). El registro del remito correcto quedo sin renglones.
Resultado en V5: el #72 figura con 150 entregadas sobre 100 pedidas, la 2566 no esta registrada y el #83 duplica 50 bolsas de la OC.

QUE HACE (cada paso con guardas; si el estado de P ya no es el auditado, NO toca nada y avisa)
  1. Corrige el registro de la 2576 del pedido #72 a lo que dice ARCA: Factura A, AUTORIZADA_AFIP, neto 487.500, IVA 102.375, total 589.875, vto 07/08,
     y engancha su renglon al renglon del pedido.
  2. Registra la 2566 (Factura A, $589.875, CAE de ARCA) en el pedido #72, con su renglon enlazado.
  3. Retira el registro duplicado de la 2576 del #83: queda ANULADA con nota (no se borra; se puede revertir).
  4. Remito 0016-2576: conserva el CORRECTO (el de las 12:47, domicilio de Poblet, $487.500): lo pasa al pedido #72 con su renglon de 50 bolsas y
     reengancha a el la factura. Anula el ERRONEO (100 bolsas, domicilio de CABA). Ninguno se borra.
  5. Anula el pedido #83 (duplicado del #72 por la misma OC) con baja logica y nota, igual que hace el sistema.
  6. Recalcula los Bits 20/21 (entrega) del #72 y del #83.
Queda el #72 en 100 pedidas / 100 entregadas (0015-3010 + 0016-2576) / 100 facturadas (2566 + 2576).

QUE NO HACE: no toca el pedido #97 ni el remito 0015-3015 (pendiente de decidir), la 2586 (se anula con una NC que todavia no se emitio), la 2600, ni
estados de pedido (la regla de estado es otra fase). No borra nada.

SEGURIDAD: SAVEPOINT unico (todo o nada), tras el backup de auto_migrar, idempotente (con el registro y por contenido), sale 0.

MIGRATION_ID = "053_poblet_oc3476_facturas_2566_2576"
NRO_SESION = 882
"""
import os
import re
import sqlite3
import uuid

MIGRATION_ID = "053_poblet_oc3476_facturas_2566_2576"
NRO_SESION = 882
EPS = 0.001
B_PARCIAL, B_COMPLETA, B_NO_COMERCIAL, B_FACTURADO = 1 << 20, 1 << 21, 1 << 11, 1 << 23
ES_ANULADO = 1 << 35
STATE_MASK = (1 << 32) | (1 << 33) | (1 << 34) | (1 << 35)

PEDIDO_OK, PEDIDO_DUP = 72, 83
RENGLON_OK, RENGLON_DUP = 127, 146
CUIT = "33660726859"          # LACTEOS DE POBLET SA
OC = "3476"
F2576 = dict(pv=1, numero=2576, cae="86305751282174", fecha="2026-07-28", vto="2026-08-07")
F2566 = dict(pv=1, numero=2566, cae="86272716608690", fecha="2026-07-06", vto="2026-07-16")
NETO, IVA, TOTAL = 487500.0, 102375.0, 589875.0
ITEM = dict(descripcion="GUANTES VETERINARIOS 90 CM BOLSA X 100 UN", cantidad=50.0, precio=9750.0, alicuota=21.0, subtotal=487500.0)

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_053] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("facturas", "facturas_items", "pedidos", "pedidos_items", "remitos", "remitos_items", "remitos_notas", "clientes"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_053] ERROR -- no existe la tabla '{t}': no es una base de V5.")
        conn.close()
        raise SystemExit(1)


def terminar(msg, registrar):
    if registrar:
        cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    print(msg)
    conn.close()
    raise SystemExit(0)


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


print(f"[migrate_053] Iniciando {MIGRATION_ID}: Poblet, OC {OC} -- facturas 2566 y 2576, pedidos #{PEDIDO_OK} y #{PEDIDO_DUP}...")

# ---------------------------------------------------------------- idempotencia por contenido
ya_hecha = cur.execute("""SELECT 1 FROM facturas WHERE numero_comprobante = 2576 AND cae = ? AND tipo_comprobante = 'FACTURA_A' AND estado = 'AUTORIZADA_AFIP'
                          AND CAST(pedido_id AS TEXT) = ?""", (F2576["cae"], str(PEDIDO_OK))).fetchone()
p83 = cur.execute("SELECT estado FROM pedidos WHERE id = ?", (PEDIDO_DUP,)).fetchone()
if ya_hecha and p83 and p83[0] == "ANULADO":
    terminar("[migrate_053] OK -- nada que hacer: el estado ya es el buscado (la correccion se hizo antes); " + MIGRATION_ID + " registrada.", True)

# ---------------------------------------------------------------- guardas: P tiene que estar como se audito
def abortar(motivo):
    terminar(f"[migrate_053] AVISO -- no se toca nada: {motivo}. {MIGRATION_ID} NO se registra (se reintenta en el proximo arranque).", False)


ped72 = cur.execute("SELECT id, cliente_id, oc, estado FROM pedidos WHERE id = ?", (PEDIDO_OK,)).fetchone()
ped83 = cur.execute("SELECT id, cliente_id, oc, estado FROM pedidos WHERE id = ?", (PEDIDO_DUP,)).fetchone()
if ped72 is None or ped83 is None:
    abortar("falta el pedido #72 o el #83")
if ped72[1] != ped83[1] or str(ped72[2]).strip() != OC or str(ped83[2]).strip() != OC or ped72[3] == "ANULADO" or ped83[3] != "PENDIENTE":
    abortar("los pedidos #72 y #83 ya no son los auditados (mismo cliente, OC 3476, #83 pendiente)")
cli = cur.execute("SELECT cuit FROM clientes WHERE id = ?", (ped72[1],)).fetchone()
if cli is None or digitos(cli[0]) != CUIT:
    abortar("el cliente del pedido #72 no es Lacteos de Poblet (CUIT)")
r72 = cur.execute("SELECT id, cantidad FROM pedidos_items WHERE id = ? AND pedido_id = ?", (RENGLON_OK, PEDIDO_OK)).fetchone()
r83 = cur.execute("SELECT id, cantidad FROM pedidos_items WHERE id = ? AND pedido_id = ?", (RENGLON_DUP, PEDIDO_DUP)).fetchone()
if r72 is None or abs(r72[1] - 100) > EPS or r83 is None or abs(r83[1] - 50) > EPS:
    abortar("los renglones ya no son los auditados (#72: 100 bolsas, #83: 50 bolsas)")
if cur.execute("SELECT COUNT(*) FROM pedidos_items WHERE pedido_id IN (?, ?)", (PEDIDO_OK, PEDIDO_DUP)).fetchone()[0] != 2:
    abortar("el #72 o el #83 tienen mas de un renglon")

f_b = cur.execute("""SELECT id, estado, tipo_comprobante FROM facturas WHERE numero_comprobante = 2576 AND punto_venta = 1 AND cae = ? AND CAST(pedido_id AS TEXT) = ?
                     AND tipo_comprobante = 'FACTURA_B'""", (F2576["cae"], str(PEDIDO_OK))).fetchone()
f_x = cur.execute("""SELECT id, estado FROM facturas WHERE numero_comprobante = 2576 AND punto_venta = 1 AND cae = ? AND CAST(pedido_id AS TEXT) = ?
                     AND tipo_comprobante = 'PRESUPUESTO_X'""", (F2576["cae"], str(PEDIDO_DUP))).fetchone()
if f_b is None or f_x is None or f_b[1] != "BORRADOR" or f_x[1] not in ("AUTORIZADA_AFIP", "BORRADOR"):
    abortar("los dos registros de la factura 2576 ya no estan como se auditaron")
# (los presupuestos X sin CAE que el sistema genera como espejo de cada pedido X no son comprobantes: solo cuentan las facturas con CAE)
otras = cur.execute("""SELECT COUNT(*) FROM facturas WHERE CAST(pedido_id AS TEXT) IN (?, ?) AND id NOT IN (?, ?) AND estado != 'ANULADA'
                      AND cae IS NOT NULL AND trim(cae) != ''""", (str(PEDIDO_OK), str(PEDIDO_DUP), f_b[0], f_x[0])).fetchone()[0]
if otras:
    abortar("el #72 o el #83 tienen otras facturas con CAE ademas de la 2576")
if cur.execute("SELECT 1 FROM facturas WHERE numero_comprobante = 2566 AND punto_venta = 1").fetchone():
    abortar("la factura 2566 ya esta registrada")
rems = cur.execute("SELECT id, pedido_id, estado FROM remitos WHERE numero_legal = '0016-00002576' ORDER BY pedido_id").fetchall()
if [(r[1], r[2]) for r in rems] != [(PEDIDO_OK, "BORRADOR"), (PEDIDO_DUP, "BORRADOR")]:
    abortar("los dos remitos 0016-2576 ya no estan como se auditaron")
rem_err, rem_bueno = rems[0][0], rems[1][0]      # el del #72 (100, CABA) y el del #83 (vacio, Poblet, $487.500)
it_err = cur.execute("SELECT id, pedido_item_id, cantidad_remitida FROM remitos_items WHERE remito_id = ?", (rem_err,)).fetchall()
if len(it_err) != 1 or it_err[0][1] != RENGLON_OK or abs(it_err[0][2] - 100) > EPS:
    abortar("el remito 0016-2576 del #72 ya no tiene el renglon de 100 auditado")
if cur.execute("SELECT COUNT(*) FROM remitos_items WHERE remito_id = ?", (rem_bueno,)).fetchone()[0] != 0:
    abortar("el remito 0016-2576 del #83 ya no esta vacio")
dom72 = cur.execute("SELECT domicilio_entrega_id FROM pedidos WHERE id = ?", (PEDIDO_OK,)).fetchone()[0]
dom_b = cur.execute("SELECT domicilio_entrega_id, valor_declarado FROM remitos WHERE id = ?", (rem_bueno,)).fetchone()
dom_e = cur.execute("SELECT domicilio_entrega_id FROM remitos WHERE id = ?", (rem_err,)).fetchone()[0]
if dom_b[0] != dom72 or abs((dom_b[1] or 0) - NETO) > EPS or dom_e == dom72:
    abortar("los domicilios/valor de los dos remitos 0016-2576 ya no son los auditados (el bueno: domicilio del pedido #72 y $487.500; el erroneo: otro domicilio)")
if cur.execute("SELECT 1 FROM remitos WHERE pedido_id = ? AND estado != 'ANULADO' AND id != ?", (PEDIDO_DUP, rem_bueno)).fetchone():
    abortar("el pedido #83 tiene otros remitos vigentes")
links = {r[0]: r[1] for r in cur.execute("SELECT factura_id, remito_id FROM facturas_remitos WHERE factura_id IN (?, ?)", (f_b[0], f_x[0])).fetchall()}
if links != {f_b[0]: rem_err, f_x[0]: rem_bueno}:
    abortar("los vinculos factura-remito de la 2576 ya no son los auditados")
entregado_otros = cur.execute("""SELECT COALESCE(SUM(ri.cantidad_remitida), 0) FROM remitos_items ri JOIN remitos r ON r.id = ri.remito_id AND r.estado != 'ANULADO'
                                 WHERE ri.pedido_item_id = ? AND ri.remito_id NOT IN (?, ?)""", (RENGLON_OK, rem_err, rem_bueno)).fetchone()[0]
if abs(entregado_otros - 50) > EPS:
    abortar(f"las demas entregas del renglon del #72 suman {entregado_otros:g}, no 50 (remito 0015-3010)")

# ---------------------------------------------------------------- todo o nada
cur.execute("SAVEPOINT todo")
try:
    cliente_id = ped72[1]
    marca = " | [SISTEMA] {} (S882, migrate_053)"
    # 1) 2576 del #72 -> Factura A real
    nota_b = cur.execute("SELECT notas_auditoria FROM facturas WHERE id = ?", (f_b[0],)).fetchone()[0] or ""
    cur.execute("""UPDATE facturas SET tipo_comprobante = 'FACTURA_A', estado = 'AUTORIZADA_AFIP', fecha_emision = ?, neto_gravado = ?, iva_21 = ?, iva_105 = 0, exento = 0,
                   total = ?, cae_vencimiento = ?, cuit_comprador = ?, notas_auditoria = ? WHERE id = ?""",
                (F2576["fecha"], NETO, IVA, TOTAL, F2576["vto"], CUIT,
                 nota_b + marca.format("Corregida desde el PDF de ARCA: FACTURA_B BORRADOR -> FACTURA_A AUTORIZADA_AFIP, total 487500 -> 589875; es la factura de la 2da entrega de la OC 3476 (50 bolsas) del pedido #72"), f_b[0]))
    cur.execute("UPDATE facturas_items SET pedido_item_id = ?, alicuota_iva = 21 WHERE factura_id = ?", (RENGLON_OK, f_b[0]))
    # 2) registrar la 2566
    fid = uuid.uuid4().hex
    cur.execute("""INSERT INTO facturas (id, cliente_id, pedido_id, cuit_comprador, tipo_comprobante, punto_venta, numero_comprobante, fecha_emision, estado,
                                         neto_gravado, iva_21, iva_105, exento, percepciones, total, cae, cae_vencimiento, flags_estado, notas_auditoria)
                   VALUES (?, ?, ?, ?, 'FACTURA_A', 1, 2566, ?, 'AUTORIZADA_AFIP', ?, ?, 0, 0, 0, ?, ?, ?, 3, ?)""",
                (fid, cliente_id, str(PEDIDO_OK), CUIT, F2566["fecha"], NETO, IVA, TOTAL, F2566["cae"], F2566["vto"],
                 "[SISTEMA] Registrada desde el PDF de ARCA (S882, migrate_053): 1ra entrega de la OC 3476 (50 bolsas), pedido #72."))
    cur.execute("""INSERT INTO facturas_items (factura_id, pedido_item_id, remito_item_id, descripcion, cantidad, precio_unitario_neto, alicuota_iva, subtotal_neto)
                   VALUES (?, ?, NULL, ?, ?, ?, ?, ?)""", (fid, RENGLON_OK, ITEM["descripcion"], ITEM["cantidad"], ITEM["precio"], ITEM["alicuota"], ITEM["subtotal"]))
    # 3) retirar el registro duplicado del #83
    nota_x = cur.execute("SELECT notas_auditoria FROM facturas WHERE id = ?", (f_x[0],)).fetchone()[0] or ""
    cur.execute("UPDATE facturas SET estado = 'ANULADA', notas_auditoria = ? WHERE id = ?",
                (nota_x + marca.format("Registro DUPLICADO de la factura 2576 retirado: la factura real esta en el pedido #72 (Factura A, $589.875). Queda ANULADA, no se borra"), f_x[0]))
    # 4) remitos
    # el remito correcto (12:47: 50 bolsas, domicilio de Poblet) pasa al #72 con su renglon; el erroneo (12:46: 100 bolsas, domicilio de CABA) se anula
    cur.execute("UPDATE remitos SET pedido_id = ? WHERE id = ?", (PEDIDO_OK, rem_bueno))
    cur.execute("INSERT INTO remitos_items (remito_id, pedido_item_id, cantidad_remitida, cantidad_declarada) VALUES (?, ?, 50, 50)", (rem_bueno, RENGLON_OK))
    cur.execute("INSERT INTO remitos_notas (remito_id, remito_item_id, fecha, autor_id, texto) VALUES (?, NULL, datetime('now'), NULL, ?)",
                (rem_bueno, "[SISTEMA] Remito pasado del pedido #83 (duplicado) al #72 con su renglon de 50 bolsas: es la impresion correcta del 28/07 12:47 (domicilio de Poblet, $487.500, factura 2576). S882, migrate_053."))
    cur.execute("UPDATE remitos SET estado = 'ANULADO' WHERE id = ?", (rem_err,))
    cur.execute("INSERT INTO remitos_notas (remito_id, remito_item_id, fecha, autor_id, texto) VALUES (?, NULL, datetime('now'), NULL, ?)",
                (rem_err, "[SISTEMA] Remito anulado: era la impresion ERRONEA del 28/07 12:46 (100 bolsas, domicilio de CABA); la correcta (50 bolsas, Poblet) se imprimio a las 12:47 y esta en este mismo pedido. No se borra. S882, migrate_053."))
    cur.execute("UPDATE facturas_remitos SET remito_id = ? WHERE factura_id = ?", (rem_bueno, f_b[0]))      # la factura real queda con el remito correcto
    cur.execute("UPDATE facturas_remitos SET remito_id = ? WHERE factura_id = ?", (rem_err, f_x[0]))        # y la anulada con el anulado
    # 5) pedido #83: baja logica, igual que el sistema
    cur.execute("""UPDATE pedidos SET estado = 'ANULADO', flags_estado = (COALESCE(flags_estado, 0) & ?) | ?,
                   nota = COALESCE(nota, '') || ? WHERE id = ?""",
                (~STATE_MASK, ES_ANULADO, "\n[SISTEMA] Anulado por duplicado del pedido #72 (misma OC 3476: 100 bolsas en dos entregas de 50, facturas 2566 y 2576). S882, migrate_053.", PEDIDO_DUP))
    # 6) bits de entrega
    recalcular_bits(PEDIDO_OK)
    recalcular_bits(PEDIDO_DUP)
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    cur.execute("RELEASE todo")
except Exception as e:  # noqa: BLE001
    cur.execute("ROLLBACK TO todo"); cur.execute("RELEASE todo")
    print(f"[migrate_053] ERROR -- {type(e).__name__}: {e} (no se toco nada; se reintenta en el proximo arranque).")
    conn.close()
    raise SystemExit(0)

print(f"[migrate_053] OK -- 2576 corregida a Factura A $589.875 en el pedido #{PEDIDO_OK}; 2566 registrada; duplicados del #{PEDIDO_DUP} retirados (factura, remito, pedido); "
      f"remito 0016-2576 correcto (50 bolsas) en el #72, el erroneo (100) anulado; {MIGRATION_ID} registrada.")
conn.close()
