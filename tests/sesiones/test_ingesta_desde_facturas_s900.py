r"""S900, Card #213 (Carlos 04/11: «el sistema Facturas debería tener un branch al viejo sistema de ingesta, de manera que si el operador ingesta una factura y necesita crear remito y crear pedido, sea una alternativa más
desde el menú de Facturas, y es solo invocar el sistema viejo que ya está ok, procesa y vuelve a Facturas»; «caminos paralelos suman, no restan»). En «Subidas sin terminar» cada factura tiene un botón «Crear pedido y remito» que
abre la Ingesta de siempre CON ESA FACTURA YA SUBIDA (?rawId=…&volver=facturas), sin volver a subir el PDF; la Ingesta la analiza (el mismo código que al subir un PDF, ahora en `analizarRaw`) y, al aprobar la factura o dejarla en
cuarentena, vuelve a Facturas. La marca «volver a Facturas» viaja en el store de pedidos y sobrevive al desvío por el PedidoCanvas (crear el pedido). Parte de servidor: sin cambios; se prueba que el preview de una subida anterior
(PDF real de ARCA, copia de P del 04/11 16:28) entrega lo mismo que al subirla y no cambia nada. Parte de pantalla: prueba estática y compilación con @vue/compiler-sfc (Node)."""
import sys, os, sqlite3, subprocess, hashlib, json, glob
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261104_1628.db"
ARCA = r"Q:\Mi unidad\V5_Silo_Claude\FACTURAS_PDF\ARCA"
T = os.path.join(RAIZ, "scratch", "test_ingesta_desde_facturas_tmp.db"); copiar_p(ORIG, T)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
def huella(sql, *a): return hashlib.md5(repr(q(sql, *a)).encode("utf-8")).hexdigest()
env = dict(os.environ, DATABASE_URL="sqlite:///" + T, PYTHONIOENCODING="utf-8")
subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_078_facturas_no_se_cargan.py")], capture_output=True, text=True, encoding="utf-8", env=env)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp_213"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)

# ---------- servidor: el preview de una subida anterior ----------
p0 = cli.get("/ingesta/facturas/panorama").json()
s2612 = [s for s in p0["sin_terminar"] if s["numero"] == 2612][0]
h_antes = (huella("select id, audit_status, flags_estado from ingesta_facturas_raw order by id"), huella("select * from facturas order by id"), huella("select * from pedidos order by id"), huella("select * from remitos order by id"))
r = cli.get(f"/ingesta/raw/{s2612['raw_id']}/preview")
j = r.json() if r.status_code == 200 else {}
check("el preview de una factura YA subida (la 2612, subida antes y sin terminar) responde 200 con lo mismo que da al subirla: datos leídos del PDF (número, cliente, ítems) y el audit_log del Conserje",
      r.status_code == 200 and str((j.get("parsed_data") or {}).get("factura", {}).get("numero", "")).endswith("2612") and len((j.get("parsed_data") or {}).get("items", [])) >= 1 and isinstance(j.get("audit_log"), dict))
check("el preview es de solo lectura: la subida sigue RECIBIDA y no cambian las subidas, facturas, pedidos ni remitos (la Ingesta clásica recién escribe al aprobar)",
      (huella("select id, audit_status, flags_estado from ingesta_facturas_raw order by id"), huella("select * from facturas order by id"), huella("select * from pedidos order by id"), huella("select * from remitos order by id")) == h_antes
      and q("select audit_status from ingesta_facturas_raw where id=?", s2612["raw_id"].replace("-", ""))[0][0] == "RECIBIDO")
check("el cliente de la 2612 (Medicient) se resuelve igual que al subir el PDF: el audit_log trae la resolución del cliente por CUIT",
      "client_resolution" in (j.get("audit_log") or {}) and (j["audit_log"]["client_resolution"] or {}).get("id"))
f2603 = glob.glob(os.path.join(ARCA, "30715603973_001_00001_00002603*.pdf"))
rr = cli.post("/ingesta/raw", files={"file": (os.path.basename(f2603[0]), open(f2603[0], "rb").read(), "application/pdf")}) if f2603 else None
rid = rr.json()["id"] if rr is not None and rr.status_code == 200 else None
rp = cli.get(f"/ingesta/raw/{rid}/preview") if rid else None
check("una factura sin pedido en V5 (la 2603 de Doc Baires, recién subida) también se abre: preview 200, cliente conocido y los ítems de ARCA (6 Surgizime E2 bidón x 5 L)",
      rp is not None and rp.status_code == 200 and (rp.json()["parsed_data"]["cliente"]["razon_social"] or "").upper().startswith("DOC BAIRES")
      and any("Surgizime" in (i.get("descripcion") or "") and float(i.get("cantidad")) == 6 for i in rp.json()["parsed_data"]["items"]))

# ---------- pantallas ----------
SRC = os.path.join(RAIZ, "frontend", "src")
leer = lambda *pth: open(os.path.join(SRC, *pth), encoding="utf-8").read().replace("\r\n", "\n")
ing, fac, sto = leer("views", "Pedidos", "IngestaFacturaView.vue"), leer("views", "Facturas", "FacturasView.vue"), leer("stores", "pedidos.js")
check("Facturas: cada línea de «Subidas sin terminar» tiene «Crear pedido y remito», que abre la Ingesta clásica con la factura ya subida y la marca de procedencia (?rawId=…&volver=facturas), al lado de «Seguir» y «Ver PDF»",
      'data-test="ingesta-clasica"' in fac and "name: 'IngestaFactura', query: { rawId: s.raw_id, volver: 'facturas' }" in fac and "Crear pedido y remito" in fac
      and fac.index('data-test="seguir"') < fac.index('data-test="ingesta-clasica"') < fac.index('data-test="pdf-sin-terminar"'))
