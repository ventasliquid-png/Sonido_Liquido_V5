r"""Card #164 (S882): la ingesta (POST /ingesta/raw/{id}/approve -> MODO ESPEJO) guarda la factura con los datos del PDF de ARCA y el remito con lo facturado.
Sobre una COPIA de la base de P de las 16:21 (con las migraciones 051-058 ya aplicadas)."""
import sys, os, shutil, sqlite3, glob, json, uuid
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from backend.pedidos.cantidades import facturado_por_renglon
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_*.db"))[-1]
T = os.path.join(RAIZ, "scratch", "test_ingesta_tmp.db"); copiar_p(ORIG, T)
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
def fact_renglon(i):
    s = S(); v = facturado_por_renglon(s, [i]).get(i, (0.0, 0.0)); s.close(); return v

# ---- datos de partida: pedido #82 (Poblet, OC 3502): veterinarios 200 pedidos / 100 remitidos, guantes ya entregados
cliente_id = q("select cliente_id from pedidos where id=82")[0][0]
cuit = q("select cuit from clientes where id=?", cliente_id)[0][0]
vet = q("select id, producto_id, cantidad from pedidos_items where id=181")[0]
prod_vet, prod_l = vet[1], q("select producto_id from pedidos_items where id=180")[0][0]
check("partida: #82 con 200 veterinarios pedidos, 100 ya remitidos y guantes L y M entregados por completo",
      vet[2] == 200.0 and q("select coalesce(sum(cantidad_remitida),0) from remitos_items ri join remitos r on r.id=ri.remito_id and r.estado!='ANULADO' where ri.pedido_item_id=181")[0][0] == 100.0)

def raw(parsed, nombre="test.pdf"):
    rid = uuid.uuid4().hex
    con = sqlite3.connect(T)
    con.execute("insert into ingesta_facturas_raw (id, filename, pdf_bytes, audit_status, parsed_data_raw, flags_estado, created_at) values (?, ?, ?, 'RECIBIDO', ?, 0, datetime('now'))",
                (rid, nombre, b"%PDF-1.4", json.dumps(parsed)))
    con.commit(); con.close(); return rid

def parsed_pdf(numero, cae, vto, items, neto, total, tipo="FACTURA_A", fecha="2026-10-08", con_fiscales=True):
    f = {"numero": numero, "cae": cae, "vto_cae": vto}
    if con_fiscales: f.update({"codigo_afip": "01", "tipo_comprobante": tipo, "fecha_emision": fecha, "total_neto": neto, "total_final": total})
    return {"cliente": {"cuit": cuit}, "factura": f, "items": items}

def payload(numero, cae, vto, items, modo, pedido, **extra):
    """Lo que manda la pantalla (IngestaFacturaView.vue): solo numero, CAE y vencimiento; sin tipo, fecha ni importes."""
    p = {"cliente": {"id": cliente_id, "cuit": cuit, "razon_social": "LACTEOS DE POBLET SA"}, "factura": {"numero": numero, "cae": cae, "vto_cae": vto},
         "items": items, "bultos": 1, "valor_declarado": 0.0, "modo_ingesta": modo, "pedido_id_vinculado": pedido}
    p.update(extra); return p

ITEM_VET60 = {"descripcion": "GUANTES VETERINARIOS 90 CM BOLSA X 100 UN", "cantidad": 60.0, "precio_unitario": 9750.0, "producto_id": prod_vet}

