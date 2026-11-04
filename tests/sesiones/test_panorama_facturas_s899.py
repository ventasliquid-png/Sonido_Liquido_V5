r"""S899, Card #212 (Carlos 04/11: «Tomy no sabe si ya ingestó, por ejemplo, la 2612… Deberías poner un Menú "Facturas" a la izquierda a nivel Remito o Pedido o Productos, para que desde ahí se acceda a ese listado y esos 3 botones»;
corte: «dale, desde la 2600»). La pantalla «Facturas» muestra qué facturas de ARCA están CARGADAS en V5, cuáles se SUBIERON SIN TERMINAR y cuáles FALTAN (huecos de la numeración); lo que se decidió no cargar a propósito
(2586 y la NC 74, decisión de Carlos 03/11) vive en la tabla `facturas_no_se_cargan` (migrate_078) y no cuenta como hueco. Sobre una COPIA de la base de P del 04/11 16:28 (con la 2612 y la 2622 subidas sin procesar,
la 2603 y la 2626 sin subir). Incluye la prueba estática del menú, la ruta y la pantalla, y su compilación con @vue/compiler-sfc (Node)."""
import sys, os, sqlite3, subprocess, hashlib, json, uuid
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
T = os.path.join(RAIZ, "scratch", "test_panorama_facturas_tmp.db"); copiar_p(ORIG, T)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
def x(sql, *a):
    con = sqlite3.connect(T); con.execute(sql, a); con.commit(); con.close()
def huella(sql, *a): return hashlib.md5(repr(q(sql, *a)).encode("utf-8")).hexdigest()

# ---------- migrate_078 ----------
def correr(db):
    env = dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_078_facturas_no_se_cargan.py")], capture_output=True, text=True, encoding="utf-8", env=env)
    return r.returncode, r.stdout
check("partida: la copia de P no tiene todavía la tabla de «no se cargan»",
      not q("select 1 from sqlite_master where name='facturas_no_se_cargan'"))
h_fac, h_raw, h_ped, h_rem = huella("select * from facturas order by id"), huella("select id, audit_status, filename from ingesta_facturas_raw order by id"), huella("select * from pedidos order by id"), huella("select * from remitos order by id")
rc, out = correr(T)
check(f"migrate_078 corre y sale 0 [{rc}]; crea la tabla, carga las dos decisiones de Carlos (2586 y la NC 74) y se registra",
      rc == 0 and out.count("OK --") == 2 and q("select count(*) from _migraciones_aplicadas where id='078_facturas_no_se_cargan'")[0][0] == 1
      and q("select tipo_comprobante, punto_venta, numero_comprobante from facturas_no_se_cargan order by numero_comprobante") == [("NOTA_CREDITO_A", 1, 74), ("FACTURA_A", 1, 2586)])
check("las dos marcas llevan el motivo y quién lo decidió (Carlos, 03/11)",
      all(m and "no se carga" in m.lower() and "Carlos" in (d or "") for m, d in q("select motivo, decidido_por from facturas_no_se_cargan")))
check("no toca facturas, subidas, pedidos ni remitos",
      huella("select * from facturas order by id") == h_fac and huella("select id, audit_status, filename from ingesta_facturas_raw order by id") == h_raw
      and huella("select * from pedidos order by id") == h_ped and huella("select * from remitos order by id") == h_rem)
rc2, out2 = correr(T)
check(f"idempotente: la segunda corrida se saltea por el registro [{rc2}] y no duplica", rc2 == 0 and "SKIP" in out2 and q("select count(*) from facturas_no_se_cargan")[0][0] == 2)
x("delete from _migraciones_aplicadas where id='078_facturas_no_se_cargan'")
rc3, out3 = correr(T)
check("sin el registro tampoco duplica (INSERT OR IGNORE sobre la clave única) y vuelve a registrarse", rc3 == 0 and out3.count("OK --") == 0 and q("select count(*) from facturas_no_se_cargan")[0][0] == 2
      and q("select count(*) from _migraciones_aplicadas where id='078_facturas_no_se_cargan'")[0][0] == 1)
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import auto_migrar
check("auto_migrar (el arranque de P) descubre la 078 con su nombre de archivo",
      dict(auto_migrar.migraciones_disponibles()).get("078_facturas_no_se_cargan", "").endswith("migrate_078_facturas_no_se_cargan.py"))

