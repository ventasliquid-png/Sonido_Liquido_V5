r"""S893, nodo Remitos (Carlos 26/10): la base de la ficha. (1) La OC se copia al remito (migrate_068 sobre los que ya existen; el evento del
modelo al crear uno nuevo; el papel la imprime del remito). (2) `GET /remitos/buscar` reconoce lo que se tipea: número («3031»,
«0015-3031», «0015-00003031»), pedido («#137»), OC y cliente (sin acentos). (3) `GET /remitos/ficha/{ref}` trae todo un remito por UUID o por
número, con la tabla del PR renglón por renglón, la historia y los vínculos; un número que existe en dos series da 409 con los candidatos.
Sobre una COPIA de P (la más nueva de BACKUPS_DB/PRODUCCION_P) con migrate_066 y migrate_068 aplicadas."""
import sys, os, shutil, sqlite3, glob, subprocess
from _esquema_p import asegurar_esquema, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
import fitz

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
# [S895] Fijada a la copia de P del 28/10 12:52, ANTERIOR al despliegue del paquete (Tomy relanzó a las 13:03): esta prueba corre migraciones sobre la copia de P
# y con una copia más nueva ya vienen aplicadas (SKIP). Mismo criterio que las de la S890 (auditoría de CA, 28/10).
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261028_1252.db"
TMP = os.path.join(RAIZ, "scratch", "test_ficha_busqueda_s893"); os.makedirs(TMP, exist_ok=True)
T = os.path.join(TMP, "P.db"); shutil.copyfile(ORIG, T)
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
def correr(nombre):
    return subprocess.run([PY, "-X", "utf8", os.path.join(RAIZ, "scripts", nombre)], capture_output=True, text=True, encoding="utf-8",
                          env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
r66 = correr("migrate_066_remitos_genoma_fecha_emision.py")
def q(sql, *a):
    con = sqlite3.connect(T); x = con.execute(sql, a).fetchall(); con.commit(); con.close(); return x
check(f"setup: copia de P con migrate_066 [rc {r66.returncode}]", r66.returncode == 0)

# ---- (1) la migración 068 sobre los remitos que ya existen
tiene_antes = "oc" in [c[1] for c in q("pragma table_info(remitos)")]
esperados = q("""select count(*) from remitos r join pedidos p on p.id=r.pedido_id where p.oc is not null and trim(p.oc) != ''""")[0][0]
antes = {i: tuple(x) for i, *x in q("select id, estado, numero_legal, flags_estado, fecha_salida, bultos from remitos")}
r68 = correr("migrate_068_remitos_oc.py")
check(f"migrate_068 sobre la copia de P [rc {r68.returncode}]: agrega remitos.oc y copia la OC de cada pedido ({esperados} remitos con OC en su pedido)",
      r68.returncode == 0 and not tiene_antes and "068_remitos_oc registrada" in r68.stdout)
con_oc = q("select count(*) from remitos where oc is not null and trim(oc) != ''")[0][0]
check(f"quedan {con_oc} remitos con OC, los {esperados} cuyo pedido la tiene", con_oc == esperados and esperados > 0)
dif = q("""select count(*) from remitos r join pedidos p on p.id=r.pedido_id where p.oc is not null and trim(p.oc) != '' and r.oc != trim(p.oc)""")[0][0]
check("la OC del remito es la de su pedido, sin espacios en las puntas", dif == 0)
sin = q("""select count(*) from remitos r join pedidos p on p.id=r.pedido_id where (p.oc is null or trim(p.oc) = '') and r.oc is not null""")[0][0]
check("los remitos de pedidos sin OC quedan en NULL", sin == 0)
despues = {i: tuple(x) for i, *x in q("select id, estado, numero_legal, flags_estado, fecha_salida, bultos from remitos")}
check("no toca estado, número, genoma, fechas ni bultos", antes == despues)
r2 = correr("migrate_068_remitos_oc.py")
check("idempotente: otra vez, SKIP", r2.returncode == 0 and "SKIP" in r2.stdout)
q("update remitos set oc='OC-MANUAL' where numero_legal='0015-00003027'")
q("delete from _migraciones_aplicadas where id='068_remitos_oc'")
correr("migrate_068_remitos_oc.py")
check("y no pisa una OC que el remito ya tiene", q("select oc from remitos where numero_legal='0015-00003027'")[0][0] == "OC-MANUAL")
asegurar_esquema(T)

from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
import backend.remitos.router as _router
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(_router.__file__))))
_aparte = imagenes_aparte(BASE); _aparte.__enter__()
SALIDA = os.path.join(BASE, "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida")
previos = set(os.listdir(SALIDA)) if os.path.isdir(SALIDA) else set()
def hx(x): return str(x).replace("-", "")
def rid(numero): return q("select id from remitos where numero_legal=?", numero)[0][0]
def buscar(txt, **kw): return cli.get("/remitos/buscar", params={"q": txt, **kw}).json()
def nums(res): return [x["numero_legal"] for x in res["resultados"]]