# ---------- A) VINCULAR_EXISTENTE: factura parcial de 60 veterinarios sobre el #82 ----------
neto = 60 * 9750.0
rid = raw(parsed_pdf("00001-00002999", "86416772099991", "2026-10-18", [{"descripcion": ITEM_VET60["descripcion"], "cantidad": 60.0, "precio_unitario": 9750.0, "subtotal": neto, "alicuota_iva": 21.0}], neto, round(neto * 1.21, 2)))
r = cli.post(f"/ingesta/raw/{rid}/approve", json=payload("00001-00002999", "86416772099991", "18/10/2026", [ITEM_VET60], "VINCULAR_EXISTENTE", 82))
check(f"A: la ingesta aprueba [{r.status_code}] {r.text[:120] if r.status_code != 200 else ''}", r.status_code == 200)
f = q("select id, tipo_comprobante, estado, fecha_emision, neto_gravado, iva_21, total, cae_vencimiento, flags_estado, pedido_id from facturas where numero_comprobante=2999")
check(f"A: factura espejo = lo que dice el PDF: Factura A, AUTORIZADA_AFIP, fecha 08/10 (no la de carga), neto 585.000 + IVA 122.850 = total 707.850, vencimiento 18/10 {f[0][1:8] if f else None}",
      f and f[0][1] == "FACTURA_A" and f[0][2] == "AUTORIZADA_AFIP" and f[0][3] == "2026-10-08" and abs(f[0][4] - 585000) < .01 and abs(f[0][5] - 122850) < .01 and abs(f[0][6] - 707850) < .01 and f[0][7] == "2026-10-18")
fi = q("select fi.pedido_item_id, fi.remito_item_id, fi.cantidad from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=2999")
check(f"A: el renglon de la factura queda enlazado al renglon #181 del pedido y al renglon del remito {fi}", len(fi) == 1 and fi[0][0] == 181 and fi[0][1] is not None and fi[0][2] == 60.0)
ri = q("select ri.pedido_item_id, ri.cantidad_remitida, ri.cantidad_declarada from remitos_items ri join remitos r on r.id=ri.remito_id join facturas_remitos fr on fr.remito_id=r.id join facturas f on f.id=fr.factura_id where f.numero_comprobante=2999")
check(f"A: el remito espejo lleva SOLO el renglon facturado, con 60 (la factura), no los 200 del pedido ni los guantes ya entregados {ri}", ri == [(181, 60.0, 60.0)])
check(f"A: ahora cuenta como facturado en el renglon: 100 (2577) + 60 = {fact_renglon(181)[0]:g}", fact_renglon(181) == (160.0, 0.0))
check("A: la factura espejo ya no queda en BORRADOR con CAE (nada para corregir despues)", q("select count(*) from facturas where numero_comprobante=2999 and estado='BORRADOR'")[0][0] == 0)

# ---------- B) sin los datos fiscales en el raw (ingesta con parser viejo): se infiere como antes, pero el estado sigue el CAE ----------
rid = raw(parsed_pdf("00001-00002998", "86416772099992", "2026-10-18", [], 0, 0, con_fiscales=False))
it30 = dict(ITEM_VET60, cantidad=15.0)
r = cli.post(f"/ingesta/raw/{rid}/approve", json=payload("00001-00002998", "86416772099992", "18/10/2026", [it30], "VINCULAR_EXISTENTE", 82, valor_declarado=0.0, cliente={"id": cliente_id, "cuit": cuit, "razon_social": "X", "condicion_iva": "RESPONSABLE INSCRIPTO"}))
f = q("select tipo_comprobante, estado, total from facturas where numero_comprobante=2998")
check(f"B: sin datos del parser: tipo por condicion de IVA (Responsable Inscripto -> Factura A), estado AUTORIZADA por tener CAE, total = suma de los renglones como antes (15 x 9.750) [{r.status_code}] {f}",
      r.status_code == 200 and f and f[0][0] == "FACTURA_A" and f[0][1] == "AUTORIZADA_AFIP" and abs(f[0][2] - 146250.0) < .01)

# ---------- C) sin CAE: BORRADOR como antes ----------
rid = raw(parsed_pdf("00001-00002997", "", "", [], 0, 0, con_fiscales=False))
it10 = dict(ITEM_VET60, cantidad=10.0)
r = cli.post(f"/ingesta/raw/{rid}/approve", json=payload("00001-00002997", "", "", [it10], "VINCULAR_EXISTENTE", 82))
f = q("select estado, cae from facturas where numero_comprobante=2997")
check(f"C: sin CAE la factura espejo queda en BORRADOR como antes [{r.status_code}] {f}", r.status_code == 200 and f and f[0][0] == "BORRADOR" and not (f[0][1] or "").strip())