# ---------- el listado ----------
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp_facturas"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
def pano():
    r = cli.get("/ingesta/facturas/panorama"); assert r.status_code == 200, r.text; return r.json()
h_antes = (huella("select * from facturas order by id"), huella("select id, audit_status from ingesta_facturas_raw order by id"), huella("select * from facturas_no_se_cargan order by id"))
p = pano()
check("GET /ingesta/facturas/panorama no escribe nada (facturas, subidas y marcas idénticas)",
      (huella("select * from facturas order by id"), huella("select id, audit_status from ingesta_facturas_raw order by id"), huella("select * from facturas_no_se_cargan order by id")) == h_antes)
check("el corte es la 2600 para las facturas A (Carlos 04/11) y el primer número cargado desde el 08/09 para las notas de crédito (la 72)",
      {(c["tipo"], c["desde"]) for c in p["corte"]} == {("FACTURA_A", 2600), ("NOTA_CREDITO_A", 72)})
nums = lambda lista, tipo="FACTURA_A": sorted(e["numero"] for e in lista if e["tipo"] == tipo)
check("FALTAN: solo la 2603 (Doc Baires, 16/09, sin pedido) y la 2626 (Centro Pet; espera la salida del #151); NO la 2612 ni la 2622 (esas se subieron) ni la 2586 (marcada)",
      nums(p["faltan"]) == [2603, 2626] and not nums(p["faltan"], "NOTA_CREDITO_A"))
check("cada hueco dice entre qué facturas cargadas está: la 2603 entre la 2602 (14/09) y la 2604; la 2626 entre la 2625 (02/11) y la 2627 (04/11)",
      {h["numero"]: (h["anterior"]["numero"], h["anterior"]["fecha"], h["siguiente"]["numero"]) for h in p["faltan"]} == {2603: (2602, "2026-09-14", 2604), 2626: (2625, "2026-11-02", 2627)})
check("SUBIDAS SIN TERMINAR: la 2612 (Medicient, 198.682) y la 2622 (Piñeyro, 2.265.120), una sola vez cada una, en estado RECIBIDO «Subida, falta conciliar», con el raw para seguir",
      nums(p["sin_terminar"]) == [2612, 2622] and all(s["veces"] == 1 and s["estado"] == "RECIBIDO" and s["estado_texto"] == "Subida, falta conciliar" and s["raw_id"] for s in p["sin_terminar"])
      and {s["numero"]: s["total"] for s in p["sin_terminar"]} == {2612: 198682.0, 2622: 2265120.0})
check("las subidas repetidas de facturas que YA están cargadas (la 2621 ×3, la 2625, las de la 2600/2602/2608 y otras desde el corte) no cuentan: se informan aparte (12)",
      p["resumen"]["repetidas_ignoradas"] == 12 and not ({2621, 2625, 2600, 2602, 2608} & set(nums(p["sin_terminar"]))))
cg = {(c["tipo"], c["numero"]): c for c in p["cargadas"]}
check("CARGADAS: desde la 2600 (nada anterior, ningún presupuesto X), la más nueva arriba: la 2627 de Cynthia con el pedido #150 y el remito 0015-00003042",
      p["cargadas"][0]["numero"] == 2627 and p["cargadas"][0]["pedido_id"] == 150 and [r["numero_legal"] for r in p["cargadas"][0]["remitos"]] == ["0015-00003042"]
      and min(n for (t, n) in cg if t == "FACTURA_A") == 2600 and all(c["tipo"] != "PRESUPUESTO_X" for c in p["cargadas"]) and p["resumen"]["cargadas"] == 26)
check("las notas de crédito 72 y 73 (08/09) figuran como cargadas; la NC 74 (marcada «no se carga») no es hueco ni subida",
      ("NOTA_CREDITO_A", 72) in cg and ("NOTA_CREDITO_A", 73) in cg and not any(h["tipo"] == "NOTA_CREDITO_A" for h in p["faltan"]))
