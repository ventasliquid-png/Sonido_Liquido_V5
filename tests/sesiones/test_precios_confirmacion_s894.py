r"""Card #144 (S894, Carlos 28/10): «No quiero que solo avise: quiero que provoque una confirmación del operador si hay discrepancia».
El lector lee «% Bonif» y el «Subtotal» de ARCA; la Ingesta y «Conciliar contra PR» comparan el precio efectivo de la factura con el del pedido
(descuento del renglón y general); con diferencia, 409 DIFERENCIA_DE_PRECIO y la factura entra solo si el operador confirma (motivo opcional), con
nota [SISTEMA] en la factura y el pedido y su usuario; la Ingesta pide sesión. Sobre COPIAS de la base de P del 27/10 15:58 (Wullich, 5 %)."""
import sys, os, sqlite3, json, uuid
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from backend.pedidos.constants import PedidoFlags, STATE_MASK
from backend.remitos.pdf_parser import extract_text_from_pdf, parse_invoice_data
from backend.ingesta.precios import precio_efectivo_factura, diferencia_de_precio, factor_descuento_general
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261027_1558.db"
T = os.path.join(RAIZ, "scratch", "test_precios_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
def x(sql, *a):
    con = sqlite3.connect(T); con.execute(sql, a); con.commit(); con.close()

# ---------- el lector ----------
pdf2616 = q("select pdf_bytes from ingesta_facturas_raw where filename like '%_00002616 %'")[0][0]
it = parse_invoice_data(*extract_text_from_pdf(pdf2616))["items"][0]
check(f"el lector de la 2616 lee la bonificación (5 %) y el subtotal de ARCA (3.967.200), con el precio de lista (11.600) {it['bonificacion'], it['subtotal'], it['precio_unitario']}",
      it["bonificacion"] == 5.0 and it["subtotal"] == 3967200.0 and it["precio_unitario"] == 11600.0)

# ---------- el cálculo ----------
check("precio efectivo de la factura: el subtotal de ARCA sobre la cantidad (11.020), o el precio con la bonificación si no vino el subtotal",
      precio_efectivo_factura({"cantidad": 360, "subtotal": 3967200.0, "precio_unitario": 11600.0}) == 11020.0
      and abs(precio_efectivo_factura({"cantidad": 360, "precio_unitario": 11600.0, "bonificacion": 5.0}) - 11020.0) < 1e-6)
class PI:
    def __init__(s, cant, precio, dto, sub, pid=1): s.cantidad, s.precio_unitario, s.descuento_porcentaje, s.subtotal, s.id, s.producto = cant, precio, dto, sub, pid, None
class PED:
    def __init__(s, items, dg): s.items, s.descuento_global_importe = items, dg
sin_dto = PI(10, 1000.0, 0.0, 10000.0)
check("con un descuento general del 5 % en el pedido, cada peso vale 0,95", abs(factor_descuento_general(PED([sin_dto], 500.0)) - 0.95) < 1e-9)
check("dentro de la tolerancia ($1 o 0,5 %) no hay diferencia; afuera sí, con el detalle",
      diferencia_de_precio(sin_dto, {"cantidad": 10, "subtotal": 9960.0}) is None
      and "factura tiene 5 % de bonificación" in diferencia_de_precio(sin_dto, {"cantidad": 10, "subtotal": 9500.0, "bonificacion": 5.0}, producto="X")["detalle"])

# ---------- Ingesta: un pedido abierto de Wullich con dos renglones ----------
cliente_id, cuit = q("select p.cliente_id, c.cuit from pedidos p join clientes c on c.id=p.cliente_id where p.id=128")[0]
SURGI, OTRO = 177, 201        # SURGIZIME (11.600) y el de la 2617 (46.400)
FLAGS = (q("select flags_estado from pedidos where id=128")[0][0] & ~int(STATE_MASK)) | int(PedidoFlags.ES_FIRME)
def pedido_nuevo(renglones, dg=0.0):
    """Copia del #128 abierta, con estos renglones (producto, cantidad, precio, descuento %). Devuelve (id, {producto: pedido_item_id})."""
    con = sqlite3.connect(T)
    cols = [r[1] for r in con.execute("pragma table_info(pedidos)")]
    nuevo = con.execute("select max(id) from pedidos").fetchone()[0] + 1
    fila = dict(zip(cols, con.execute("select * from pedidos where id=128").fetchone()))
    neto = sum(c * p * (1 - d / 100) for _, c, p, d in renglones) - dg
    fila.update(id=nuevo, estado="PENDIENTE", nota="", oc=None, flags_estado=FLAGS, descuento_global_importe=dg,
                descuento_global_porcentaje=0.0, total=round(neto * 1.21, 2))
    con.execute(f"insert into pedidos ({','.join(cols)}) values ({','.join('?' * len(cols))})", [fila[c] for c in cols])
    icols = [r[1] for r in con.execute("pragma table_info(pedidos_items)")]
    base = dict(zip(icols, con.execute("select * from pedidos_items where pedido_id=128").fetchone()))
    ids = {}
    for prod, cant, precio, dto in renglones:
        f = dict(base); f.update(id=None, pedido_id=nuevo, producto_id=prod, cantidad=cant, precio_unitario=precio, descuento_porcentaje=dto,
                                 descuento_importe=round(cant * precio * dto / 100, 2), subtotal=round(cant * precio * (1 - dto / 100), 2))
        cur = con.execute(f"insert into pedidos_items ({','.join(icols)}) values ({','.join('?' * len(icols))})", [f[c] for c in icols])
        ids[prod] = cur.lastrowid
    con.commit(); con.close(); return nuevo, ids
def raw(numero, items, neto):
    rid = uuid.uuid4().hex
    parsed = {"cliente": {"cuit": cuit}, "factura": {"numero": numero, "cae": "8641" + numero[-8:].rjust(10, "7"), "vto_cae": "2026-11-07", "codigo_afip": "01",
              "tipo_comprobante": "FACTURA_A", "fecha_emision": "2026-10-28", "total_neto": neto, "total_final": round(neto * 1.21, 2)}, "items": items}
    x("insert into ingesta_facturas_raw (id, filename, pdf_bytes, audit_status, parsed_data_raw, flags_estado, created_at) values (?, ?, ?, 'RECIBIDO', ?, 0, datetime('now'))",
      rid, f"test_{numero}.pdf", b"%PDF-1.4", json.dumps(parsed))
    return rid, parsed
def aprobar(rid, parsed, pedido, **extra):
    p = {"cliente": {"id": cliente_id, "cuit": cuit, "razon_social": "WULLICH MATIAS GUILLERMO"},
         "factura": {k: parsed["factura"][k] for k in ("numero", "cae", "vto_cae")}, "bultos": 1, "valor_declarado": 0.0,
         "items": [{"descripcion": i["descripcion"], "cantidad": i["cantidad"], "precio_unitario": i["precio_unitario"], "bonificacion": i.get("bonificacion", 0),
                    "producto_id": i["producto_id"]} for i in parsed["items"]],
         "modo_ingesta": "VINCULAR_PARCIAL", "pedido_id_vinculado": pedido}
    p.update(extra)
    return cli.post(f"/ingesta/raw/{rid}/approve", json=p)
def renglon(prod, cant, precio, bonif):
    return {"descripcion": f"producto {prod}", "cantidad": cant, "precio_unitario": precio, "bonificacion": bonif, "alicuota_iva": 21.0,
            "subtotal": round(cant * precio * (1 - bonif / 100), 2), "producto_id": prod}

# A) el pedido tiene el 5 % y la factura también: entra sin preguntar
pa, _ = pedido_nuevo([(SURGI, 100, 11600.0, 5.0), (OTRO, 5, 46400.0, 0.0)])
items = [renglon(SURGI, 100, 11600.0, 5.0), renglon(OTRO, 5, 46400.0, 0.0)]
rid, parsed = raw("00001-00091001", items, 1102000.0 + 232000.0)
r = aprobar(rid, parsed, pa)
f = q("select id, neto_gravado, iva_21, percepciones, notas_auditoria from facturas where numero_comprobante=91001")
fi = q("select precio_unitario_neto, subtotal_neto from facturas_items where factura_id=? order by id", f[0][0]) if f else []
check(f"A: pedido con 5 % y factura con 5 %: entra sin pedir confirmación [{r.status_code}] {r.text[:150] if r.status_code != 200 else ''}", r.status_code == 200 and f)
check(f"A: los renglones de la factura quedan con el precio de lista y el subtotal bonificado, como en el PDF {fi}", fi == [(11600.0, 1102000.0), (46400.0, 232000.0)])
check(f"A: neto 1.334.000, IVA 280.140, sin percepciones, sin nota de diferencia {f[0][1:4] if f else None}",
      f and f[0][1:4] == (1334000.0, 280140.0, 0.0) and "Diferencia de precio" not in (f[0][4] or ""))

# B) la factura bonifica el segundo renglón y el pedido no: 409, no se registra nada y el raw queda como estaba
pb, ids_b = pedido_nuevo([(SURGI, 100, 11600.0, 5.0), (OTRO, 5, 46400.0, 0.0)])
items = [renglon(SURGI, 100, 11600.0, 5.0), renglon(OTRO, 5, 46400.0, 5.0)]
rid, parsed = raw("00001-00091002", items, 1102000.0 + 220400.0)
nf0, nr0 = q("select count(*) from facturas")[0][0], q("select count(*) from remitos")[0][0]
r = aprobar(rid, parsed, pb)
det = r.json().get("detail") if r.status_code == 409 else None
check(f"B: diferencia de precio: 409 DIFERENCIA_DE_PRECIO con un solo renglón [{r.status_code}]",
      r.status_code == 409 and isinstance(det, dict) and det.get("codigo") == "DIFERENCIA_DE_PRECIO" and len(det.get("diferencias") or []) == 1)
d0 = (det or {}).get("diferencias", [{}])[0]
check(f"B: el renglón dice pedido 46.400 y factura 44.080, la bonificación de la factura y que el pedido no tiene descuento: {d0.get('detalle')}",
      d0.get("pedido_item_id") == ids_b[OTRO] and d0.get("precio_pedido") == 46400.0 and d0.get("precio_factura") == 44080.0
      and "5 % de bonificación" in d0.get("detalle", "") and "sin descuento" in d0.get("detalle", ""))
check("B: no se registró nada (ni factura ni remito) y el PDF sigue RECIBIDO, no en ERROR",
      q("select count(*) from facturas")[0][0] == nf0 and q("select count(*) from remitos")[0][0] == nr0
      and q("select audit_status from ingesta_facturas_raw where id=?", rid)[0][0] == "RECIBIDO")

# C) el operador confirma, con motivo
r = aprobar(rid, parsed, pb, confirmar_diferencias_precio=True, motivo_diferencias_precio="Wullich tiene 5 % en todo; el pedido se cargó sin el descuento")
f = q("select notas_auditoria from facturas where numero_comprobante=91002")
nota_ped = q("select nota from pedidos where id=?", pb)[0][0] or ""
check(f"C: confirmado, la factura entra [{r.status_code}] {r.text[:150] if r.status_code != 200 else ''}", r.status_code == 200 and f)
check("C: la factura dice la diferencia, quién la confirmó y el motivo",
      f and "[SISTEMA] Diferencia de precio con la factura 00001-00091002, confirmada por tmp" in f[0][0] and "Motivo: Wullich tiene 5 %" in f[0][0])
check("C: el pedido también lo dice, y sus renglones no cambiaron (el pedido es soberano)",
      "[SISTEMA] Diferencia de precio con la factura 00001-00091002" in nota_ped
      and q("select precio_unitario, descuento_porcentaje, subtotal from pedidos_items where id=?", ids_b[OTRO])[0] == (46400.0, 0.0, 232000.0))
al = json.loads(q("select audit_log from ingesta_facturas_procesadas where raw_id=?", rid)[0][0])
check(f"C: la auditoría de la ingesta guarda las diferencias, quién y el motivo {al.get('diferencias_precio', {}).get('confirmado_por')}",
      al.get("diferencias_precio", {}).get("confirmado_por") == "tmp" and len(al["diferencias_precio"]["diferencias"]) == 1)

# D) descuento general del pedido (5 %) contra una factura bonificada renglón por renglón: coinciden
pd_, _ = pedido_nuevo([(SURGI, 10, 11600.0, 0.0), (OTRO, 5, 46400.0, 0.0)], dg=round((116000.0 + 232000.0) * 0.05, 2))
items = [renglon(SURGI, 10, 11600.0, 5.0), renglon(OTRO, 5, 46400.0, 5.0)]
rid, parsed = raw("00001-00091003", items, 110200.0 + 220400.0)
r = aprobar(rid, parsed, pd_)
check(f"D: descuento general del 5 % en el pedido y 5 % por renglón en la factura: entra sin preguntar [{r.status_code}] {r.text[:120] if r.status_code != 200 else ''}", r.status_code == 200)

# E) sin sesión no se aprueba
del app.dependency_overrides[get_current_active_user]
pe, _ = pedido_nuevo([(SURGI, 10, 11600.0, 5.0)])
rid, parsed = raw("00001-00091004", [renglon(SURGI, 10, 11600.0, 5.0)], 110200.0)
r = aprobar(rid, parsed, pe)
check(f"E: la Ingesta pide sesión [{r.status_code}]", r.status_code == 401)
app.dependency_overrides[get_current_active_user] = lambda: U()

# F) cuarentena: el pedido nace de la factura con la bonificación como descuento del renglón
rid, parsed = raw("00001-00091005", [renglon(SURGI, 20, 11600.0, 5.0)], 220400.0)
r = aprobar(rid, parsed, None, modo_ingesta=None, modo_cuarentena=True)
pf = q("select pi.precio_unitario, pi.descuento_porcentaje, pi.subtotal from pedidos_items pi join facturas f on f.pedido_id=pi.pedido_id where f.numero_comprobante=91005")
check(f"F: cuarentena: el renglón del pedido nuevo lleva el 5 % y el subtotal bonificado [{r.status_code}] {pf}", r.status_code == 200 and pf == [(11600.0, 5.0, 220400.0)])

# G) un PDF subido antes de la S894 (sin la bonificación en lo guardado): la vista lo vuelve a leer
rid_viejo = q("select id from ingesta_facturas_raw where filename like '%_00002616 %'")[0][0]
guardado = json.loads(q("select parsed_data_raw from ingesta_facturas_raw where id=?", rid_viejo)[0][0])
r = cli.get(f"/ingesta/raw/{uuid.UUID(rid_viejo)}/preview")
vista = (r.json().get("parsed_data") or {}).get("items") if r.status_code == 200 else None
check(f"G: lo guardado de la 2616 no tiene la bonificación, y la vista previa la trae al releer el PDF [{r.status_code}] {vista[0].get('bonificacion') if vista else None}",
      "bonificacion" not in guardado["items"][0] and vista and vista[0].get("bonificacion") == 5.0 and vista[0].get("subtotal") == 3967200.0)

# ---------- Conciliar contra PR: la 2616 contra su remito 0015-00003027 del #128 ----------
from backend.ingesta.conciliador import ConciliadorService
fid = q("select id from facturas where numero_comprobante=2616 and tipo_comprobante='FACTURA_A'")[0][0]
x("delete from facturas_items where factura_id=?", fid); x("delete from facturas_remitos where factura_id=?", fid); x("delete from facturas where id=?", fid)
x("update remitos_items set cantidad_facturada=0 where remito_id=(select id from remitos where numero_legal='0015-00003027')")   # 0 = facturable y sin facturar (NULL = no facturable)
x("update ingesta_facturas_raw set audit_status='RECIBIDO' where id=?", rid_viejo)
rem = q("select r.id, ri.id from remitos r join remitos_items ri on ri.remito_id=r.id where r.numero_legal='0015-00003027'")[0]
emp = [{"item_pdf": 0, "remito_item_id": rem[1]}]
def evaluar():
    s = S(); ev = ConciliadorService.evaluar(s, uuid.UUID(rid_viejo), [str(uuid.UUID(rem[0]))], emp); s.close()
    return [d for d in ev["diferencias"] if d.get("tipo") == "PRECIO"], ev["bloqueos"]
precios, bloq = evaluar()
check(f"7b: la 2616 (5 %) contra su pedido con el 5 %: ninguna diferencia de precio (antes avisaba una al revés) {bloq}", precios == [] and bloq == [])
x("update pedidos_items set descuento_porcentaje=0, descuento_importe=0, subtotal=4176000 where pedido_id=128")
precios, bloq = evaluar()
check(f"7b: con el pedido sin el descuento, una diferencia de precio: {precios[0]['detalle'] if precios else None}",
      len(precios) == 1 and precios[0]["precio"]["precio_pedido"] == 11600.0 and precios[0]["precio"]["precio_factura"] == 11020.0)
cuerpo = {"remito_ids": [str(uuid.UUID(rem[0]))], "emparejamiento": emp}
r = cli.post(f"/ingesta/raw/{uuid.UUID(rid_viejo)}/conciliacion/confirmar", json=cuerpo)
check(f"7b: sin confirmar, 409 DIFERENCIA_DE_PRECIO y no se registra [{r.status_code}]",
      r.status_code == 409 and isinstance(r.json().get("detail"), dict) and r.json()["detail"].get("codigo") == "DIFERENCIA_DE_PRECIO"
      and q("select count(*) from facturas where numero_comprobante=2616 and tipo_comprobante='FACTURA_A'")[0][0] == 0)
r = cli.post(f"/ingesta/raw/{uuid.UUID(rid_viejo)}/conciliacion/confirmar", json={**cuerpo, "confirmar_diferencias_precio": True})
f = q("select notas_auditoria from facturas where numero_comprobante=2616 and tipo_comprobante='FACTURA_A'")
check(f"7b: confirmado (sin motivo), entra con la nota en la factura y en el pedido [{r.status_code}] {r.text[:120] if r.status_code != 200 else ''}",
      r.status_code == 200 and f and "[SISTEMA] Diferencia de precio con FACTURA_A" in f[0][0] and "confirmada por tmp" in f[0][0] and "Motivo:" not in f[0][0]
      and "[SISTEMA] Diferencia de precio con FACTURA_A" in (q("select nota from pedidos where id=128")[0][0] or ""))

# ---------- las pantallas ----------
ing = open(os.path.join(RAIZ, "frontend", "src", "views", "Pedidos", "IngestaFacturaView.vue"), encoding="utf-8").read()
con = open(os.path.join(RAIZ, "frontend", "src", "views", "Pedidos", "ConciliarFacturaView.vue"), encoding="utf-8").read()
mod = open(os.path.join(RAIZ, "frontend", "src", "views", "Pedidos", "components", "ConfirmarDiferenciasPrecio.vue"), encoding="utf-8").read()
check("pantalla: el modal muestra la lista, pide motivo opcional y tiene «Confirmo las diferencias» y «Volver sin registrar»",
      "Confirmo las diferencias" in mod and "Motivo (opcional)" in mod and "Volver sin registrar" in mod)
check("pantalla Ingesta: manda la bonificación, abre el modal con el 409 y reenvía con la confirmación y el motivo",
      ing.count("bonificacion: item.bonificacion") == 2 and "detail?.codigo === 'DIFERENCIA_DE_PRECIO'" in ing
      and "confirmar_diferencias_precio: true, motivo_diferencias_precio" in ing and "<ConfirmarDiferenciasPrecio" in ing)
check("pantalla Conciliar contra PR: con diferencias de precio, abre el modal antes de registrar y reenvía con la confirmación",
      "d.tipo === 'PRECIO'" in con and "confirmar_diferencias_precio: true" in con and "<ConfirmarDiferenciasPrecio" in con)
check("pantallas: un clic no cuenta como confirmación (el botón llama confirmar() sin el evento y la función solo acepta { motivo }); lo encontró la prueba en el banco",
      '@click="confirmar()"' in con and '@click="confirmar"' not in con
      and con.count("'motivo' in confirmacionPrecios") == 1 and ing.count("'motivo' in confirmacionPrecios") == 1)

del cli; eng.dispose()
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
