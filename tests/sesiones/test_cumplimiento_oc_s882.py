r"""Card #167 (S882): informe «Cumplimiento de OC» (GET /informes/cumplimiento-oc) y el Reporte de Entregas sin pedidos anulados.
Sobre una COPIA de la base de P del 08/10 con las migraciones 051-055 aplicadas."""
import sys, os, shutil, sqlite3, subprocess, glob, io, csv
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from backend.informes.router import _situacion_cumplimiento
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261008_1224.db"
T = os.path.join(RAIZ, "scratch", "test_cumpl_tmp.db"); copiar_p(ORIG, T)
for m in ("051_remitos_0016_al_pedido_de_su_factura", "052_facturas_con_cae_a_autorizada", "053_poblet_oc3476_facturas_2566_2576", "054_poblet_oc3502", "055_facturas_aceptadas_y_nc_cassara", "056_centropet_58_duplicado"):
    f = glob.glob(os.path.join(RAIZ, "scripts", f"migrate_{m[:3]}_*.py"))
    if not f: continue
    subprocess.run([sys.executable, f[0]], capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, DATABASE_URL="sqlite:///" + T, PYTHONIOENCODING="utf-8"))
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
c = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v

# --- la regla de situacion ---
check("situacion: 100/100/100 CERRADA; 100/50/50 FALTA ENTREGAR; 100/100/60 FALTA FACTURAR; 100/120/100 SOBRE-ENTREGADA; 100/100/120 SOBRE-FACTURADA; sin facturacion (Rosa) 100/100/None CERRADA",
      [_situacion_cumplimiento(100, 100, 100), _situacion_cumplimiento(100, 50, 50), _situacion_cumplimiento(100, 100, 60), _situacion_cumplimiento(100, 120, 100), _situacion_cumplimiento(100, 100, 120), _situacion_cumplimiento(100, 100, None)]
      == ["CERRADA", "FALTA ENTREGAR", "FALTA FACTURAR", "SOBRE-ENTREGADA", "SOBRE-FACTURADA", "CERRADA"])
check("situacion: lo de mas se muestra antes que lo que falta (120 entregadas y 50 facturadas -> SOBRE-ENTREGADA)", _situacion_cumplimiento(100, 120, 50) == "SOBRE-ENTREGADA")

# --- el informe sobre P ---
r = c.get("/informes/cumplimiento-oc")
d = r.json() if r.status_code == 200 else {}
filas = d.get("filas", [])
check(f"GET /informes/cumplimiento-oc responde [{r.status_code}] con {len(d.get('columnas', []))} columnas y {len(filas)} renglones", r.status_code == 200 and len(d.get("columnas", [])) == 13 and len(filas) > 20)
def fila(ped, prod_like):
    x = [f for f in filas if f["pedido_id"] == ped and prod_like.lower() in f["renglon"].lower()]
    return x[0] if len(x) == 1 else None
cof = fila(110, "cofia")
check(f"OC 3673 (#110): 4.000 cofias pedidas / 4.000 entregadas / 4.000 facturadas -> CERRADA, sin faltantes {cof and (cof['pedido'], cof['entregado'], cof['facturado'], cof['situacion'])}",
      cof and (cof["pedido"], cof["entregado"], cof["facturado"], cof["a_entregar"], cof["a_facturar"], cof["situacion"]) == (4000.0, 4000.0, 4000.0, 0.0, 0.0, "CERRADA"))
v72 = fila(72, "veterinarios")
check(f"OC 3476 (#72): 100 / 100 / 100 -> CERRADA (la 2566 y la 2576 suman 100; el remito erroneo de 100 esta anulado) {v72 and (v72['pedido'], v72['entregado'], v72['facturado'], v72['situacion'])}",
      v72 and (v72["pedido"], v72["entregado"], v72["facturado"], v72["situacion"]) == (100.0, 100.0, 100.0, "CERRADA"))
v98 = fila(98, "veterinarios")
check(f"OC 3596 (#98): 80 pedidas / 20 entregadas / 20 facturadas -> FALTA ENTREGAR, a entregar 60 y a facturar 60 {v98 and (v98['entregado'], v98['facturado'], v98['a_entregar'], v98['a_facturar'], v98['situacion'])}",
      v98 and (v98["entregado"], v98["facturado"], v98["a_entregar"], v98["a_facturar"], v98["situacion"]) == (20.0, 20.0, 60.0, 60.0, "FALTA ENTREGAR"))