check("cada cargada con PDF trae el raw para «Ver PDF» (la 2625, la 2627); las que se registraron sin pasar por la subida (2607, 2613, NC 72 y 73) vienen sin raw",
      cg[("FACTURA_A", 2627)]["raw_id"] and cg[("FACTURA_A", 2625)]["raw_id"] and not any(cg[(t, n)]["raw_id"] for (t, n) in (("FACTURA_A", 2607), ("FACTURA_A", 2613), ("NOTA_CREDITO_A", 72), ("NOTA_CREDITO_A", 73))))
check("las 2625 y 2627 llevan el PDF de la subida PROCESADA (no el de una subida repetida)",
      all(q("select audit_status from ingesta_facturas_raw where id=?", cg[("FACTURA_A", n)]["raw_id"].replace("-", ""))[0][0] == "PROCESADO" for n in (2625, 2627)))
claves = [("c", c["tipo"], c["numero"]) for c in p["cargadas"]] + [("s", s["tipo"], s["numero"]) for s in p["sin_terminar"]] + [("f", f["tipo"], f["numero"]) for f in p["faltan"]]
check("cada número sale en UN solo lugar (cargadas, sin terminar o faltan): ninguna repetición entre listas",
      len({(t, n) for (_k, t, n) in claves}) == len(claves))
check("el resumen coincide con las listas (26 / 2 / 2 y 2 marcadas)",
      (p["resumen"]["cargadas"], p["resumen"]["sin_terminar"], p["resumen"]["faltan"], p["resumen"]["no_se_cargan"]) == (len(p["cargadas"]), len(p["sin_terminar"]), len(p["faltan"]), len(p["no_se_cargan"])) == (26, 2, 2, 2))

# ---------- marcar y deshacer ----------
body = lambda n, motivo="Factura de una OC que nunca se completó": {"tipo_comprobante": "FACTURA_A", "punto_venta": 1, "numero_comprobante": n, "motivo": motivo}
r = cli.post("/ingesta/facturas/no-se-carga", json=body(2603))
p2 = pano()
check("marcar la 2603 como «no se carga» (200): deja de ser hueco, aparece entre las marcadas con su motivo y quién la marcó",
      r.status_code == 200 and nums(p2["faltan"]) == [2626] and any(m["numero"] == 2603 and m["decidido_por"] == "tmp_facturas" and "OC" in m["motivo"] for m in p2["no_se_cargan"]) and p2["resumen"]["no_se_cargan"] == 3)
r_dup = cli.post("/ingesta/facturas/no-se-carga", json=body(2603))
check("marcar dos veces el mismo número es 409 YA_ESTA_MARCADA", r_dup.status_code == 409 and "YA_ESTA_MARCADA" in r_dup.text)
r_car = cli.post("/ingesta/facturas/no-se-carga", json=body(2627))
check("marcar una factura que YA está cargada es 409 YA_ESTA_CARGADA (no se puede esconder lo que está en V5)", r_car.status_code == 409 and "YA_ESTA_CARGADA" in r_car.text)
r_sm = cli.post("/ingesta/facturas/no-se-carga", json=body(2626, "   "))
check("sin motivo (o solo espacios) es 400 MOTIVO_REQUERIDO y no escribe", r_sm.status_code == 400 and "MOTIVO_REQUERIDO" in r_sm.text and nums(pano()["faltan"]) == [2626])
mid = [m["id"] for m in p2["no_se_cargan"] if m["numero"] == 2603][0]
r_del = cli.delete(f"/ingesta/facturas/no-se-carga/{mid}")
check("deshacer la marca (200): la 2603 vuelve a contar como faltante", r_del.status_code == 200 and nums(pano()["faltan"]) == [2603, 2626])
check("deshacer una marca que no existe es 404", cli.delete("/ingesta/facturas/no-se-carga/99999").status_code == 404)