# ---- (2) la búsqueda
b = buscar("3031")
check(f"«3031» -> el 0015-00003031 es el exacto [{b['total']} resultado(s)]", hx(b["exacto"]) == rid("0015-00003031") and nums(b)[0] == "0015-00003031")
check("«0015-3031» y «0015-00003031» llegan al mismo remito", hx(buscar("0015-3031")["exacto"]) == hx(buscar("0015-00003031")["exacto"]) == rid("0015-00003031"))
b = buscar("303")
check(f"«303» trae el 3030 y el 3031 (número parcial), sin exacto {nums(b)[:3]}", {"0015-00003030", "0015-00003031"} <= set(nums(b)) and b["exacto"] is None)
b = buscar("#137")
check("«#137» trae los remitos del pedido 137 (el 3031 de Petroplastic)", "0015-00003031" in nums(b) and all("pedido" in x["coincide"] for x in b["resultados"]))
b = buscar("lacteos"); b2 = buscar("LÁCTEOS")
check(f"«lacteos» y «LÁCTEOS» traen los remitos de Lácteos de Poblet, sin acentos ({b['total']})",
      b["total"] > 0 and b["total"] == b2["total"] and all("Poblet" in x["razon_social"] for x in b["resultados"]))
oc_real, rem_oc = q("select oc, numero_legal from remitos where oc is not null and numero_legal is not null limit 1")[0]
b = buscar(oc_real)
check(f"la OC «{oc_real}» trae su remito {rem_oc}", rem_oc in nums(b) and any("OC" in x["coincide"] for x in b["resultados"]))
check("texto vacío -> sin resultados; texto que no existe -> sin resultados", buscar("")["total"] == 0 and buscar("xyzzy-nada")["total"] == 0)
b = buscar("2597", incluir_anulados=False)
check("incluir_anulados=false deja afuera los anulados", all(x["estado"] != "ANULADO" for x in b["resultados"]))
check("el remito con número mal formado de P (0016-00001-00002514) se encuentra por «2514»", "0016-00001-00002514" in nums(buscar("2514")))

# ---- (3) la ficha
r = cli.get("/remitos/ficha/3031")
f = r.json() if r.status_code == 200 else {}
check(f"ficha por número «3031» [{r.status_code}]: remito, pedido y cliente", r.status_code == 200 and f["remito"]["numero_legal"] == "0015-00003031"
      and f["pedido"]["id"] == 137 and "PETROPLASTIC" in f["cliente"]["razon_social"].upper())
check("la ficha es la misma por UUID, por «0015-3031» y por «0015-00003031»",
      all(hx(cli.get(f"/remitos/ficha/{x}").json()["remito"]["id"]) == rid("0015-00003031") for x in (rid("0015-00003031"), "0015-3031", "0015-00003031")))
check("genoma, transporte, bultos y valor del 3031 (los de la migración 065)", f["remito"]["genoma"]["clase"] == "EGRESO" and f["transporte"]["nombre"].upper().startswith("VICTOR MASSON")
      and f["remito"]["bultos"] == 200 and abs(f["remito"]["valor_declarado"] - 2980000.0) < 0.01)
