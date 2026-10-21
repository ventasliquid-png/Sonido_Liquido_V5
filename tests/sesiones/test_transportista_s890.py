r"""S890, paquete 1 de remitos, punto 2 (Carlos 21/10): el casillero TRANSPORTISTA del talonario 0015 (razón social, CUIT, domicilio) se llena desde el padrón de
transportes; sin empresa, dice el método («RETIRA EL CLIENTE»...). Y la web del transporte para PEDIR EL RETIRO (empresas_transporte.web_retiro, migrate_064): en el
padrón, en la API y en la ventana del remito como enlace y para copiar, con «Nuevo transporte» al lado.
(1) Papel, sobre una COPIA de P con migrate_065 aplicada (el 3031 con Cruz del Sur): cada dato cae dentro de su casillero. (2) Mostrador y remito viejo sin método.
(3) Un nombre larguísimo no invade el casillero de al lado. (4) API: la web de retiro se lee y se guarda. (5) Pantallas (estática)."""
import sys, os, shutil, sqlite3, glob, io, subprocess
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from backend.remitos.remito_engine import generar_remito_pdf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import fitz

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
MM = 72 / 25.4
ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_*.db"))[-1]
T = os.path.join(RAIZ, "scratch", "test_transportista_tmp.db"); copiar_p(ORIG, T)
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
r = subprocess.run([PY, "-X", "utf8", os.path.join(RAIZ, "scripts", "migrate_065_remito_3031_petroplastic.py")], capture_output=True, text=True, encoding="utf-8",
                   env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
check(f"setup: migrate_065 sobre la copia (el 3031 con Cruz del Sur) [rc {r.returncode}]", r.returncode == 0 and "OK" in r.stdout)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); x = con.execute(sql, a).fetchall(); con.commit(); con.close(); return x
def guid(h): h = h.replace("-", ""); return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"

import backend.remitos.router as _router
SALIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(_router.__file__)))), "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida")
RESP = os.path.join(RAIZ, "scratch", "test_transportista_resp"); os.makedirs(RESP, exist_ok=True)
tocados = ["remito_0015_00003031.pdf", "remito_0015_00003030.pdf", "remito_0015_00003027.pdf"]
for n in tocados:
    if os.path.exists(os.path.join(SALIDA, n)): shutil.copyfile(os.path.join(SALIDA, n), os.path.join(RESP, n))

CASILLEROS = {"razon_social": (68.0, 125.6, 242.0, 247.5), "cuit": (55.0, 125.6, 250.0, 255.5), "domicilio": (61.0, 125.6, 258.5, 264.0)}   # las letras de cada etiqueta: 243.3-245.7, 251.7-254.1 y 260.2-262.4 mm
def casilleros(pdf_bytes_o_ruta):
    doc = fitz.open(stream=pdf_bytes_o_ruta, filetype="pdf") if isinstance(pdf_bytes_o_ruta, bytes) else fitz.open(pdf_bytes_o_ruta)
    pag = doc[0]; out = {k: [] for k in CASILLEROS}; fuera = []
    for x0, y0, x1, y1, w, *_ in pag.get_text("words"):
        if 238 * MM <= y0 <= 265 * MM and x0 >= 54 * MM and x1 <= 140 * MM:
            dentro = False
            for k, (cx0, cx1, cy0, cy1) in CASILLEROS.items():
                if cx0 * MM - 0.5 <= x0 and x1 <= cx1 * MM and cy0 * MM <= y0 <= cy1 * MM:
                    out[k].append(w); dentro = True
            if not dentro: fuera.append((w, round(x0 / MM, 1), round(y0 / MM, 1)))
    return {k: " ".join(v) for k, v in out.items()}, fuera, " ".join(pag.get_text().split())

# ---- (1) el 3031 con Cruz del Sur
rid = q("select id from remitos where numero_legal='0015-00003031'")[0][0]
rp = cli.get(f"/remitos/{guid(rid)}/pdf")
cas, fuera, txt = casilleros(rp.content) if rp.status_code == 200 else ({}, [], "")
check(f"3031 [{rp.status_code}]: razón social del transportista en su casillero: {cas.get('razon_social')!r}", cas.get("razon_social") == "VICTOR MASSON TRANSPORTES CRUZ DEL SUR SA")
check(f"3031: CUIT con guiones en su casillero: {cas.get('cuit')!r}", cas.get("cuit") == "30-55656579-8")
check(f"3031: domicilio del transporte (su vínculo en el Address Hub) en su casillero: {cas.get('domicilio')!r}", cas.get("domicilio", "").upper().startswith("AV. JUAN DE GARAY 3212"))
check(f"3031: nada del transportista se sale de los casilleros {fuera}", not fuera)
check("3031: el resto del papel coincide con el que imprimió Celtrap (Ruta 234 Km 16, 20/10/2026, $ 2.980.000,00, 200 bultos)",
      "RUTA 234 KM. 16, JUNIN DE LOS ANDES" in txt and "20/10/2026" in txt and "$ 2.980.000,00" in txt and "BULTOS: 200" in txt)