# ---------- subidas nuevas ----------
def raw(numero, estado="RECIBIDO", filename=None, parsed="auto", cuando="datetime('now')"):
    rid = uuid.uuid4().hex
    if parsed == "auto":
        parsed = json.dumps({"cliente": {"razon_social": "CLIENTE DE PRUEBA", "cuit": "30111111111", "condicion_iva": "IVA Responsable Inscripto"},
                             "factura": {"numero": f"00001-{numero:08d}", "total_final": 1000.0, "fecha_emision": "2026-11-04"}, "items": []})
    con = sqlite3.connect(T)
    con.execute(f"insert into ingesta_facturas_raw (id, filename, pdf_bytes, audit_status, parsed_data_raw, flags_estado, created_at) values (?, ?, ?, ?, ?, 1, {cuando})",
                (rid, filename or f"30715603973_001_00001_{numero:08d} F CLIENTE.pdf", b"%PDF-1.4", estado, parsed))
    con.commit(); con.close(); return rid
raw(2629); raw(2629)
p3 = pano()
check("una factura nueva (la 2629) subida DOS veces y sin terminar: aparece UNA vez en «Subidas sin terminar» con «×2»; y como hay una posterior, la 2628 pasa a faltar",
      [s for s in p3["sin_terminar"] if s["numero"] == 2629][0]["veces"] == 2 and len([s for s in p3["sin_terminar"] if s["numero"] == 2629]) == 1 and 2628 in nums(p3["faltan"]))
raw(2630, estado="ERROR"); raw(2631, estado="PROCESANDO")
p4 = pano()
tx = {s["numero"]: s["estado_texto"] for s in p4["sin_terminar"]}
check("los estados se dicen en palabras: ERROR «Con error al leerla» y PROCESANDO «Quedó a medio camino»", tx.get(2630) == "Con error al leerla" and tx.get(2631) == "Quedó a medio camino")
raw(2640, filename="sin_formato_de_arca.pdf", parsed=None, estado="ERROR")
p5 = pano()
check("un PDF que no se pudo leer (sin número) no queda invisible: sale en «Subidas sin terminar» como «sin número legible»",
      any(s["numero"] is None and s["numero_legal"] == "sin número legible" for s in p5["sin_terminar"]))
x("delete from ingesta_facturas_raw where created_at >= datetime('now', '-1 minute')")
r_nc = raw(75, filename="30715603973_003_00001_00000075 NC CLIENTE.pdf",
           parsed=json.dumps({"cliente": {"razon_social": "CLIENTE", "cuit": "30111111111"}, "factura": {"numero": "00001-00000075", "clase_comprobante": "NOTA_CREDITO", "tipo_comprobante": "NOTA_CREDITO_A", "total_final": 500.0}, "items": []}))
p6 = pano()
check("una nota de crédito subida (la 75) se ubica en su serie propia (NOTA_CREDITO_A) y deja la 74 como marcada, no como hueco (la serie ya está cortada en la 72)",
      any(s["tipo"] == "NOTA_CREDITO_A" and s["numero"] == 75 for s in p6["sin_terminar"]) and not any(f["tipo"] == "NOTA_CREDITO_A" and f["numero"] == 74 for f in p6["faltan"]))
x("delete from ingesta_facturas_raw where id=?", r_nc)

# ---------- menú, ruta y pantalla ----------
SRC = os.path.join(RAIZ, "frontend", "src")
leer = lambda *pth: open(os.path.join(SRC, *pth), encoding="utf-8").read()
side, rut, vista, ing_svc = leer("components", "layout", "AppSidebar.vue"), leer("router", "index.js"), leer("views", "Facturas", "FacturasView.vue"), None
check("el menú tiene el grupo FACTURAS a la izquierda, al nivel de Pedidos, Remitos y Productos (entre Remitos y Productos), con «Facturas» y la Ingesta",
      'data-grupo="facturas"' in side and side.index('data-grupo="remitos"') < side.index('data-grupo="facturas"') < side.index("<!-- PRODUCTOS Group -->")
      and "navigate('FacturasPanel')" in side and "FACTURAS\n            </span>" in side.replace("\r\n", "\n"))
