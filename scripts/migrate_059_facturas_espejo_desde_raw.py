"""
migrate_059_facturas_espejo_desde_raw.py
========================================
Plan de saneamiento / Card #164 (S882, 08/10/2026): la ingesta vieja (MODO ESPEJO) seguia guardando cada factura nueva mal: tipo inferido de la condicion de IVA (Factura A como B), total = neto, estado BORRADOR
aunque tuviera CAE y renglones sin enlazar al pedido. El codigo ya se corrigio (backend/remitos/service.py create_from_ingestion); esta migracion corrige las facturas espejo que ya habian quedado asi
(2614 y 2615 del 08/10, y las que entren con el codigo viejo antes de que P se relance con el nuevo).

LOS DATOS salen del propio PDF de ARCA, que la ingesta guarda en `ingesta_facturas_raw.parsed_data_raw` (tipo por codigo AFIP, fecha de emision, neto, total, vencimiento del CAE, renglones): no hace falta
ningun archivo externo. Se corrige SOLO si todo cierra: el raw es unico y PROCESADO, trae el mismo numero y el mismo CAE, el desglose del PDF suma el total, y la factura de V5 muestra el defecto conocido
(total igual al neto o ya igual al total, estado BORRADOR, sin la marca de correccion).

QUE HACE: tipo, fecha de emision, neto, IVA, total y vencimiento desde el PDF; estado -> AUTORIZADA_AFIP; enlaza cada renglon de la factura con su renglon de pedido (y del remito) cuando es unico
(mismo producto y misma cantidad). Nota [SISTEMA]. QUE NO HACE: no toca pedidos, remitos ni otras facturas; lo que no cierra se informa y queda como estaba.

SEGURIDAD: SAVEPOINT por factura, despues del backup de auto_migrar, idempotente (la marca de la nota), sale 0.

MIGRATION_ID = "059_facturas_espejo_desde_raw"
NRO_SESION = 882
"""
import json
import os
import re
import sqlite3

MIGRATION_ID = "059_facturas_espejo_desde_raw"
NRO_SESION = 882
EPS = 0.5
MARCA = "Datos fiscales leidos del PDF de ARCA"

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_059] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("facturas", "facturas_items", "facturas_remitos", "remitos_items", "pedidos_items", "productos", "ingesta_facturas_raw"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_059] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)


def norm(x):
    return re.sub(r"\s+", " ", str(x or "").upper()).strip()


def desglose(items, neto_pdf, total_pdf):
    """Mismo criterio que backend/ingesta/conciliador.py::desglose_importes: neto y total los manda ARCA; el IVA sale de los renglones por alicuota; lo que sobra hasta el total son percepciones."""
    iva_21 = sum((it.get("subtotal") or 0) * 0.21 for it in items if abs((it.get("alicuota_iva") if it.get("alicuota_iva") is not None else 21) - 21) < 0.01)
    iva_105 = sum((it.get("subtotal") or 0) * 0.105 for it in items if abs((it.get("alicuota_iva") or 0) - 10.5) < 0.01)
    exento = sum((it.get("subtotal") or 0) for it in items if abs(it.get("alicuota_iva") if it.get("alicuota_iva") is not None else 21) < 0.01)
    neto = neto_pdf if neto_pdf is not None else sum((it.get("subtotal") or 0) for it in items)
    percep = round(total_pdf - neto - iva_21 - iva_105 - exento, 2)
    return neto, iva_21, iva_105, exento, (0.0 if abs(percep) < EPS else percep), total_pdf


candidatas = cur.execute("""SELECT id, punto_venta, numero_comprobante, cae, total, notas_auditoria, cae_vencimiento, CAST(pedido_id AS TEXT)
                            FROM facturas WHERE estado = 'BORRADOR' AND cae IS NOT NULL AND trim(cae) != '' AND tipo_comprobante LIKE 'FACTURA_%'
                            AND notas_auditoria LIKE 'GENERADA POR MODO ESPEJO%' AND notas_auditoria NOT LIKE ?""", (f"%{MARCA}%",)).fetchall()
