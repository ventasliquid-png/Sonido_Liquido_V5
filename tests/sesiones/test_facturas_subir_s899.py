r"""S899 (Carlos 04/11: «ahora que hay una pantalla de facturas es más fácil: solo abrir las que faltan conciliar y agregar las que no están subidas… si es que están armados los caminos para que todo se maneje desde una misma pantalla»).
Cierra el circuito en la pantalla «Facturas»: (1) SUBIR los PDF desde ahí (botón o arrastrando, varios juntos) por POST /ingesta/raw, que solo guarda y lee el PDF: NO crea pedido, remito ni factura; las subidas quedan en «Subidas sin terminar»
y se avisa si el número ya estaba cargado o ya estaba subido; (2) «Seguir» marca de dónde se viene (?volver=facturas) y la conciliación, al terminar, vuelve a Facturas y ofrece seguir con la siguiente subida sin terminar (la de número más bajo).
Parte de servidor: PDF REALES de ARCA del reservorio del Silo (2603, 2612, 2625 y 2626) subidos por el endpoint sobre una COPIA de la base de P del 04/11 16:28. Parte de pantalla: prueba estática y compilación con @vue/compiler-sfc (Node)."""
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
T = os.path.join(RAIZ, "scratch", "test_facturas_subir_tmp.db"); copiar_p(ORIG, T)
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
class U: id = 1; username = "tmp_subir"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
pano = lambda: cli.get("/ingesta/facturas/panorama").json()

# ---------- servidor: subir PDF reales ----------
def pdf(n):
    f = glob.glob(os.path.join(ARCA, f"30715603973_001_00001_0000{n}*.pdf"))
    return f[0] if f else None
archivos = {n: pdf(n) for n in (2603, 2612, 2625, 2626)}
check("partida: los cuatro PDF reales de ARCA están en el reservorio del Silo", all(archivos.values()))
def subir(n):
    with open(archivos[n], "rb") as fh:
        r = cli.post("/ingesta/raw", files={"file": (os.path.basename(archivos[n]), fh.read(), "application/pdf")})
    return r, r.json()
p0 = pano()
check("partida (copia de P del 04/11): faltan la 2603 y la 2626; sin terminar la 2612 y la 2622; 12 repetidas ignoradas",
      sorted(f["numero"] for f in p0["faltan"]) == [2603, 2626] and sorted(s["numero"] for s in p0["sin_terminar"]) == [2612, 2622] and p0["resumen"]["repetidas_ignoradas"] == 12)
h0 = tuple(huella(f"select * from {t} order by id") for t in ("pedidos", "remitos", "facturas", "pedidos_items"))
r1, j1 = subir(2625)
check("subir una factura YA cargada (la 2625): 200 y el servidor avisa «duplicado.encontrado» con su pedido (#144); la pantalla lo dice «ya está cargada»",
      r1.status_code == 200 and j1["duplicado"]["encontrado"] is True and str(j1["duplicado"]["pedido_id"]) == "144" and j1["duplicado"]["numero_comprobante"] == 2625)
p1 = pano()
check("esa subida repetida no cuenta: la 2625 no aparece en «sin terminar» y suma una a las repetidas ignoradas (13)",
      2625 not in [s["numero"] for s in p1["sin_terminar"]] and p1["resumen"]["repetidas_ignoradas"] == 13)
r2, j2 = subir(2612)
p2 = pano()
s2612 = [s for s in p2["sin_terminar"] if s["numero"] == 2612]
check("subir de nuevo la 2612 (ya estaba subida sin terminar): una sola línea con «×2» y apuntando al raw recién subido (así la pantalla dice «ya estaba subida»)",
      r2.status_code == 200 and j2["duplicado"]["encontrado"] is False and len(s2612) == 1 and s2612[0]["veces"] == 2 and s2612[0]["raw_id"] == j2["id"])
r3, j3 = subir(2603)
r4, j4 = subir(2626)
p3 = pano()
nuevas = {s["numero"]: s for s in p3["sin_terminar"]}
check("subir la 2603 y la 2626 (las que faltaban): dejan de ser hueco y pasan a «Subidas sin terminar» (×1, estado RECIBIDO, con el raw recién subido); ya no falta ninguna",
      r3.status_code == 200 and r4.status_code == 200 and p3["faltan"] == [] and nuevas[2603]["raw_id"] == j3["id"] and nuevas[2626]["raw_id"] == j4["id"]
      and nuevas[2603]["veces"] == 1 and nuevas[2626]["veces"] == 1 and nuevas[2603]["estado"] == "RECIBIDO" and sorted(nuevas) == [2603, 2612, 2622, 2626])
check("el cliente de cada subida se lee del PDF (la pantalla lo muestra: Doc Baires, Centro Pet, Medicient)",
      "DOC BAIRES" in (nuevas[2603]["cliente"] or "").upper() and "CENTRO PET" in (nuevas[2626]["cliente"] or "").upper() and "MEDI CIENT" in (nuevas[2612]["cliente"] or "").upper())
check("subir PDF NO crea pedido, remito, factura ni renglones: solo guarda y lee (pedidos, remitos, facturas y pedidos_items idénticos)",
      tuple(huella(f"select * from {t} order by id") for t in ("pedidos", "remitos", "facturas", "pedidos_items")) == h0)
