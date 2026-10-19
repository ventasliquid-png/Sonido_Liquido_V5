"""Informe G -- renglones que salieron SIN SER VENTA FIRME (S876). Sobre una COPIA de la base migrada de P con
migrate_047 aplicada. Nunca toca bases vivas."""
import sys, os, shutil, io, gc, sqlite3, subprocess
from datetime import datetime, timedelta
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5"); os.chdir(r"C:\dev\Sonido_Liquido_V5")
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import fitz, openpyxl

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)

TMP = r"C:\dev\Sonido_Liquido_V5\scratch\test_informe_g_tmp.db"
shutil.copyfile(r"C:\dev\Sonido_Liquido_V5\scratch\pilot_v5x_P_migrada_pre047_20260930.db", TMP)
m = subprocess.run([sys.executable, r"scripts\migrate_047_remito_metodo_entrega_renglon_motivo.py"], env=dict(os.environ, DATABASE_URL="sqlite:///" + TMP), capture_output=True, text=True, encoding="utf-8", errors="replace")
assert m.returncode == 0, m.stdout + m.stderr
eng = create_engine(f"sqlite:///{TMP}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
c = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(TMP); v = con.execute(sql, a).fetchall(); con.close(); return v
def ejec(sql, *a):
    con = sqlite3.connect(TMP); con.execute(sql, a); con.commit(); con.close()
def h(u): return str(u).replace("-", "").lower()
def G(**p):
    r = c.get("/informes/renglones-no-facturables", params=p); assert r.status_code == 200, (p, r.status_code, r.text[:200]); return r.json()

LIBRES = """select p.id from pedidos p where p.id not in (select pedido_id from remitos where estado != 'ANULADO') and p.estado != 'ANULADO'
            and (select count(*) from pedidos_items i where i.pedido_id=p.id) >= 1 order by p.id"""
usados = set()
def libre():
    for (pid,) in q(LIBRES):
        if pid not in usados: usados.add(pid); return pid
    raise AssertionError("sin pedidos libres")
def pendientes(pid):
    j = c.get(f"/pedidos/{pid}").json(); return [(i["id"], i["cantidad"] - (i.get("cantidad_entregada") or 0)) for i in j["items"] if i["cantidad"] - (i.get("cantidad_entregada") or 0) > 0.001]
def consignar(motivo="CONSIGNACION", dias=0):
    pid = libre(); (pi, cant), = pendientes(pid)[:1]
    r = c.post("/remitos/armar", json={"pedido_id": pid, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": pi, "cantidad": cant, "motivo_no_facturable": motivo}]})
    assert r.status_code == 200, r.text
    j = r.json()
    if dias:
        viejo = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S.000000")
        ejec("update remitos set fecha_creacion=?, fecha_salida=NULL where id=?", viejo, h(j["id"]))
    return pid, pi, cant, j

check("arranca vacío: ningún renglón sin venta firme en la base", G()["resumen"]["total"] == 0 and G()["filas"] == [])

pA, piA, cantA, jA = consignar("CONSIGNACION", dias=0)
pB, piB, cantB, jB = consignar("MUESTRA_SIN_CARGO", dias=45)
pC, piC, cantC, jC = consignar("GARANTIA_REEMPLAZO", dias=30)
pD, piD, cantD, jD = consignar("CONSIGNACION", dias=29)
g = G(); f = g["filas"]
check(f"aparecen los 4 renglones abiertos [{len(f)}]", len(f) == 4 and g["resumen"]["total"] == 4)
check("orden: los más viejos primero (45, 30, 29, 0 días)", [x["antiguedad"] for x in f] == [45, 30, 29, 0])
check("alerta a los 30 días o más: 45 y 30 sí, 29 y 0 no", [x["en_alerta"] for x in f] == [True, True, False, False] and g["resumen"]["en_alerta"] == 2)
check("texto de alerta con los días; vacío si no hay alerta", f[0]["alerta"] == "ALERTA: 45 días sin resolver" and f[3]["alerta"] == "")
check("motivo legible y motivo de base", f[0]["motivo"] == "Muestra sin cargo" and f[0]["motivo_base"] == "MUESTRA_SIN_CARGO" and f[1]["motivo"] == "Garantía / reemplazo")
check("trae pedido, cliente, producto, cantidad, remito y cómo salió", f[0]["pedido_id"] == pB and f[0]["cliente"] and f[0]["producto"] and f[0]["cantidad"] == cantB and f[0]["remito"] == "(sin número)" and f[0]["entrega"] == "Mostrador")
check("trae el circuito del pedido (Blanco / Rosa)", all(x["circuito"] in ("Blanco", "Rosa") for x in f))
check("resumen por motivo: 2 consignaciones, 1 muestra, 1 garantía", {m["motivo"]: m["cantidad"] for m in g["resumen"]["por_motivo"]} == {"Consignación": 2, "Muestra sin cargo": 1, "Garantía / reemplazo": 1})
check("solo_alerta deja únicamente los de 30 días o más", [x["antiguedad"] for x in G(solo_alerta=True)["filas"]] == [45, 30])
check("filtro por motivo (también en minúsculas)", [x["pedido_id"] for x in G(motivo="CONSIGNACION")["filas"]] == [pD, pA] and len(G(motivo="muestra_sin_cargo")["filas"]) == 1)
cli = q("select cliente_id from pedidos where id=?", pB)[0][0]
check("filtro por cliente", {x["pedido_id"] for x in G(cliente_id=cli)["filas"]} >= {pB} and all(x["cliente"] == f[0]["cliente"] for x in G(cliente_id=cli)["filas"]))
check("motivo inválido -> 400", c.get("/informes/renglones-no-facturables", params={"motivo": "REGALO"}).status_code == 400)

# se cierran: facturar, devolver, anular
riB = q("select id from remitos_items where remito_id=?", h(jB["id"]))[0][0]
c.post(f"/remitos/items/{riB}/resolver-no-facturable", json={"accion": "FACTURAR"})
check("al resolver FACTURAR el renglón sale del informe", pB not in {x["pedido_id"] for x in G()["filas"]} and G()["resumen"]["total"] == 3)
r = c.post("/remitos/armar", json={"pedido_id": pC, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": piC, "cantidad": -cantC}]})
check(f"una devolución completa (PR de cantidad negativa) cierra el renglón: sale del informe [{r.status_code}]", r.status_code == 200 and pC not in {x["pedido_id"] for x in G()["filas"]} and G()["resumen"]["total"] == 2)
if cantD > 1:
    r = c.post("/remitos/armar", json={"pedido_id": pD, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": piD, "cantidad": -1}]})
    check("una devolución PARCIAL no lo cierra: sigue abierto", r.status_code == 200 and pD in {x["pedido_id"] for x in G()["filas"]})
else:
    check("(cantidad 1: no hay devolución parcial posible en este caso, se omite)", True)
ejec("update remitos set estado='ANULADO' where id=?", h(jA["id"]))
check("un remito ANULADO no figura", pA not in {x["pedido_id"] for x in G()["filas"]})

# exportaciones
consignar("CONSIGNACION", dias=40)
rx = c.get("/informes/renglones-no-facturables/export", params={"formato": "excel"}); ws = openpyxl.load_workbook(io.BytesIO(rx.content)).active
hdr = [x.value for x in ws[1]]
check(f"Excel: {ws.max_row - 1} fila(s) y las columnas del informe", rx.status_code == 200 and hdr == ["Pedido", "Circuito", "Cliente", "Producto", "Cantidad", "Motivo", "Remito", "Entrega", "Desde", "Días", "Alerta"] and ws.max_row - 1 == G()["resumen"]["total"])
rp = c.get("/informes/renglones-no-facturables/export", params={"formato": "pdf", "solo_alerta": "true"}); d = fitz.open(stream=rp.content, filetype="pdf")
t = " ".join(" ".join(p.get_text().split()) for p in d)
check(f"PDF: título, subtítulo con alerta a los 30 días y 'solo en alerta', y la marca ALERTA [{d.page_count} pág.]", rp.status_code == 200 and "Renglones sin venta firme" in t and "30 días" in t and "solo en alerta" in t and "ALERTA" in t)
check("CSV y TXT devuelven 200", c.get("/informes/renglones-no-facturables/export", params={"formato": "csv"}).status_code == 200 and c.get("/informes/renglones-no-facturables/export", params={"formato": "txt"}).status_code == 200)
check("formato inválido -> 400", c.get("/informes/renglones-no-facturables/export", params={"formato": "docx"}).status_code == 400)

del c; gc.collect(); eng.dispose()
try: os.remove(TMP)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
