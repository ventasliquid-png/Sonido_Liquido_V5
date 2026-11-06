r"""S901, hallazgo H27 de CA (auditoría de la S900; pedido de Carlos 06/11: «arrancá con H26 y H27»; la S901 lo dejó SIN COMITEAR a la espera del dictamen de Nike sobre qué fecha usan los informes).
Un pedido que nace de una factura tomaba la fecha de HOY (la 2603 del 16/09 quedó del 05/11 y la venta de septiembre figuraba en noviembre; de ahí el «duplicado… Similar: #155»). Ahora toma la fecha de la factura:
la pantalla del pedido (cuando viene de la Ingesta: allí nació el #155) y el pedido de cuarentena del servidor. Sobre una COPIA de la base de P del 05/11 10:21."""
import sys, os, re, json, uuid, sqlite3, subprocess
from datetime import datetime
from types import SimpleNamespace
from _esquema_p import copiar_p, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user, get_current_user_optional
from backend.remitos.service import RemitosService
import backend.pedidos.router as _pr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
APP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(_pr.__file__))))   # raíz del código que se está probando (D, o current/ del clon de B)
def leer(*partes): return open(os.path.join(APP, *partes), encoding="utf-8").read()

# ---------- el helper, sin base ----------
def payload_con(fecha): return SimpleNamespace(factura=SimpleNamespace(fecha_emision=fecha))
hoy = datetime.now()
f = RemitosService._fecha_del_pedido_de_la_factura
check("con la fecha de la factura (AAAA-MM-DD) el pedido toma esa fecha a las 00:00, igual que contra natura", f(payload_con("2026-09-16")) == datetime(2026, 9, 16, 0, 0))
check("tolera espacios y una hora pegada (2026-09-16 10:20:00)", f(payload_con(" 2026-09-16 10:20:00 ")) == datetime(2026, 9, 16, 0, 0))
check("sin fecha, con una fecha ilegible o con una fecha a futuro, la de hoy", all(abs((f(p) - hoy).total_seconds()) < 60 for p in (payload_con(None), payload_con(""), payload_con("16/09/2026"), payload_con("basura"), payload_con("2999-01-01"), SimpleNamespace())))
check("la factura de HOY da hoy a las 00:00", f(payload_con(hoy.strftime("%Y-%m-%d"))) == datetime(hoy.year, hoy.month, hoy.day))