check("el botón solo aparece para facturas con número legible (no para notas de crédito o débito, que se concilian, ni para un PDF que no se pudo leer)",
      "const puedeIngestaClasica = (s) => !!s.tipo && s.tipo.startsWith('FACTURA') && s.numero != null" in fac and 'v-if="puedeIngestaClasica(s)"' in fac)
check("Ingesta clásica: el análisis posterior a la subida (preview, resolución del cliente, domicilios, pedidos pendientes) vive en analizarRaw(rawId); la subida de un PDF sigue igual (sube, avisa duplicados y llama a analizarRaw)",
      "const analizarRaw = async (rawId) => {" in ing and "await ingestaService.getPreview(rawId);" in ing[ing.index("const analizarRaw"):ing.index("const cargarRawExistente")]
      and all(x in ing[ing.index("const processFile"):ing.index("const processFile") + 1800] for x in ("await ingestaService.uploadRaw(formData);", "dup.encontrado", "await analizarRaw(rawId);")))
check("la Ingesta abre una factura ya subida SIN pedir el PDF: con ?rawId (y sin contexto de un desvío anterior) llama a cargarRawExistente, que fija el raw y la analiza",
      "const cargarRawExistente = async (rawId) => {" in ing and "currentRawId.value = rawId;\n        await analizarRaw(rawId);" in ing
      and "} else if (route.query.rawId) {" in ing and "await cargarRawExistente(String(route.query.rawId));" in ing)
check("al terminar vuelve a Facturas: aprobar (Ingesta procesada) y dejar en cuarentena terminan con terminarYVolver(), que limpia la marca y va a FacturasPanel solo si se llegó desde Facturas",
      "const terminarYVolver = () => {" in ing and "router.push({ name: 'FacturasPanel' });" in ing[ing.index("const terminarYVolver"):ing.index("const reset = ")]
      and ing[ing.index("Ingesta Procesada y Sellada (Bit 22)"):ing.index("Ingesta Procesada y Sellada (Bit 22)") + 900].count("terminarYVolver();") == 1
      and ing[ing.index("Remito en cuarentena generado"):ing.index("Remito en cuarentena generado") + 500].count("terminarYVolver();") == 1)
check("la marca sobrevive al desvío por el PedidoCanvas (crear el pedido): se guarda en el store (ingestaVolverA), se recupera al volver con el contexto del desvío y se limpia al irse a cualquier otra pantalla o al volver a entrar sin marca",
      "ingestaVolverA: null" in sto and "volverAFacturas.value = route.query.volver === 'facturas' || (!!pedidosStore.pending409Context && pedidosStore.ingestaVolverA === 'facturas');" in ing
      and "pedidosStore.ingestaVolverA = volverAFacturas.value ? 'facturas' : null;" in ing and "pedidosStore.ingestaVolverA = null;   // [S899, Card #213]" in ing)
check("la Ingesta muestra «Volver a Facturas» en el encabezado solo si se llegó desde Facturas; sin la marca la pantalla es la de siempre (sin botón y sin cambio de destino al aprobar)",
      'v-if="volverAFacturas"' in ing and 'data-test="volver-a-facturas-ingesta"' in ing and "if (volverAFacturas.value) {" in ing[ing.index("const terminarYVolver"):ing.index("const reset = ")])
check("lo demás de la Ingesta clásica no se toca: handleProceder, el desvío al PedidoCanvas (goToNewPedido / goToVincularPedido), el payload de aprobar y «Descartar» (reset) siguen",
      all(x in ing for x in ("const handleProceder = () => {", "const goToNewPedido = () => {", "const goToVincularPedido = () => {", "ingestaService.approve(currentRawId.value, payload)", "pedidosStore.set409Context({"))
      and ing.count("reset();") >= 2)
js = ("const fs = require('fs'); const { createRequire } = require('module'); const req = createRequire('C:/dev/Sonido_Liquido_V5/frontend/package.json');"
      "const { parse, compileTemplate, compileScript } = req('@vue/compiler-sfc'); const out = {};"
      "for (const f of ['Pedidos/IngestaFacturaView', 'Facturas/FacturasView']) { const src = fs.readFileSync('C:/dev/Sonido_Liquido_V5/frontend/src/views/' + f + '.vue', 'utf8');"
      "const { descriptor, errors } = parse(src, { filename: f }); let n = errors.length; if (!n) { n += compileTemplate({ source: descriptor.template.content, filename: f, id: 'x' }).errors.length; compileScript(descriptor, { id: 'x' }); } out[f] = n }"
      "console.log(JSON.stringify(out))")
try:
    rc = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", timeout=120)
    res = json.loads(rc.stdout.strip())
except (OSError, ValueError, subprocess.SubprocessError):
    res = {}
check("las dos pantallas compilan (parseo, plantilla y script) sin errores", res == {"Pedidos/IngestaFacturaView": 0, "Facturas/FacturasView": 0})

for n in os.listdir(os.path.join(RAIZ, "scratch")):
    if n.startswith("test_ingesta_desde_facturas_tmp"):
        try: os.remove(os.path.join(RAIZ, "scratch", n))
        except OSError: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