# ---------- D) el techo del pedido sigue funcionando (Card #125): 150 veterinarios contra 100 pendientes -> 409 ----------
rid = raw(parsed_pdf("00001-00002996", "86416772099993", "2026-10-18", [], 0, 0, con_fiscales=False))
nf0, nr0 = q("select count(*) from facturas")[0][0], q("select count(*) from remitos")[0][0]
r = cli.post(f"/ingesta/raw/{rid}/approve", json=payload("00001-00002996", "86416772099993", "18/10/2026", [dict(ITEM_VET60, cantidad=150.0)], "VINCULAR_EXISTENTE", 82))
check(f"D: 150 sobre 15 pendientes se rechaza con 409 y no deja nada [{r.status_code}]", r.status_code == 409 and "CANTIDAD_EXCEDE_PEDIDO" in r.text and q("select count(*) from facturas")[0][0] == nf0 and q("select count(*) from remitos")[0][0] == nr0)

# ---------- E) VINCULAR_PARCIAL (camino que ya usaba las cantidades de la factura) con datos fiscales ----------
neto = 10 * 9750.0
rid = raw(parsed_pdf("00001-00002995", "86416772099994", "2026-10-18", [{"descripcion": ITEM_VET60["descripcion"], "cantidad": 10.0, "precio_unitario": 9750.0, "subtotal": neto, "alicuota_iva": 21.0}], neto, round(neto * 1.21, 2)))
r = cli.post(f"/ingesta/raw/{rid}/approve", json=payload("00001-00002995", "86416772099994", "18/10/2026", [dict(ITEM_VET60, cantidad=10.0)], "VINCULAR_PARCIAL", 82))
f = q("select tipo_comprobante, estado, total from facturas where numero_comprobante=2995"); fi = q("select fi.pedido_item_id from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=2995")
check(f"E: VINCULAR_PARCIAL tambien guarda la factura con los datos del PDF y el renglon enlazado [{r.status_code}] {f} {fi}", r.status_code == 200 and f == [("FACTURA_A", "AUTORIZADA_AFIP", 117975.0)] and fi == [(181,)])

# ---------- F) cuarentena: pedido nuevo armado con la factura, renglon por renglon ----------
neto = 5 * 8950.0
rid = raw(parsed_pdf("00001-00002994", "86416772099995", "2026-10-18", [{"descripcion": "Guantes nitrilo talle L caja x 100", "cantidad": 5.0, "precio_unitario": 8950.0, "subtotal": neto, "alicuota_iva": 21.0}], neto, round(neto * 1.21, 2)))
p = payload("00001-00002994", "86416772099995", "18/10/2026", [{"descripcion": "Guantes nitrilo talle L caja x 100", "cantidad": 5.0, "precio_unitario": 8950.0}], None, None, modo_cuarentena=True)
r = cli.post(f"/ingesta/raw/{rid}/approve", json=p)
f = q("select f.tipo_comprobante, f.estado, f.total, fi.pedido_item_id from facturas f join facturas_items fi on fi.factura_id=f.id where f.numero_comprobante=2994")
check(f"F: cuarentena: factura autorizada con los datos del PDF y su renglon enlazado al renglon del pedido nuevo [{r.status_code}] {f}", r.status_code == 200 and f and f[0][:3] == ("FACTURA_A", "AUTORIZADA_AFIP", 54147.5) and f[0][3] is not None)

# ---------- G) lo ya guardado no se toca ----------
check("G: las facturas anteriores de la base no cambiaron de estado por esto (2576 sigue siendo la A de $589.875 en el #72)", q("select tipo_comprobante, estado, total from facturas where numero_comprobante=2576 and tipo_comprobante='FACTURA_A'") == [("FACTURA_A", "AUTORIZADA_AFIP", 589875.0)])
del cli; eng.dispose()
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