print(f"[migrate_059] Iniciando {MIGRATION_ID}: {len(candidatas)} factura(s) espejo en BORRADOR con CAE a revisar...")
corregidas, saltadas, errores = [], [], []
for fid, pv, nc, cae, total_v5, notas, vto_v5, pedido_id in candidatas:
    etiqueta = f"{(pv or 0):05d}-{(nc or 0):08d}"
    try:
        cur.execute("SAVEPOINT fac")
        raws = cur.execute("""SELECT parsed_data_raw FROM ingesta_facturas_raw WHERE audit_status = 'PROCESADO' AND filename LIKE ?""", (f"%_{(pv or 0):05d}_{(nc or 0):08d}%",)).fetchall()
        datos = []
        for (pd,) in raws:
            try:
                d = json.loads(pd) if isinstance(pd, (str, bytes)) else pd
            except Exception:
                continue
            f = (d or {}).get("factura") or {}
            if str(f.get("cae") or "").strip() == str(cae).strip() and re.sub(r"\D", "", str(f.get("numero") or ""))[-8:].lstrip("0") == str(nc):
                datos.append(d)
        if len(datos) != 1:
            saltadas.append((etiqueta, f"no hay un unico registro de ingesta procesado con ese numero y CAE ({len(datos)})")); cur.execute("RELEASE fac"); continue
        d = datos[0]; f = d["factura"]; items = d.get("items") or []
        tipo = str(f.get("tipo_comprobante") or "").upper()
        if not tipo.startswith("FACTURA_") or f.get("total_final") is None or f.get("total_neto") is None or not f.get("fecha_emision"):
            saltadas.append((etiqueta, "el PDF no trae tipo, fecha, neto y total")); cur.execute("RELEASE fac"); continue
        total_pdf, neto_pdf = float(f["total_final"]), float(f["total_neto"])
        if abs((total_v5 or 0) - neto_pdf) > EPS and abs((total_v5 or 0) - total_pdf) > EPS:
            saltadas.append((etiqueta, f"el total de V5 ({total_v5}) no es ni el neto ni el total del PDF: alguien lo toco, no se pisa")); cur.execute("RELEASE fac"); continue
        neto, iva21, iva105, exento, percep, total = desglose(items, neto_pdf, total_pdf)
        if abs(neto + iva21 + iva105 + exento + percep - total) > EPS or abs(iva21 + iva105 - (total - neto - exento - percep)) > EPS:
            saltadas.append((etiqueta, "el desglose del PDF no suma el total")); cur.execute("RELEASE fac"); continue
        vto = f.get("vto_cae")
        vto = vto if (vto and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(vto))) else None
        marca = f"[SISTEMA] {MARCA} (S882, migrate_059): tipo {tipo}, total {total_v5} -> {total}, estado BORRADOR -> AUTORIZADA_AFIP."
        cur.execute("""UPDATE facturas SET tipo_comprobante = ?, fecha_emision = ?, neto_gravado = ?, iva_21 = ?, iva_105 = ?, exento = ?, percepciones = ?, total = ?,
                       cae_vencimiento = COALESCE(cae_vencimiento, ?), estado = 'AUTORIZADA_AFIP', notas_auditoria = ? WHERE id = ?""",
                    (tipo, f["fecha_emision"], round(neto, 2), round(iva21, 2), round(iva105, 2), round(exento, 2), percep, round(total, 2), vto, (notas or "") + " | " + marca, fid))
        # renglones: mismo producto y misma cantidad, unico; y su renglon de remito
        contador = [0]
        pedido_items = cur.execute("""SELECT pi.id, pi.cantidad, pr.nombre FROM pedidos_items pi JOIN productos pr ON pr.id = pi.producto_id WHERE CAST(pi.pedido_id AS TEXT) = ?""", (pedido_id,)).fetchall()
        libres = list(pedido_items)
        sin_enlace = []

        def enlazar(fi_id, pedido_item):
            libres.remove(pedido_item)
            ri = cur.execute("""SELECT ri.id FROM remitos_items ri JOIN facturas_remitos fr ON fr.remito_id = ri.remito_id WHERE fr.factura_id = ? AND ri.pedido_item_id = ?""", (fid, pedido_item[0])).fetchone()
            cur.execute("UPDATE facturas_items SET pedido_item_id = ?, remito_item_id = COALESCE(remito_item_id, ?) WHERE id = ?", (pedido_item[0], ri[0] if ri else None, fi_id))
            contador[0] += 1

        # paso 1: mismo producto (por nombre) y, si hay varios, misma cantidad
        for fi_id, desc, cant, pi_actual in cur.execute("SELECT id, descripcion, cantidad, pedido_item_id FROM facturas_items WHERE factura_id = ? ORDER BY id", (fid,)).fetchall():
            if pi_actual is not None:
                continue
            cands = [p for p in libres if norm(p[2]) == norm(desc) and abs(p[1] - cant) < 0.001]
            if len(cands) != 1:
                cands = [p for p in libres if norm(p[2]) == norm(desc)]      # mismo producto aunque la cantidad difiera (factura parcial)
            if len(cands) == 1:
                enlazar(fi_id, cands[0])
            else:
                sin_enlace.append((fi_id, cant))
        # paso 2: la factura y el pedido llaman distinto al mismo producto ("talle M caja x 100" / "caja por 100 Talle M"): si quedan tantos renglones
        # sin enlazar como renglones libres en el pedido, se emparejan por cantidad cuando esa cantidad es unica de los dos lados
        if sin_enlace and len(sin_enlace) == len(libres):
            for fi_id, cant in list(sin_enlace):
                de_factura = [c for _, c in sin_enlace if abs(c - cant) < 0.001]
                del_pedido = [p for p in libres if abs(p[1] - cant) < 0.001]
                if len(de_factura) == 1 and len(del_pedido) == 1:
                    enlazar(fi_id, del_pedido[0])
        corregidas.append((etiqueta, tipo, total, contador[0]))
        cur.execute("RELEASE fac")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO fac"); cur.execute("RELEASE fac")
        errores.append((etiqueta, f"{type(e).__name__}: {e}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_059] OK -- corregidas {len(corregidas)}, saltadas {len(saltadas)}, con error {len(errores)}; {MIGRATION_ID} registrada.")
for n, tipo, total, enl in corregidas:
    print(f"[migrate_059]   {n}: {tipo}, total {total:,.2f}, AUTORIZADA_AFIP, {enl} renglon(es) enlazados")
for n, m in saltadas:
    print(f"[migrate_059] AVISO -- {n}: {m}")
for n, m in errores:
    print(f"[migrate_059] ERROR -- {n}: {m} (esa factura quedo como estaba)")
conn.close()