bloque_fact = side[side.index('data-grupo="facturas"'):side.index("<!-- PRODUCTOS Group -->")]
bloque_ped = side[side.index("<!-- PEDIDOS Group -->"):side.index("<!-- REMITOS Group")]
check("«Ingesta Facturas Propias» sigue en su lugar de siempre (Pedidos) Y también en el grupo Facturas: dos puertas a la misma pantalla (Carlos 04/11: «caminos paralelos suman, no restan»); la conciliación mantiene iluminado el grupo Facturas",
      "navigate('IngestaFactura')" in bloque_fact and "navigate('IngestaFactura')" in bloque_ped
      and "if (group === 'PEDIDOS') return ['PedidoList', 'TacticalLoader', 'IngestaFactura', 'FacturacionDashboard'].includes(route.name)" in side
      and "if (group === 'FACTURAS') return ['FacturasPanel', 'IngestaFactura', 'ConciliarFactura'].includes(route.name)" in side and "'INFORMES_REMITOS', 'FACTURAS']" in side)
check("la ruta /facturas (FacturasPanel) carga la pantalla nueva", "path: 'facturas'" in rut and "name: 'FacturasPanel'" in rut and "views/Facturas/FacturasView.vue" in rut)
check("la pantalla tiene los TRES botones (Cargadas, Subidas sin terminar, Faltan) con su cuenta, y el buscador por número o cliente",
      all(f'data-test="{t}"' in vista for t in ("boton-cargadas", "boton-sin-terminar", "boton-faltan", "cuenta-cargadas", "cuenta-sin-terminar", "cuenta-faltan", "buscar"))
      and "Subidas sin terminar" in vista and "Cargadas" in vista and "Faltan" in vista)
check("«Seguir» lleva a «Conciliar contra PR» de esa subida y «Ver PDF» abre el PDF original; «No se carga» pide el motivo y lo anota por el endpoint",
      "name: 'ConciliarFactura', params: { rawId: s.raw_id }" in vista and "`/ingesta/raw/${rawId}/pdf`" in vista and "api.post('/ingesta/facturas/no-se-carga'" in vista
      and 'data-test="motivo"' in vista and "api.delete(`/ingesta/facturas/no-se-carga/${m.id}`)" in vista)
check("el buscador salta solo al botón donde está lo que se busca (por número con o sin ceros, o por cliente)",
      "watch(filtro" in vista and "['sin_terminar', 'faltan', 'cargadas'].find" in vista and "digitos.replace(/^0+/, '')" in vista)
check("avisa el límite honesto: V5 no ve ARCA y los huecos se cuentan desde el corte", 'data-test="nota-limite"' in vista and "V5 no ve ARCA" in vista and "datos.corte" in vista)
js = ("const fs = require('fs'); const { createRequire } = require('module'); const req = createRequire('C:/dev/Sonido_Liquido_V5/frontend/package.json');"
      "const { parse, compileTemplate, compileScript } = req('@vue/compiler-sfc'); const out = {};"
      "for (const f of ['views/Facturas/FacturasView', 'components/layout/AppSidebar']) { const src = fs.readFileSync('C:/dev/Sonido_Liquido_V5/frontend/src/' + f + '.vue', 'utf8');"
      "const { descriptor, errors } = parse(src, { filename: f }); let n = errors.length; if (!n) { n += compileTemplate({ source: descriptor.template.content, filename: f, id: 'x' }).errors.length; compileScript(descriptor, { id: 'x' }); } out[f] = n }"
      "console.log(JSON.stringify(out))")
try:
    rr = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", timeout=120)
    res = json.loads(rr.stdout.strip())
except (OSError, ValueError, subprocess.SubprocessError):
    res = {}
check("la pantalla nueva y la barra lateral compilan (parseo, plantilla y script) sin errores", res == {"views/Facturas/FacturasView": 0, "components/layout/AppSidebar": 0})

for n in os.listdir(os.path.join(RAIZ, "scratch")):
    if n.startswith("test_panorama_facturas_tmp"):
        try: os.remove(os.path.join(RAIZ, "scratch", n))
        except OSError: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