rc = cli.get(f"/ingesta/raw/{j2['id']}/conciliacion/candidatos")
c2612 = rc.json() if rc.status_code == 200 else {}
check("lo subido se puede seguir: los candidatos de la 2612 recién subida ofrecen el pedido #153 (remito 0015-00003035) con el total igual al de la factura",
      rc.status_code == 200 and any(str(x["pedido_id"]) == "153" and x["numero_legal"] == "0015-00003035" and abs((x["pedido_total"] or 0) - 198682.0) < 0.01 for x in c2612.get("prs", [])))
rp = cli.get(f"/ingesta/raw/{j3['id']}/pdf")
check("«Ver PDF» de lo recién subido entrega el PDF original", rp.status_code == 200 and rp.headers.get("content-type") == "application/pdf" and rp.content[:4] == b"%PDF")

# ---------- pantalla ----------
SRC = os.path.join(RAIZ, "frontend", "src", "views")
leer = lambda *pth: open(os.path.join(SRC, *pth), encoding="utf-8").read().replace("\r\n", "\n")
fac, con = leer("Facturas", "FacturasView.vue"), leer("Pedidos", "ConciliarFacturaView.vue")
check("el botón del encabezado sube PDF desde la pantalla: input oculto que acepta PDF y varios archivos; ya no manda a la Ingesta vieja",
      'type="file" accept="application/pdf,.pdf" multiple class="hidden" data-test="input-archivos"' in fac and 'data-test="subir-factura"' in fac and "name: 'IngestaFactura'" not in fac)
check("se pueden arrastrar los PDF sobre la pantalla (zona de soltar con el aviso de que no se crea pedido ni remito)",
      '@drop.prevent="alSoltar"' in fac and '@dragover.prevent="arrastrando = true"' in fac and 'data-test="zona-soltar"' in fac and "no se crea ningún pedido ni remito" in fac)
check("sube de a uno, en orden (for…of con await), solo por uploadRaw (POST /ingesta/raw): nunca /approve ni /preview, que son el camino viejo que crea pedido y remito",
      "for (const f of archivos)" in fac and "await ingestaService.uploadRaw(fd)" in fac and "/approve" not in fac and "/preview" not in fac and "modo_ingesta" not in fac)
check("ignora lo que no es PDF y cuenta el error de cada archivo sin cortar el resto",
      "const esPdf = (f)" in fac and "No es un PDF: se ignora." in fac and "No se pudo subir: " in fac)
check("al terminar relee el listado y dice por cada archivo: subida (falta conciliar), ya estaba subida (×N) o ya está cargada (pedido); pasa al botón «Subidas sin terminar»",
      "await cargar()" in fac and "Ya estaba subida (×${s.veces})" in fac and "Ya está cargada en V5" in fac and "Subida: falta conciliarla, apretá «Seguir»." in fac
      and "tab.value = 'sin_terminar'" in fac and 'data-test="resultado-subida"' in fac)
check("«Subir el PDF» de la pestaña Faltan abre el mismo selector de archivos (en vez de mandar a la Ingesta)", 'data-test="subirla"' in fac and '@click="elegirArchivos" data-test="subirla"' in fac)
check("«Seguir» lleva a Conciliar marcando de dónde viene (?volver=facturas)", "params: { rawId: s.raw_id }, query: { volver: 'facturas' }" in fac)
check("la conciliación, si viene de Facturas: el botón de arriba dice «Volver a Facturas»; al terminar ofrece volver y «Seguir con la siguiente» (la de número más bajo, con cuántas quedan)",
      "const vieneDeFacturas = route.query.volver === 'facturas'" in con and "vieneDeFacturas ? 'Volver a Facturas' : 'Volver a Ingesta'" in con
      and 'data-test="volver-a-facturas"' in con and 'data-test="seguir-con-la-siguiente"' in con and ".sort((a, b) => a.numero - b.numero)" in con
      and "api.get('/ingesta/facturas/panorama')" in con and "query: { volver: 'facturas' } })\"" in con)
check("sin ?volver (desde la Ingesta de siempre) nada cambia: «Volver a Ingesta» y sin botones nuevos; la siguiente se busca solo después de conciliar",
      "name: vieneDeFacturas ? 'FacturasPanel' : 'IngestaFactura'" in con and 'v-if="vieneDeFacturas" class="mt-3' in con and "if (!r || !vieneDeFacturas) return" in con)
js = ("const fs = require('fs'); const { createRequire } = require('module'); const req = createRequire('C:/dev/Sonido_Liquido_V5/frontend/package.json');"
      "const { parse, compileTemplate, compileScript } = req('@vue/compiler-sfc'); const out = {};"
      "for (const f of ['Facturas/FacturasView', 'Pedidos/ConciliarFacturaView']) { const src = fs.readFileSync('C:/dev/Sonido_Liquido_V5/frontend/src/views/' + f + '.vue', 'utf8');"
      "const { descriptor, errors } = parse(src, { filename: f }); let n = errors.length; if (!n) { n += compileTemplate({ source: descriptor.template.content, filename: f, id: 'x' }).errors.length; compileScript(descriptor, { id: 'x' }); } out[f] = n }"
      "console.log(JSON.stringify(out))")
try:
    rr = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", timeout=120)
    res = json.loads(rr.stdout.strip())
except (OSError, ValueError, subprocess.SubprocessError):
    res = {}
check("las dos pantallas compilan (parseo, plantilla y script) sin errores", res == {"Facturas/FacturasView": 0, "Pedidos/ConciliarFacturaView": 0})

for n in os.listdir(os.path.join(RAIZ, "scratch")):
    if n.startswith("test_facturas_subir_tmp"):
        try: os.remove(os.path.join(RAIZ, "scratch", n))
        except OSError: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