it = f["items"][0]
check(f"la tabla del PR trae cada cantidad por renglón {sorted(it.keys())[:4]}...",
      all(k in it for k in ("impreso", "salio", "llego", "facturado", "acreditado", "pendiente_remitir", "pendiente_facturar", "pedido_cantidad", "producto")) and it["salio"] > 0)
check("la historia trae las notas, la última primero, con la de la migración 065", any("Remito alineado con el papel" in n["texto"] for n in f["notas"]))
check("«salió» del renglón no supera lo pedido y el pendiente por remitir cierra: pedido - entregado", all(abs(i["pendiente_remitir"] - max(0.0, i["pedido_cantidad"] - i["entregado_pedido"])) < 1e-9 for i in f["items"]))
r17 = cli.get("/remitos/ficha/0015-00003017").json()
check("un Rosa con 0015 (3017): la ficha dice pedido Rosa y el genoma lleva el IMPRESO o no según el papel", r17["pedido"]["rosa"] is True and r17["remito"]["numero_legal"] == "0015-00003017")
check("número que no existe -> 404", cli.get("/remitos/ficha/999999").status_code == 404 and cli.get("/remitos/ficha/abc").status_code == 404)
q("update remitos set numero_legal='0016-00003031' where numero_legal='0015-00003030'")
ra = cli.get("/remitos/ficha/3031")
check(f"«3031» en dos series -> 409 NUMERO_AMBIGUO con los candidatos [{ra.status_code}]", ra.status_code == 409 and "NUMERO_AMBIGUO" in ra.text and "0016-00003031" in ra.text and "0015-00003031" in ra.text)
check("con el punto de venta se resuelve: «0015-3031» y «0016-3031»", cli.get("/remitos/ficha/0015-3031").status_code == 200 and cli.get("/remitos/ficha/0016-3031").status_code == 200)

# ---- (4) un remito nuevo copia la OC del pedido y el papel la imprime
ped = q("""select p.id, pi.id, pi.cantidad - coalesce((select sum(ri.cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id
           where ri.pedido_item_id=pi.id and r.estado<>'ANULADO'),0) from pedidos p join pedidos_items pi on pi.pedido_id=p.id
           where p.estado='PENDIENTE' and (p.oc is null or trim(p.oc)='') order by p.id desc""")
ped = [x for x in ped if x[2] and x[2] > 0]
q("update pedidos set oc='  OC-S893-77  ' where id=?", ped[0][0])
r = cli.post("/remitos/armar", json={"pedido_id": ped[0][0], "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": ped[0][1], "cantidad": ped[0][2]}]})
nuevo = r.json()["id"] if r.status_code == 200 else ""
check(f"un remito nuevo copia la OC del pedido, sin espacios [{r.status_code}]: {q('select oc from remitos where id=?', nuevo.replace('-', ''))[0][0]!r}",
      q("select oc from remitos where id=?", nuevo.replace("-", ""))[0][0] == "OC-S893-77")
q("update pedidos set oc='OTRA-OC' where id=?", ped[0][0])
rp = cli.get(f"/remitos/{nuevo}/pdf")
txt = " ".join(fitz.open(stream=rp.content, filetype="pdf")[0].get_text().split()) if rp.status_code == 200 else ""
check(f"el papel imprime la OC DEL REMITO (la que se copió), aunque el pedido cambie después [{rp.status_code}]", "OC-S893-77" in txt and "OTRA-OC" not in txt)
r2p = next(x for x in ped if x[0] != ped[0][0])   # otro pedido, sin OC
r = cli.post("/remitos/armar", json={"pedido_id": r2p[0], "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": r2p[1], "cantidad": r2p[2]}]})
check("un remito de un pedido sin OC no inventa una", r.status_code == 200 and q("select oc from remitos where id=?", r.json()["id"].replace("-", ""))[0][0] is None)

# ---- limpieza
del cli; eng.dispose()
for n in (set(os.listdir(SALIDA)) - previos) if os.path.isdir(SALIDA) else []:
    os.remove(os.path.join(SALIDA, n))
_aparte.__exit__(None, None, None)
shutil.rmtree(TMP, ignore_errors=True)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