# ---------- el camino de cuarentena de punta a punta (POST /ingesta/raw/{id}/approve con modo_cuarentena), con la factura de septiembre y una sin fecha ----------
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261105_1021.db"
T = os.path.join(RAIZ, "scratch", "test_fecha_pedido_factura_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "prueba"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U(); app.dependency_overrides[get_current_user_optional] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
_aparte = imagenes_aparte(APP); _aparte.__enter__()
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
cliente_id = q("select cliente_id from pedidos where id=82")[0][0]
cuit = q("select cuit from clientes where id=?", cliente_id)[0][0]
def raw(parsed):
    rid = uuid.uuid4().hex
    con = sqlite3.connect(T)
    con.execute("insert into ingesta_facturas_raw (id, filename, pdf_bytes, audit_status, parsed_data_raw, flags_estado, created_at) values (?, ?, ?, 'RECIBIDO', ?, 0, datetime('now'))", (rid, "test.pdf", b"%PDF-1.4", json.dumps(parsed)))
    con.commit(); con.close(); return rid
def cuarentena(numero, cae, fecha_pdf):
    neto = 5 * 8950.0
    fact = {"numero": numero, "cae": cae, "vto_cae": "2026-10-18"}
    if fecha_pdf: fact.update({"codigo_afip": "01", "tipo_comprobante": "FACTURA_A", "fecha_emision": fecha_pdf, "total_neto": neto, "total_final": round(neto * 1.21, 2)})
    rid = raw({"cliente": {"cuit": cuit}, "factura": fact, "items": [{"descripcion": "Guantes nitrilo talle L caja x 100", "cantidad": 5.0, "precio_unitario": 8950.0, "subtotal": neto, "alicuota_iva": 21.0}]})
    p = {"cliente": {"id": cliente_id, "cuit": cuit, "razon_social": "LACTEOS DE POBLET SA"}, "factura": {"numero": numero, "cae": cae, "vto_cae": "18/10/2026"},
         "items": [{"descripcion": "Guantes nitrilo talle L caja x 100", "cantidad": 5.0, "precio_unitario": 8950.0}], "bultos": 1, "valor_declarado": 0.0, "modo_cuarentena": True}
    return cli.post(f"/ingesta/raw/{rid}/approve", json=p)
nmax = q("select max(id) from pedidos")[0][0]
r = cuarentena("00001-00002941", "86416772099941", "2026-09-16")
nuevo = q("select id, fecha, origen, nota from pedidos where id > ? order by id limit 1", nmax)
check(f"cuarentena con la factura del 16/09: el pedido que nace queda del 16/09/2026 y no de hoy [{r.status_code}] {nuevo and nuevo[0][1]}", r.status_code == 200 and nuevo and str(nuevo[0][1]).startswith("2026-09-16") and nuevo[0][2] == "INGESTA_PDF")
nmax = q("select max(id) from pedidos")[0][0]
r = cuarentena("00001-00002942", "86416772099942", None)
nuevo = q("select id, fecha from pedidos where id > ? order by id limit 1", nmax)
check(f"cuarentena con una factura SIN fecha legible: la de hoy, como siempre [{r.status_code}]", r.status_code == 200 and nuevo and str(nuevo[0][1]).startswith(hoy.strftime("%Y-%m-%d")))
sv = leer("backend", "remitos", "service.py")
check("el pedido de cuarentena ya no se crea con datetime.now() sino con el helper de la fecha de la factura", "fecha=RemitosService._fecha_del_pedido_de_la_factura(payload)" in sv and "nota=f\"Ingesta en Cuarentena Factura: {original_invoice}\"" in sv
      and re.search(r"cliente_id=cliente\.id,\s*fecha=datetime\.now\(\),\s*nota=f\"Ingesta en Cuarentena", sv) is None)

# ---------- la pantalla del pedido (donde nació el #155): el pedido NUEVO que viene de la Ingesta toma la fecha de la factura ----------
can = leer("frontend", "src", "views", "Ventas", "PedidoCanvas.vue")
check("PedidoCanvas: un pedido NUEVO que viene de la Ingesta toma la fecha de la factura (ISO, que no sea futura; el casillero sigue editable), no el de hoy",
      "const fechaFactura = String(ingesta.factura?.fecha_emision || '').slice(0, 10);" in can
      and "if (!route.params.id && /^\\d{4}-\\d{2}-\\d{2}$/.test(fechaFactura) && fechaFactura <= getLocalDate()) fechaPedido.value = fechaFactura;" in can
      and can.index("const fechaFactura") < can.index("console.log('[PedidoCanvas] Ingesta data recibida:'"))
js = ("const fs = require('fs'); const { createRequire } = require('module'); const req = createRequire('C:/dev/Sonido_Liquido_V5/frontend/package.json');"
      "const { parse, compileTemplate, compileScript } = req('@vue/compiler-sfc'); const out = {}; const base = " + json.dumps(APP.replace("\\", "/")) + " + '/frontend/src/views/';"
      "for (const f of ['Ventas/PedidoCanvas']) { const src = fs.readFileSync(base + f + '.vue', 'utf8');"
      "const { descriptor, errors } = parse(src, { filename: f }); let n = errors.length; if (!n) { n += compileTemplate({ source: descriptor.template.content, filename: f, id: 'x' }).errors.length; compileScript(descriptor, { id: 'x' }); } out[f] = n }"
      "console.log(JSON.stringify(out))")
try:
    res_js = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", timeout=180).stdout.strip())
except (OSError, ValueError, subprocess.SubprocessError):
    res_js = {}
check("la pantalla del pedido compila sin errores", res_js == {"Ventas/PedidoCanvas": 0})

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
try: _aparte.__exit__(None, None, None)
except Exception: pass
del cli; eng.dispose()
try: os.remove(T)
except OSError: pass
sys.exit(1 if falla else 0)
