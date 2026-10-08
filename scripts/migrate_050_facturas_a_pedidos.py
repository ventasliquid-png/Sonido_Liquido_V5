"""
migrate_050_facturas_a_pedidos.py
=================================
Plan de saneamiento, Fase 2 (S882, 08/10/2026; Cards #164, #165): asigna a sus pedidos las facturas emitidas que V5 no tiene registradas y
corrige el enlace a pedido de las que estaban enganchadas al pedido equivocado.

Los datos salen de `scripts/asignar_facturas_a_pedidos.py --generar-migracion` (solo propuestas de confianza ALTA: producto, cantidad, total y
fecha apuntan a un unico pedido) y viajan en `scripts/data/asignacion_facturas_s882.json`. La lectura de los PDF esta validada contra el CSV
oficial de ARCA (Mis Comprobantes Emitidos).

QUE HACE
  1. REGISTRAR: crea el registro de la factura (estado AUTORIZADA_AFIP, tipo y totales del PDF de ARCA, CAE y vencimiento) ligado al pedido, con
     sus renglones enlazados a los renglones del pedido cuando la lectura del PDF cierra con el total impreso.
  2. ENLACES: pasa una factura ya registrada del pedido equivocado al correcto (cabecera y enlace de renglones).
QUE NO HACE: no cambia el estado del pedido ni sus bits, no toca remitos, no crea clientes ni pedidos, no borra nada, no toca duplicadas ni
las propuestas de confianza media o baja (esas las decide Carlos).

SEGURIDAD (por factura, con SAVEPOINT; un error en una no frena el arranque)
  - No crea si ya existe un comprobante con ese punto de venta y numero (idempotente).
  - Verifica que el pedido exista, no este anulado y que el CUIT de su cliente sea el de la factura.
  - Verifica que el pedido no quede cubierto de mas: suma de las facturas vigentes del pedido + esta <= total del pedido (con 1 % de margen).
  - Un enlace solo se corrige si la factura sigue enganchada al pedido que se audito.
  - Corre despues del backup de auto_migrar; no se escribe la base de P por la red.

MIGRATION_ID = "050_facturas_a_pedidos"
NRO_SESION = 882
"""
import json
import os
import re
import sqlite3
import uuid

MIGRATION_ID = "050_facturas_a_pedidos"
NRO_SESION = 882

AQUI = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(AQUI, "..", "pilot_v5x.db")
JSON_PATH = os.path.join(AQUI, "data", "asignacion_facturas_s882.json")

conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (
        id VARCHAR PRIMARY KEY,
        nro_sesion INTEGER,
        aplicada_en DATETIME DEFAULT (datetime('now'))
    )
""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_050] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("facturas", "facturas_items", "pedidos", "pedidos_items", "clientes"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_050] ERROR -- no existe la tabla '{t}': no es una base de V5.")
        conn.close()
        raise SystemExit(1)