v82 = fila(82, "veterinarios")
check(f"OC 3502 (#82): 200 pedidas / 100 entregadas (remito 0016-2577 ya con renglones) / 100 facturadas -> FALTA ENTREGAR 100 {v82 and (v82['pedido'], v82['entregado'], v82['facturado'], v82['a_entregar'], v82['situacion'])}",
      v82 and (v82["pedido"], v82["entregado"], v82["facturado"], v82["a_entregar"], v82["situacion"]) == (200.0, 100.0, 100.0, 100.0, "FALTA ENTREGAR"))
check("los pedidos anulados no aparecen (#83 y #97 de Poblet, #58 de Centro Pet)", not [f for f in filas if f["pedido_id"] in (83, 97, 58)])
b109 = [f for f in filas if f["pedido_id"] == 109]
check(f"OC del #109 (Cassara): 1.480 pedidas / facturado neto de NC 1.480 (1.500 - 20) -> no queda SOBRE-FACTURADA {[(f['facturado'], f['situacion']) for f in b109]}",
      b109 and all(f["facturado"] == 1480.0 for f in b109) and not any(f["situacion"] == "SOBRE-FACTURADA" for f in b109))
check("el informe solo trae pedidos con OC", all(f["oc"] for f in filas))
# --- filtros ---
r2 = c.get("/informes/cumplimiento-oc", params={"solo_abiertas": True}); ab = r2.json()["filas"]
check(f"solo_abiertas: saca las CERRADAS y deja el resto ({len(ab)} de {len(filas)}); la OC 3673 (cofias, cerrada) ya no esta",
      len(ab) < len(filas) and not any(f["situacion"] == "CERRADA" for f in ab) and not [f for f in ab if f["pedido_id"] == 110])
r3 = c.get("/informes/cumplimiento-oc", params={"oc": "3596"}); f3 = r3.json()["filas"]
check(f"filtro por OC '3596': solo el #98 ({len(f3)} renglones)", f3 and {f["pedido_id"] for f in f3} == {98})
cli = q("select p.cliente_id from pedidos p where p.id=98")[0][0]
r4 = c.get("/informes/cumplimiento-oc", params={"cliente_id": cli}); f4 = r4.json()["filas"]
check("filtro por cliente: solo Lacteos de Poblet", f4 and {f["cliente"] for f in f4} == {f3[0]["cliente"]})
# --- exportacion ---
for formato, tipo in (("csv", "text/csv"), ("excel", "spreadsheet"), ("pdf", "pdf"), ("txt", "text")):
    rx = c.get("/informes/cumplimiento-oc/export", params={"formato": formato, "solo_abiertas": True})
    check(f"export {formato}: responde [{rx.status_code}] y trae datos ({len(rx.content)} bytes, {rx.headers.get('content-type', '')[:40]})", rx.status_code == 200 and len(rx.content) > 500 and tipo in rx.headers.get("content-type", ""))
rcsv = c.get("/informes/cumplimiento-oc/export", params={"formato": "csv", "oc": "3596"}).content.decode("utf-8-sig")
filas_csv = list(csv.reader(io.StringIO(rcsv)))
check(f"el CSV lleva los encabezados y los numeros de la OC 3596 {filas_csv[0][:4]}...", filas_csv[0][:3] == ["Cliente", "OC", "Pedido"] and any("20.0" in row and "60.0" in row for row in filas_csv[1:]))
check("formato invalido -> 400", c.get("/informes/cumplimiento-oc/export", params={"formato": "xyz"}).status_code == 400)
# --- Reporte de Entregas: sin pedidos anulados ---
re_ = c.get("/remitos/entregas").json()
peds = {f["pedido_id"] for f in re_["filas"]}
check("Reporte de Entregas: ya no muestra los pedidos anulados (#58, #83, #97)", not ({58, 83, 97} & peds))
ocs_rep = [a for a in re_["anomalias"] if a["tipo"] == "OC_EN_VARIOS_PEDIDOS" and a["oc"] in ("3476", "3502")]
check(f"...y desaparecen las falsas 'OC en varios pedidos' de la 3476 y la 3502 {ocs_rep}", not ocs_rep)
con_anul = c.get("/remitos/entregas", params={"incluir_anulados": True}).json()
check("con incluir_anulados=true los pedidos anulados vuelven a verse", {58, 83, 97} <= {f["pedido_id"] for f in con_anul["filas"]})
# --- el pedido sin OC no se cuela ---
check("un pedido sin OC no aparece", not [f for f in filas if not (f.get("oc") or "").strip()])
del c; eng.dispose()
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