# ---- (2) sin empresa: el método; sin método: en blanco
rid30 = q("select id from remitos where numero_legal='0015-00003030'")[0][0]
rp = cli.get(f"/remitos/{guid(rid30)}/pdf"); cas, fuera, _ = casilleros(rp.content)
check(f"3030 (mostrador, sin transporte) [{rp.status_code}]: el casillero dice «RETIRA EL CLIENTE» y nada más", cas == {"razon_social": "RETIRA EL CLIENTE", "cuit": "", "domicilio": ""} and not fuera)
rid27, met27, tr27 = q("select id, metodo_entrega, transporte_id from remitos where numero_legal='0015-00003027'")[0]
q("update remitos set transporte_id=NULL, metodo_entrega=NULL where id=?", rid27)
rp = cli.get(f"/remitos/{guid(rid27)}/pdf"); cas, fuera, _ = casilleros(rp.content)
check(f"remito viejo sin transporte ni método [{rp.status_code}]: el casillero queda en blanco", cas == {"razon_social": "", "cuit": "", "domicilio": ""} and not fuera)

# ---- (3) un nombre larguísimo no invade el casillero de al lado
p = os.path.join(RESP, "_largo.pdf")
generar_remito_pdf({"razon_social": "X", "cuit": "20000000001", "domicilio_fiscal": "Y", "condicion_iva": "RESPONSABLE INSCRIPTO", "referencia": "Pedido #1", "oc": "",
                    "transportista": {"razon_social": "EXPRESO INTERPROVINCIAL DE CARGAS GENERALES DEL NOROESTE ARGENTINO SOCIEDAD ANONIMA", "cuit": "30-12345678-9",
                                      "domicilio": "Avenida General Intendente Alvear de los Pueblos Unidos 12345 Piso 14 Dto B, Ciudad Autónoma de Buenos Aires (Capital Federal)"}},
                   [{"codigo": "", "descripcion": "Z", "cantidad": 1, "unidad": "UN"}], is_preview=False, output_path=p, numero_remito="0015-00009999")
cas, fuera, _ = casilleros(p)
check(f"nombre y domicilio larguísimos: se achican y se cortan, sin salirse del casillero (nada fuera: {fuera})", not fuera and cas["razon_social"].startswith("EXPRESO") and cas["domicilio"].upper().startswith("AVENIDA"))

# ---- (4) API: la web de retiro se lee y se guarda
cruz = q("select id from empresas_transporte where replace(cuit,'-','')='30556565798'")[0][0]
emps = cli.get("/logistica/empresas").json()
e = next((x for x in emps if x["id"].replace("-", "") == cruz.replace("-", "")), {})
check(f"GET /logistica/empresas devuelve web_retiro (la de Cruz del Sur, cargada por migrate_065): {e.get('web_retiro')!r}", e.get("web_retiro") == "https://www.cruzdelsur.com/herramientas_retiro.php")
alberto = q("select id from empresas_transporte where nombre='Alberto Imad'")[0][0]
r = cli.put(f"/logistica/empresas/{guid(alberto)}", json={"web_retiro": "https://ejemplo.invalid/retiro"})
check(f"PUT /logistica/empresas/{{id}} guarda web_retiro [{r.status_code}]", r.status_code == 200 and q("select web_retiro from empresas_transporte where id=?", alberto) == [("https://ejemplo.invalid/retiro",)])

# ---- (5) pantallas (estática)
split = io.open(os.path.join(RAIZ, "frontend", "src", "views", "Logistica", "LogisticaSplitter.vue"), encoding="utf-8").read()
canvas = io.open(os.path.join(RAIZ, "frontend", "src", "views", "Logistica", "components", "TransporteCanvas.vue"), encoding="utf-8").read()
check("ventana del remito: el título del recuadro del transporte es el enlace a su web de retiro (otra pestaña), con botón para copiarla",
      'data-enlace="web-retiro"' in split and ':href="urlWeb(transporteElegido.web_retiro)" target="_blank"' in split and "Pedir retiro en {{ transporteElegido.nombre }}" in split
      and 'data-accion="copiar-web-retiro"' in split and "navigator.clipboard.writeText(urlWeb(transporteElegido.value?.web_retiro))" in split)
check("ventana del remito: «Nuevo transporte» abre el padrón en otra pestaña y ↻ recarga la lista; sin web cargada, lo avisa",
      'data-accion="nuevo-transporte"' in split and "window.open(router.resolve({ name: 'Transportes' }).href, '_blank')" in split
      and 'data-accion="recargar-transportes"' in split and "Sin web para pedir el retiro" in split)
check("tarjeta del remito ya armado: enlace «Pedir retiro» si su transporte tiene web", 'data-enlace="web-retiro-remito"' in split and "webRetiroDe(remito.transporte_id)" in split)
check("padrón de transportes: campo «Web para pedir el retiro»", 'v-model="localModel.web_retiro"' in canvas and "Web para pedir el retiro" in canvas)

# ---- limpieza
del cli; eng.dispose()
for n in tocados:
    gen = os.path.join(SALIDA, n)
    if os.path.exists(os.path.join(RESP, n)): shutil.copyfile(os.path.join(RESP, n), gen)
    elif os.path.exists(gen): os.remove(gen)
shutil.rmtree(RESP, ignore_errors=True)
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