if not os.path.exists(JSON_PATH):
    print(f"[migrate_050] AVISO -- falta {JSON_PATH}: no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
    conn.close()
    raise SystemExit(0)

datos = json.load(open(JSON_PATH, encoding="utf-8"))
print(f"[migrate_050] Iniciando {MIGRATION_ID}: {len(datos['registrar'])} factura(s) a registrar, {len(datos['enlaces'])} enlace(s) a corregir...")
registradas, ya, saltadas, errores, enlazadas = [], [], [], [], []


def solo_digitos(x):
    return re.sub(r"\D", "", str(x or ""))


def cubierto(pedido_id):
    """Suma de las facturas VIGENTES (con CAE, no anuladas) ya asignadas al pedido."""
    r = cur.execute("""SELECT COALESCE(SUM(total), 0) FROM facturas WHERE CAST(pedido_id AS TEXT) = ? AND cae IS NOT NULL AND trim(cae) != ''
                       AND estado != 'ANULADA'""", (str(pedido_id),)).fetchone()
    return r[0] or 0.0


def validar_pedido(pedido_id, cuit, total_factura, descontar=0.0):
    """-> (cliente_id, motivo_de_rechazo|None)"""
    p = cur.execute("SELECT id, cliente_id, total, estado FROM pedidos WHERE id = ?", (int(pedido_id),)).fetchone()
    if p is None:
        return None, f"el pedido #{pedido_id} no existe"
    if p[3] == "ANULADO":
        return None, f"el pedido #{pedido_id} esta anulado"
    c = cur.execute("SELECT cuit FROM clientes WHERE id = ?", (p[1],)).fetchone()
    if c is None or solo_digitos(c[0]) != solo_digitos(cuit):
        return None, f"el CUIT del cliente del pedido #{pedido_id} no coincide con el de la factura"
    if cubierto(pedido_id) - descontar + total_factura > (p[2] or 0.0) * 1.01 + 1:
        return None, f"el pedido #{pedido_id} ya esta cubierto por otras facturas"
    return p[1], None


# ---------------------------------------------------------------- 1) registrar
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
        t = r["totales"]
        nota = (f"[SISTEMA] Registrada desde el PDF de ARCA (S882, migrate_050): asignada al pedido #{r['pedido_id']} "
                f"(confianza {r['confianza']}, puntaje {r['puntaje']}; {r['motivos']})." + ("" if r["items"] else " Renglones NO cargados: revisar a mano (Card #144)."))
        fid = uuid.uuid4().hex
        cur.execute("""INSERT INTO facturas (id, cliente_id, pedido_id, cuit_comprador, tipo_comprobante, punto_venta, numero_comprobante, fecha_emision, estado,
                                             neto_gravado, iva_21, iva_105, exento, percepciones, total, cae, cae_vencimiento, flags_estado, notas_auditoria)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'AUTORIZADA_AFIP', ?, ?, ?, ?, 0, ?, ?, ?, 3, ?)""",
                    (fid, cliente_id, str(r["pedido_id"]), r["cuit"], r["tipo"], r["pv"], r["numero"], r["fecha"],
                     t["neto_gravado"], t["iva_21"], t["iva_105"], t["exento"], t["total"], r["cae"], r["vto"], nota))
        for it in (r["items"] or []):
            cur.execute("""INSERT INTO facturas_items (factura_id, pedido_item_id, remito_item_id, descripcion, cantidad, precio_unitario_neto, alicuota_iva, subtotal_neto)
                           VALUES (?, ?, NULL, ?, ?, ?, ?, ?)""", (fid, it["pedido_item_id"], it["descripcion"], it["cantidad"], it["precio"], it["alicuota"], it["subtotal"]))
        registradas.append((etiqueta, r["pedido_id"], bool(r["items"])))
        cur.execute("RELEASE reg")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO reg"); cur.execute("RELEASE reg")
        errores.append((etiqueta, f"{type(e).__name__}: {e}"))

# ---------------------------------------------------------------- 2) enlaces
for e in datos["enlaces"]:
    etiqueta = f"{e['pv']:05d}-{e['numero']:08d}"
    try:
        cur.execute("SAVEPOINT enl")
        f = cur.execute("SELECT id, cliente_id, CAST(pedido_id AS TEXT), total, notas_auditoria, cuit_comprador FROM facturas WHERE punto_venta = ? AND numero_comprobante = ? AND trim(cae) = ?",
                        (e["pv"], e["numero"], e["cae"])).fetchone()
        if f is None:
            saltadas.append((etiqueta, "no existe con ese CAE")); cur.execute("RELEASE enl"); continue
        fid, cliente_id, pedido_actual, total, notas, cuit = f
        c_f = cur.execute("SELECT cuit FROM clientes WHERE id = ?", (cliente_id,)).fetchone()   # la ingesta vieja no cargaba cuit_comprador
        cuit = cuit or (c_f[0] if c_f else "")
        if pedido_actual == e["pedido_nuevo"]:
            ya.append(etiqueta); cur.execute("RELEASE enl"); continue
        if pedido_actual != e["pedido_actual"]:
            saltadas.append((etiqueta, f"ya no esta enganchada al pedido #{e['pedido_actual']} sino al #{pedido_actual}: no se toca")); cur.execute("RELEASE enl"); continue
        cli_nuevo, motivo = validar_pedido(e["pedido_nuevo"], cuit or "", total or 0.0)
        if motivo:
            saltadas.append((etiqueta, motivo)); cur.execute("RELEASE enl"); continue
        marca = f"[SISTEMA] Enlace corregido al pedido #{e['pedido_nuevo']} (antes #{pedido_actual}) por la asignacion del plan de saneamiento (S882, migrate_050)."
        cur.execute("UPDATE facturas SET pedido_id = ?, notas_auditoria = ? WHERE id = ?", (e["pedido_nuevo"], ((notas + " | ") if notas else "") + marca, fid))
        # Renglones: por texto (sin distinguir mayusculas ni espacios) y cantidad; si la factura conserva el texto original de V5 (no se leyo el PDF
        # entero, tipicamente por la bonificacion) y hay igual cantidad de renglones, se emparejan por orden y cantidad.
        def _n(s):
            return re.sub(r"\s+", " ", str(s or "").upper()).strip()
        filas_items = cur.execute("SELECT id, descripcion, cantidad FROM facturas_items WHERE factura_id = ? ORDER BY id", (fid,)).fetchall()
        libres = list(filas_items)
        for it in e["items"]:
            hit = next((r for r in libres if _n(r[1]) == _n(it["descripcion"]) and abs(r[2] - it["cantidad"]) < 0.001), None)
            if hit is None and len(filas_items) == len(e["items"]):
                idx = e["items"].index(it)
                if idx < len(filas_items) and filas_items[idx] in libres and abs(filas_items[idx][2] - it["cantidad"]) < 0.001:
                    hit = filas_items[idx]
            if hit is not None:
                libres.remove(hit)
                cur.execute("UPDATE facturas_items SET pedido_item_id = ? WHERE id = ?", (it["pedido_item_id"], hit[0]))
        enlazadas.append((etiqueta, pedido_actual, e["pedido_nuevo"]))
        cur.execute("RELEASE enl")
    except Exception as ex:  # noqa: BLE001
        cur.execute("ROLLBACK TO enl"); cur.execute("RELEASE enl")
        errores.append((etiqueta, f"{type(ex).__name__}: {ex}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_050] OK -- registradas {len(registradas)}, enlaces corregidos {len(enlazadas)}, ya estaban {len(ya)}, saltadas {len(saltadas)}, con error {len(errores)}; {MIGRATION_ID} registrada.")
for n, ped, con_items in registradas:
    if not con_items:
        print(f"[migrate_050]   {n} -> pedido #{ped}: registrada SIN renglones -- revisar a mano (Card #144)")
for n, a, b in enlazadas:
    print(f"[migrate_050]   {n}: pedido #{a} -> #{b}")
for n, m in saltadas:
    print(f"[migrate_050] AVISO -- {n}: {m}")
for n, m in errores:
    print(f"[migrate_050] ERROR -- {n}: {m} (esa factura quedo como estaba)")
conn.close()
