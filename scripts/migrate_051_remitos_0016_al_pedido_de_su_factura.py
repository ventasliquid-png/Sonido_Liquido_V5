"""
migrate_051_remitos_0016_al_pedido_de_su_factura.py
===================================================
Plan de saneamiento, Fase 4 (S882, 08/10/2026; Cards #165, #162): los remitos serie 0016 son los que la ingesta vieja numeraba con el numero de la
factura (`0016-0000NNNN`, hasta el 17/09). SON DOCUMENTOS REALES, IMPRESOS Y EN PODER DE CLIENTES (lo dice la propia ingesta): esta migracion NO los
anula, NO los borra y NO cambia numero, estado ni cantidades.

Lo unico que hace: si el remito esta enganchado a un pedido DISTINTO del que hoy tiene su factura (la migrate_050 movio la factura pero no el remito),
lo pasa al pedido de su factura -- y solo si todo cierra: la factura es una sola, el pedido destino existe y es del mismo cliente, cada renglon del
remito tiene su producto en el pedido destino, lo remitido coincide con lo facturado de ese renglon y no hay entrega previa que lo exceda.
Recalcula los Bits 20/21 (entrega parcial / completa) de los pedidos que pierden o ganan la entrega, con la misma regla de RemitosService.

QUE NO HACE: no toca remitos con discrepancia (p.ej. remito 20 vs factura 10), con factura registrada mas de una vez, ni con factura enganchada a un
pedido inexistente: los informa. Tampoco toca estados de pedido, facturas ni remitos 0015.

SEGURIDAD: por remito con SAVEPOINT, tras el backup de auto_migrar, idempotente (un remito ya en el pedido de su factura no se vuelve a tocar), sale 0.

MIGRATION_ID = "051_remitos_0016_al_pedido_de_su_factura"
NRO_SESION = 882
"""
import os
import re
import sqlite3

MIGRATION_ID = "051_remitos_0016_al_pedido_de_su_factura"
NRO_SESION = 882
EPS = 0.001
B_PARCIAL, B_COMPLETA, B_NO_COMERCIAL, B_FACTURADO = 1 << 20, 1 << 21, 1 << 11, 1 << 23

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_051] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("remitos", "remitos_items", "remitos_notas", "facturas", "facturas_items", "pedidos", "pedidos_items"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_051] ERROR -- no existe la tabla '{t}': no es una base de V5.")
        conn.close()
        raise SystemExit(1)


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


