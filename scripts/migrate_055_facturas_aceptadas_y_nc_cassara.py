"""
migrate_055_facturas_aceptadas_y_nc_cassara.py
==============================================
Plan de saneamiento, Fase 2 (S882, 08/10/2026; Cards #164, #165): registra en V5 las facturas emitidas que Carlos acepto asignar a su pedido (2500 -> #29,
2529 -> #31, 2582 -> #94, 2607 -> #117) y las dos notas de credito que corrigen una factura que V5 SI tiene: la 2597 (Laboratorio Pablo Cassara, pedido #109).

Los datos salen de los PDF de ARCA contrastados con el CSV oficial (total, neto y fecha de cada comprobante) y viajan en `scripts/data/registro_facturas_nc_s882.json`.

FACTURAS: estado AUTORIZADA_AFIP, tipo y totales del PDF, CAE y vencimiento, ligadas al pedido, con sus renglones enlazados a los renglones del pedido.
  - 2529 y 2607 son facturas PARCIALES (el pedido tiene un renglon mas: la cofia, el envio): cada renglon facturado se enlaza al suyo.
  - 2582 lleva 5 % de bonificacion: un renglon con el precio neto ya bonificado, de modo que el total cierra con el de ARCA.
NOTAS DE CREDITO (NOTA_CREDITO_A, vinculo en facturas_ajustes como lo hace la conciliacion de la Etapa 7d, y bit TIENE_NC en la factura ajustada):
  - NC 72 ($34.727): «Diferencia entrega de mercaderia (20 bolsas a $1.435 c/u)»: lleva 20 bolsas enlazadas al renglon del pedido #109 -> el facturado neto pasa
    de 1.500 a 1.480, que es lo pedido y lo entregado.
  - NC 73 ($968.000): «Adelanto segun F 2570 del 17/07/2026»: solo importe, sin cantidades.
QUE NO HACE: no registra facturas anuladas (2495, 2548, 2561, ni la 2590) ni sus NC, no toca estados de pedidos, ni remitos, ni borra nada.

SEGURIDAD (por documento, con SAVEPOINT): idempotente (no crea si ya existe el numero), verifica que el pedido exista, no este anulado, que el CUIT del cliente sea el
del comprobante y que el pedido no quede cubierto de mas; la NC solo se registra si la factura ajustada esta en V5 con ese CAE y el renglon admite lo acreditado.

MIGRATION_ID = "055_facturas_aceptadas_y_nc_cassara"
NRO_SESION = 882
"""
import json
import os
import re
import sqlite3
import uuid

MIGRATION_ID = "055_facturas_aceptadas_y_nc_cassara"
NRO_SESION = 882
EPS = 0.001
ES_NC, TIENE_NC = 1 << 19, 1 << 17

AQUI = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(AQUI, "..", "pilot_v5x.db")
JSON_PATH = os.path.join(AQUI, "data", "registro_facturas_nc_s882.json")

conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_055] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("facturas", "facturas_items", "pedidos", "pedidos_items", "clientes", "facturas_ajustes"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_055] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)
if not os.path.exists(JSON_PATH):
    print(f"[migrate_055] AVISO -- falta {JSON_PATH}: no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
    conn.close()
    raise SystemExit(0)

datos = json.load(open(JSON_PATH, encoding="utf-8"))
print(f"[migrate_055] Iniciando {MIGRATION_ID}: {len(datos['registrar'])} factura(s) a registrar, {len(datos['notas_credito'])} nota(s) de credito...")
registradas, ya, saltadas, errores, notas_ok = [], [], [], [], []


def digitos(x):
    return re.sub(r"\D", "", str(x or ""))


def cubierto(pedido_id):
    """Suma de las facturas VIGENTES (con CAE, no anuladas, no notas) ya asignadas al pedido."""
    return cur.execute("""SELECT COALESCE(SUM(total), 0) FROM facturas WHERE CAST(pedido_id AS TEXT) = ? AND cae IS NOT NULL AND trim(cae) != ''
                          AND estado != 'ANULADA' AND tipo_comprobante NOT LIKE 'NOTA_%'""", (str(pedido_id),)).fetchone()[0] or 0.0


def validar_pedido(pedido_id, cuit, total_factura):
    p = cur.execute("SELECT id, cliente_id, total, estado FROM pedidos WHERE id = ?", (int(pedido_id),)).fetchone()
    if p is None:
        return None, f"el pedido #{pedido_id} no existe"
    if p[3] == "ANULADO":
        return None, f"el pedido #{pedido_id} esta anulado"
    c = cur.execute("SELECT cuit FROM clientes WHERE id = ?", (p[1],)).fetchone()
    if c is None or digitos(c[0]) != digitos(cuit):
        return None, f"el CUIT del cliente del pedido #{pedido_id} no coincide con el de la factura"
    if cubierto(pedido_id) + total_factura > (p[2] or 0.0) * 1.01 + 1:
        return None, f"el pedido #{pedido_id} ya esta cubierto por otras facturas"
    return p[1], None


# ---------------------------------------------------------------- 1) facturas
for r in datos["registrar"]:
    etiqueta = f"{r['pv']:05d}-{r['numero']:08d}"
    try:
        cur.execute("SAVEPOINT reg")
        if cur.execute("SELECT 1 FROM facturas WHERE punto_venta = ? AND numero_comprobante = ? AND trim(cae) = ?", (r["pv"], r["numero"], r["cae"])).fetchone():
            ya.append(etiqueta); cur.execute("RELEASE reg"); continue
        if cur.execute("SELECT 1 FROM facturas WHERE punto_venta = ? AND numero_comprobante = ? AND tipo_comprobante = ?", (r["pv"], r["numero"], r["tipo"])).fetchone():
            saltadas.append((etiqueta, f"ya existe un comprobante {r['tipo']} con ese numero y otro CAE")); cur.execute("RELEASE reg"); continue
        cliente_id, motivo = validar_pedido(r["pedido_id"], r["cuit"], r["totales"]["total"])
        if motivo:
            saltadas.append((etiqueta, motivo)); cur.execute("RELEASE reg"); continue
        for it in (r["items"] or []):
            if it["pedido_item_id"] is not None and not cur.execute("SELECT 1 FROM pedidos_items WHERE id = ? AND pedido_id = ?", (it["pedido_item_id"], int(r["pedido_id"]))).fetchone():
                raise ValueError(f"el renglon #{it['pedido_item_id']} no es del pedido #{r['pedido_id']}")
        t = r["totales"]
        nota = (f"[SISTEMA] Registrada desde el PDF de ARCA (S882, migrate_055): asignada al pedido #{r['pedido_id']} por decision de Carlos (08/10)."
                + ("" if r["items"] else " Renglones NO cargados: revisar a mano (Card #144)."))
        fid = uuid.uuid4().hex
        cur.execute("""INSERT INTO facturas (id, cliente_id, pedido_id, cuit_comprador, tipo_comprobante, punto_venta, numero_comprobante, fecha_emision, estado,
                                             neto_gravado, iva_21, iva_105, exento, percepciones, total, cae, cae_vencimiento, flags_estado, notas_auditoria)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'AUTORIZADA_AFIP', ?, ?, ?, ?, 0, ?, ?, ?, 3, ?)""",
                    (fid, cliente_id, str(r["pedido_id"]), r["cuit"], r["tipo"], r["pv"], r["numero"], r["fecha"],
                     t["neto_gravado"], t["iva_21"], t["iva_105"], t["exento"], t["total"], r["cae"], r["vto"], nota))
        for it in (r["items"] or []):
            cur.execute("""INSERT INTO facturas_items (factura_id, pedido_item_id, remito_item_id, descripcion, cantidad, precio_unitario_neto, alicuota_iva, subtotal_neto)
                           VALUES (?, ?, NULL, ?, ?, ?, ?, ?)""", (fid, it["pedido_item_id"], it["descripcion"], it["cantidad"], it["precio"], it["alicuota"], it["subtotal"]))
        registradas.append((etiqueta, r["pedido_id"]))
        cur.execute("RELEASE reg")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO reg"); cur.execute("RELEASE reg")
        errores.append((etiqueta, f"{type(e).__name__}: {e}"))

# ---------------------------------------------------------------- 2) notas de credito
for n in datos["notas_credito"]:
    etiqueta = f"NC {n['pv']:05d}-{n['numero']:08d}"
    try:
        cur.execute("SAVEPOINT nc")
        if cur.execute("SELECT 1 FROM facturas WHERE punto_venta = ? AND numero_comprobante = ? AND tipo_comprobante = ?", (n["pv"], n["numero"], n["tipo"])).fetchone():
            ya.append(etiqueta); cur.execute("RELEASE nc"); continue
        a = n["ajusta"]
        fac = cur.execute("""SELECT id, cliente_id, CAST(pedido_id AS TEXT), total, estado, COALESCE(flags_estado, 3) FROM facturas
                             WHERE punto_venta = ? AND numero_comprobante = ? AND trim(cae) = ? AND tipo_comprobante NOT LIKE 'NOTA_%'""", (a["pv"], a["numero"], a["cae"])).fetchall()
        if len(fac) != 1 or fac[0][4] == "ANULADA":
            saltadas.append((etiqueta, f"la factura {a['numero']} que corrige no esta (una sola, vigente) en V5")); cur.execute("RELEASE nc"); continue
        fid, cliente_id, pedido_id, total_f, _estado, flags_f = fac[0]
        c = cur.execute("SELECT cuit FROM clientes WHERE id = ?", (cliente_id,)).fetchone()
        if c is None or digitos(c[0]) != digitos(n["cuit"]):
            saltadas.append((etiqueta, "el CUIT del cliente de la factura no es el de la nota")); cur.execute("RELEASE nc"); continue
        if n["totales"]["total"] > (total_f or 0.0) + 0.01:
            saltadas.append((etiqueta, "la nota es mayor que la factura que corrige")); cur.execute("RELEASE nc"); continue
        it = n["item"]
        if it["pedido_item_id"] is not None:
            base = cur.execute("SELECT COALESCE(SUM(cantidad), 0) FROM facturas_items WHERE factura_id = ? AND pedido_item_id = ?", (fid, it["pedido_item_id"])).fetchone()[0]
            if base + EPS < it["cantidad"]:
                saltadas.append((etiqueta, f"la factura {a['numero']} solo tiene {base:g} en ese renglon y la nota acredita {it['cantidad']:g}")); cur.execute("RELEASE nc"); continue
        nid = uuid.uuid4().hex
        t = n["totales"]
        cur.execute("""INSERT INTO facturas (id, cliente_id, pedido_id, cuit_comprador, tipo_comprobante, punto_venta, numero_comprobante, fecha_emision, estado,
                                             neto_gravado, iva_21, iva_105, exento, percepciones, total, cae, cae_vencimiento, flags_estado, notas_auditoria)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'AUTORIZADA_AFIP', ?, ?, ?, ?, 0, ?, ?, ?, ?, ?)""",
                    (nid, cliente_id, pedido_id, n["cuit"], n["tipo"], n["pv"], n["numero"], n["fecha"], t["neto_gravado"], t["iva_21"], t["iva_105"], t["exento"], t["total"],
                     n["cae"], n["vto"], 3 | ES_NC,
                     f"[SISTEMA] Registrada desde el PDF de ARCA (S882, migrate_055): corrige la factura {a['numero']}. Motivo impreso: {n['motivo']}."))
        cur.execute("""INSERT INTO facturas_items (factura_id, pedido_item_id, remito_item_id, descripcion, cantidad, precio_unitario_neto, alicuota_iva, subtotal_neto)
                       VALUES (?, ?, NULL, ?, ?, ?, ?, ?)""", (nid, it["pedido_item_id"], it["descripcion"], it["cantidad"], it["precio"], it["alicuota"], it["subtotal"]))
        cur.execute("INSERT INTO facturas_ajustes (factura_nc_nd_id, factura_ajustada_id, monto_aplicado, fecha_vinculo) VALUES (?, ?, ?, datetime('now'))", (nid, fid, t["total"]))
        cur.execute("UPDATE facturas SET flags_estado = ? WHERE id = ?", (flags_f | TIENE_NC, fid))
        notas_ok.append(etiqueta)
        cur.execute("RELEASE nc")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO nc"); cur.execute("RELEASE nc")
        errores.append((etiqueta, f"{type(e).__name__}: {e}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_055] OK -- facturas registradas {len(registradas)}, notas de credito {len(notas_ok)}, ya estaban {len(ya)}, saltadas {len(saltadas)}, con error {len(errores)}; {MIGRATION_ID} registrada.")
for n, ped in registradas:
    print(f"[migrate_055]   {n} -> pedido #{ped}")
for n in notas_ok:
    print(f"[migrate_055]   {n} registrada y vinculada a la factura que corrige")
for n, m in saltadas:
    print(f"[migrate_055] AVISO -- {n}: {m}")
for n, m in errores:
    print(f"[migrate_055] ERROR -- {n}: {m} (ese comprobante quedo como estaba)")
conn.close()