movidos, ya, saltados, errores = [], 0, [], []
remitos = cur.execute("SELECT id, pedido_id, numero_legal FROM remitos WHERE numero_legal LIKE '0016%' AND estado != 'ANULADO' ORDER BY numero_legal").fetchall()
print(f"[migrate_051] Iniciando {MIGRATION_ID}: {len(remitos)} remito(s) 0016 a contrastar con su factura...")
for rid, pid, nl in remitos:
    try:
        cur.execute("SAVEPOINT rem")
        n = int(re.sub(r"\D", "", nl)[-8:])
        facs = cur.execute("""SELECT id, CAST(pedido_id AS TEXT), cliente_id FROM facturas WHERE numero_comprobante = ? AND cae IS NOT NULL AND trim(cae) != ''
                              AND estado != 'ANULADA'""", (n,)).fetchall()
        if len(facs) != 1:
            saltados.append((nl, f"la factura {n} esta registrada {len(facs)} veces: se decide a mano")); cur.execute("RELEASE rem"); continue
        fid, fped, fcli = facs[0]
        if fped is not None and str(pid) == fped:
            ya += 1; cur.execute("RELEASE rem"); continue
        if fped is None or not fped.isdigit():
            saltados.append((nl, "la factura no esta enganchada a ningun pedido")); cur.execute("RELEASE rem"); continue
        dest = cur.execute("SELECT id, cliente_id, estado FROM pedidos WHERE id = ?", (int(fped),)).fetchone()
        if dest is None or dest[2] == "ANULADO":
            saltados.append((nl, f"la factura {n} apunta al pedido #{fped}, que no existe o esta anulado")); cur.execute("RELEASE rem"); continue
        if dest[1] != fcli:
            saltados.append((nl, f"el cliente del pedido #{fped} no es el de la factura {n}")); cur.execute("RELEASE rem"); continue
        # renglones: cada uno debe tener su producto en el pedido destino, y lo remitido coincidir con lo facturado de ese renglon
        mapa, motivo = [], None
        for riid, piid, cant in cur.execute("SELECT id, pedido_item_id, cantidad_remitida FROM remitos_items WHERE remito_id = ?", (rid,)).fetchall():
            prod = cur.execute("SELECT producto_id FROM pedidos_items WHERE id = ?", (piid,)).fetchone()
            nuevos = cur.execute("SELECT id, cantidad FROM pedidos_items WHERE pedido_id = ? AND producto_id = ?", (int(fped), prod[0] if prod else -1)).fetchall()
            if len(nuevos) != 1:
                motivo = f"un renglon ({cant:g}) no tiene un unico producto equivalente en el pedido #{fped}"; break
            nid, ncant = nuevos[0]
            facturado = cur.execute("SELECT COALESCE(SUM(cantidad), 0) FROM facturas_items WHERE factura_id = ? AND pedido_item_id = ?", (fid, nid)).fetchone()[0]
            if abs(facturado - cant) > EPS:
                motivo = f"DISCREPANCIA: el remito dice {cant:g} y la factura {n} dice {facturado:g} en ese renglon"; break
            previo = cur.execute("""SELECT COALESCE(SUM(ri.cantidad_remitida), 0) FROM remitos_items ri JOIN remitos r ON r.id = ri.remito_id AND r.estado != 'ANULADO'
                                    WHERE ri.pedido_item_id = ? AND ri.id != ?""", (nid, riid)).fetchone()[0]
            if previo + cant > ncant + EPS:
                motivo = f"el pedido #{fped} quedaria con mas remitido ({previo + cant:g}) que pedido ({ncant:g})"; break
            mapa.append((riid, nid))
        if motivo:
            saltados.append((nl, motivo)); cur.execute("RELEASE rem"); continue
        cur.execute("UPDATE remitos SET pedido_id = ? WHERE id = ?", (int(fped), rid))
        for riid, nid in mapa:
            cur.execute("UPDATE remitos_items SET pedido_item_id = ? WHERE id = ?", (nid, riid))
        cur.execute("INSERT INTO remitos_notas (remito_id, remito_item_id, fecha, autor_id, texto) VALUES (?, NULL, datetime('now'), NULL, ?)",
                    (rid, f"[SISTEMA] Remito pasado del pedido #{pid} al #{fped}: es el pedido de su factura {n} (S882, migrate_051). Numero, estado y cantidades sin cambios."))
        for p_ in {pid, int(fped)}:
            if p_ is not None and cur.execute("SELECT 1 FROM pedidos WHERE id = ?", (p_,)).fetchone():
                recalcular_bits(p_)
        movidos.append((nl, pid, fped))
        cur.execute("RELEASE rem")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO rem"); cur.execute("RELEASE rem")
        errores.append((nl, f"{type(e).__name__}: {e}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_051] OK -- remitos movidos {len(movidos)}, ya estaban en el pedido de su factura {ya}, saltados {len(saltados)}, con error {len(errores)}; {MIGRATION_ID} registrada.")
for nl, a, b in movidos:
    print(f"[migrate_051]   {nl}: pedido #{a} -> #{b}")
for nl, m in saltados:
    print(f"[migrate_051] AVISO -- {nl}: {m}")
for nl, m in errores:
    print(f"[migrate_051] ERROR -- {nl}: {m} (ese remito quedo como estaba)")
conn.close()
