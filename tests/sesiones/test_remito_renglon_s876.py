"""Confeccion de remitos y seguimiento a nivel renglon (S876, prompt 2026-09-30_NS_implementar_remito_renglon_S875).
Sobre una COPIA de la base migrada de P (datos reales) con migrate_047 aplicada. Nunca toca bases vivas."""
import sys, os, shutil, io, gc, re, sqlite3, subprocess
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5"); os.chdir(r"C:\dev\Sonido_Liquido_V5")
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import fitz
from datetime import datetime

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)

TMP = r"C:\dev\Sonido_Liquido_V5\scratch\test_remito_renglon_tmp.db"
copiar_p(r"C:\dev\Sonido_Liquido_V5\scratch\pilot_v5x_P_migrada_pre047_20260930.db", TMP)
m = subprocess.run([sys.executable, r"scripts\migrate_047_remito_metodo_entrega_renglon_motivo.py"],
                   env=dict(os.environ, DATABASE_URL="sqlite:///" + TMP), capture_output=True, text=True, encoding="utf-8", errors="replace")
assert m.returncode == 0 and "[migrate_047] OK" in m.stdout, m.stdout + m.stderr

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
def h(u): return str(u).replace("-", "").lower()
OFICINA = h("59b01b5a-e81a-4e2a-b496-9d65fef9262b")

LIBRES_SQL = """select p.id, (p.flags_estado & 4096) > 0 as rosa, p.transporte_id, p.domicilio_entrega_id,
    (select count(*) from pedidos_items i where i.pedido_id=p.id) as n, c.cuit
  from pedidos p join clientes c on c.id=p.cliente_id
  where p.id not in (select pedido_id from remitos where estado != 'ANULADO') and p.estado != 'ANULADO' order by p.id"""
usados = set()
def libre(rosa=False, transporte=None, dom=True, min_items=1, cuit=None):
    for pid, r, tr, dm, n, cu in q(LIBRES_SQL):
        if pid in usados: continue
        if bool(r) != rosa: continue
        if transporte is not None and bool(tr) != transporte: continue
        if dom is not None and bool(dm) != dom: continue
        if n < min_items: continue
        if cuit is not None and re.sub(r"\D", "", cu or "") != cuit: continue
        usados.add(pid); return pid
    raise AssertionError(f"no hay pedido libre rosa={rosa} transporte={transporte} dom={dom} items>={min_items} cuit={cuit}")
def pendientes(pid):
    j = c.get(f"/pedidos/{pid}").json(); return [(i["id"], round(i["cantidad"] - (i.get("cantidad_entregada") or 0), 4)) for i in j["items"] if i["cantidad"] - (i.get("cantidad_entregada") or 0) > 0.001]
def armar(pid, metodo=None, items=None, **extra):
    body = {"pedido_id": pid, "items": items if items is not None else [{"pedido_item_id": i, "cantidad": cant} for i, cant in pendientes(pid)]}
    if metodo is not None: body["metodo_entrega"] = metodo
    body.update(extra); return c.post("/remitos/armar", json=body)

empresa = q("select id from empresas_transporte limit 1")[0][0]
check("setup: migrate_047 aplicada sobre la copia y la oficina NO existe todavía", q("select count(*) from domicilios where id=?", OFICINA)[0][0] == 0)

# ---------------- 1) MOSTRADOR ----------------
p1 = libre(transporte=False)
r = armar(p1, "MOSTRADOR", transporte_id=empresa, domicilio_entrega_id="11111111-2222-3333-4444-555555555555")
j = r.json()
check(f"MOSTRADOR: armar -> 200 [{r.status_code}] y el remito queda con metodo_entrega MOSTRADOR congelado", r.status_code == 200 and j["metodo_entrega"] == "MOSTRADOR")
check("MOSTRADOR: transporte_id NULL aunque el payload mande uno (la mercadería no sale a ningún lado)", j["transporte_id"] is None and q("select transporte_id from remitos where id=?", h(j["id"]))[0][0] is None)
check("MOSTRADOR: el domicilio es la oficina (DOMICILIO_ROSETI_ID), no el del payload ni el del pedido", h(j["domicilio_entrega_id"]) == OFICINA)
check("MOSTRADOR: la oficina NO existía y se restauró con sus datos documentados (Roseti 1482, CABA)", q("select calle, numero, localidad, provincia_id, bit_identidad from domicilios where id=?", OFICINA) == [("Roseti", "1482", "CABA", "C", 1)])
check("MOSTRADOR: nace sin número legal (se asigna al imprimir), ENTREGADO y con fecha de salida ahora (decisión de Arq 30/09)", j["numero_legal"] is None and j["estado"] == "ENTREGADO" and j["fecha_salida"] is not None and abs((datetime.now() - datetime.fromisoformat(j["fecha_salida"])).total_seconds()) < 120)
ped = c.get(f"/pedidos/{p1}").json()
check("MOSTRADOR: la entrega cuenta (cantidad_entregada == cantidad en todos los renglones) y no queda pendiente nada", all(abs((i.get("cantidad_entregada") or 0) - i["cantidad"]) < 0.001 for i in ped["items"]) and pendientes(p1) == [])
p1b = libre(transporte=False)
j2 = armar(p1b, "mostrador").json()
check("MOSTRADOR: el método se acepta en minúsculas y no duplica la oficina", j2["metodo_entrega"] == "MOSTRADOR" and q("select count(*) from domicilios where id=?", OFICINA)[0][0] == 1)

# ---------------- 2) otros metodos ----------------
p2 = libre(transporte=False)
r = armar(p2, "FLETE_TERCERO")
check(f"FLETE_TERCERO sin ningún transporte -> 400 [{r.status_code}]", r.status_code == 400 and "transporte" in r.json()["detail"].lower())
check("FLETE_TERCERO rechazado no dejó ningún remito", q("select count(*) from remitos where pedido_id=?", p2)[0][0] == 0)
r = armar(p2, "FLETE_TERCERO", transporte_id=empresa)
check(f"FLETE_TERCERO con transporte -> 200, congelado y BORRADOR (despachar es una acción posterior) [{r.status_code}]", r.status_code == 200 and r.json()["metodo_entrega"] == "FLETE_TERCERO" and h(r.json()["transporte_id"]) == h(empresa) and r.json()["estado"] == "BORRADOR" and r.json()["fecha_salida"] is None)
for metodo in ("TRANSPORTE_PROPIO", "MOTO_CADETERIA", "REMITO_EXTERNO"):
    pm = libre(transporte=False)
    r = armar(pm, metodo); jj = r.json()
    check(f"{metodo} sin transporte -> 200, transporte NULL, domicilio del pedido, BORRADOR sin fecha de salida [{r.status_code}]", r.status_code == 200 and jj["metodo_entrega"] == metodo and jj["transporte_id"] is None and jj["domicilio_entrega_id"] is not None and h(jj["domicilio_entrega_id"]) != OFICINA and jj["estado"] == "BORRADOR" and jj["fecha_salida"] is None)
pconT = libre(transporte=True)
r = armar(pconT, "MOTO_CADETERIA")
check("MOTO_CADETERIA NO hereda el transporte del pedido (no interviene empresa de transporte)", r.status_code == 200 and r.json()["transporte_id"] is None)
r = armar(libre(transporte=False), "CHASQUI")
check(f"método inválido -> 400 METODO_ENTREGA_INVALIDO [{r.status_code}]", r.status_code == 400 and "METODO_ENTREGA_INVALIDO" in r.json()["detail"])
pleg = libre(transporte=True)
r = armar(pleg)
check(f"sin método y con transporte del pedido: camino de siempre, metodo_entrega NULL [{r.status_code}]", r.status_code == 200 and r.json()["metodo_entrega"] is None and r.json()["transporte_id"] is not None)
pleg2 = libre(transporte=False); n0 = q("select count(*) from remitos")[0][0]
r = armar(pleg2)
check(f"sin método y sin transporte: sigue fallando como antes -> 400 [{r.status_code}], sin remito nuevo", r.status_code == 400 and q("select count(*) from remitos")[0][0] == n0)

# ---------------- 3) motivo por renglon ----------------
p3 = libre(transporte=False, min_items=2)
pend = pendientes(p3); assert len(pend) >= 2
items = [{"pedido_item_id": pend[0][0], "cantidad": pend[0][1], "motivo_no_facturable": "CONSIGNACION"}] + [{"pedido_item_id": i, "cantidad": cant} for i, cant in pend[1:]]
r = armar(p3, "MOSTRADOR", items=items); j3 = r.json()
check(f"un mismo remito con un renglón en consignación y el resto de venta firme -> 200 [{r.status_code}]", r.status_code == 200)
mot = {it["pedido_item_id"]: it["motivo_no_facturable"] for it in j3["items"]}
check("la API devuelve el motivo por renglón (CONSIGNACION / None)", mot[pend[0][0]] == "CONSIGNACION" and all(mot[i] is None for i, _ in pend[1:]))
fact = {row[0]: row[1] for row in q("select pedido_item_id, cantidad_facturada from remitos_items where remito_id=?", h(j3["id"]))}
check("renglón con motivo nace con cantidad_facturada NULL (no aplica todavía); los demás en 0.0 (aplica y pendiente)", fact[pend[0][0]] is None and all(fact[i] == 0.0 for i, _ in pend[1:]))
for mt in ("MUESTRA_SIN_CARGO", "GARANTIA_REEMPLAZO"):
    pz = libre(transporte=False); (pi_, cant_), = pendientes(pz)[:1]
    rr = armar(pz, "MOSTRADOR", items=[{"pedido_item_id": pi_, "cantidad": cant_, "motivo_no_facturable": mt.lower()}])
    check(f"motivo {mt} aceptado (también en minúsculas) y persistido", rr.status_code == 200 and q("select motivo_no_facturable from remitos_items where remito_id=?", h(rr.json()["id"]))[0][0] == mt)
pz = libre(transporte=False); n0 = q("select count(*) from remitos")[0][0]; (pi_, cant_), = pendientes(pz)[:1]
r = armar(pz, "MOSTRADOR", items=[{"pedido_item_id": pi_, "cantidad": cant_, "motivo_no_facturable": "REGALO"}])
check(f"motivo inválido -> 409 y no queda ningún remito [{r.status_code}]", r.status_code == 409 and "MOTIVO_NO_FACTURABLE_INVALIDO" in r.json()["detail"] and q("select count(*) from remitos")[0][0] == n0)
# devolución con motivo: sobre un pedido ya entregado por mostrador (p1)
it_p1 = c.get(f"/pedidos/{p1}").json()["items"][0]
n0 = q("select count(*) from remitos")[0][0]
r = c.post("/remitos/armar", json={"pedido_id": p1, "items": [{"pedido_item_id": it_p1["id"], "cantidad": -1, "motivo_no_facturable": "CONSIGNACION"}], "domicilio_entrega_id": j["domicilio_entrega_id"], "metodo_entrega": "MOSTRADOR"})
check(f"una devolución (cantidad negativa) no admite motivo -> 409 MOTIVO_EN_DEVOLUCION [{r.status_code}]", r.status_code == 409 and "MOTIVO_EN_DEVOLUCION" in r.json()["detail"] and q("select count(*) from remitos")[0][0] == n0)
r = c.post("/remitos/armar", json={"pedido_id": p1, "items": [{"pedido_item_id": it_p1["id"], "cantidad": -1}], "metodo_entrega": "MOSTRADOR"})
check(f"la devolución normal (Etapa 6) sigue funcionando, ahora también por mostrador [{r.status_code}]", r.status_code == 200 and r.json()["items"][0]["cantidad"] == -1)

# ---------------- 4) el conciliador y la resolucion ----------------
from backend.ingesta.conciliador import ConciliadorService
from backend.remitos import models as rm
db = S()
rem3 = db.query(rm.Remito).filter(rm.Remito.id == j3["id"]).first()
pool = {ri.pedido_item_id for ri in ConciliadorService._renglones_pendientes(rem3)}
check("el conciliador NO ofrece para facturar el renglón con motivo abierto, sí los de venta firme", pend[0][0] not in pool and all(i in pool for i, _ in pend[1:]))
db.close()
ri_id = next(it["id"] for it in j3["items"] if it["pedido_item_id"] == pend[0][0])
r = c.post(f"/remitos/items/{ri_id}/resolver-no-facturable", json={"accion": "FACTURAR"}); jr = r.json()
check(f"resolver FACTURAR -> 200 y el motivo vuelve a NULL [{r.status_code}]", r.status_code == 200 and jr["motivo_no_facturable"] is None)
check("resolver: cantidad_facturada pasa de NULL a 0.0 (aplica y pendiente)", q("select cantidad_facturada, motivo_no_facturable from remitos_items where id=?", ri_id) == [(0.0, None)])
nota = q("select texto, autor_id, remito_item_id from remitos_notas where remito_item_id=?", ri_id)
check("resolver deja una nota [SISTEMA] en el renglón con el motivo anterior y el autor de la sesión", len(nota) == 1 and "[SISTEMA]" in nota[0][0] and "CONSIGNACION" in nota[0][0] and nota[0][1] == 1)
db = S(); rem3 = db.query(rm.Remito).filter(rm.Remito.id == j3["id"]).first()
check("el conciliador ahora SÍ lo ofrece (entró al camino normal)", pend[0][0] in {ri.pedido_item_id for ri in ConciliadorService._renglones_pendientes(rem3)}); db.close()
r = c.post(f"/remitos/items/{ri_id}/resolver-no-facturable", json={"accion": "FACTURAR"})
check(f"resolver de nuevo -> 409 RENGLON_SIN_MOTIVO [{r.status_code}]", r.status_code == 409 and "RENGLON_SIN_MOTIVO" in r.json()["detail"])
pz = libre(transporte=False); (pi_, cant_), = pendientes(pz)[:1]
rz = armar(pz, "MOSTRADOR", items=[{"pedido_item_id": pi_, "cantidad": cant_, "motivo_no_facturable": "MUESTRA_SIN_CARGO"}]).json()
rid = rz["items"][0]["id"]
r = c.post(f"/remitos/items/{rid}/resolver-no-facturable", json={"accion": "DEVOLVER"})
check(f"acción DEVOLVER -> 400: la devolución no pasa por acá, es un PR de cantidad negativa [{r.status_code}]", r.status_code == 400 and "ACCION_INVALIDA" in r.json()["detail"] and q("select motivo_no_facturable from remitos_items where id=?", rid)[0][0] == "MUESTRA_SIN_CARGO")
r = c.post("/remitos/items/99999999/resolver-no-facturable", json={"accion": "FACTURAR"})
check(f"renglón inexistente -> 404 [{r.status_code}]", r.status_code == 404)
prosa = libre(rosa=True, transporte=False); (pi_, cant_), = pendientes(prosa)[:1]
rr_ = armar(prosa, "MOSTRADOR", items=[{"pedido_item_id": pi_, "cantidad": cant_, "motivo_no_facturable": "CONSIGNACION"}]).json()
c.post(f"/remitos/items/{rr_['items'][0]['id']}/resolver-no-facturable", json={"accion": "FACTURAR"})
check("pedido Rosa: al resolver, cantidad_facturada sigue NULL (no aplica, nunca se factura) y el motivo se limpia", q("select cantidad_facturada, motivo_no_facturable from remitos_items where id=?", rr_["items"][0]["id"]) == [(None, None)])
pz = libre(transporte=False); (pi_, cant_), = pendientes(pz)[:1]
ra = armar(pz, "MOSTRADOR", items=[{"pedido_item_id": pi_, "cantidad": cant_, "motivo_no_facturable": "CONSIGNACION"}]).json()
con = sqlite3.connect(TMP); con.execute("update remitos set estado='ANULADO' where id=?", (h(ra["id"]),)); con.commit(); con.close()
r = c.post(f"/remitos/items/{ra['items'][0]['id']}/resolver-no-facturable", json={"accion": "FACTURAR"})
check(f"renglón de un remito ANULADO no se resuelve -> 409 REMITO_ANULADO, y el motivo queda [{r.status_code}]", r.status_code == 409 and "REMITO_ANULADO" in r.json()["detail"] and q("select motivo_no_facturable from remitos_items where id=?", ra["items"][0]["id"])[0][0] == "CONSIGNACION")

# ---------------- 5) lecturas con transporte NULL ----------------
lst = c.get("/remitos/"); one = c.get(f"/remitos/{j['id']}"); porp = c.get(f"/remitos/por_pedido/{p1}")
check(f"las lecturas con transporte NULL no dan 500: lista [{lst.status_code}], uno [{one.status_code}], por pedido [{porp.status_code}]", lst.status_code == 200 and one.status_code == 200 and porp.status_code == 200)
check("GET de un remito de mostrador trae metodo_entrega y transporte_id null", one.json()["metodo_entrega"] == "MOSTRADOR" and one.json()["transporte_id"] is None)
ent = c.get("/remitos/entregas"); check(f"/remitos/entregas (logística) tolera remitos sin transporte [{ent.status_code}]", ent.status_code == 200)
for ruta in ("/informes/remitos", "/informes/pedidos-pendiente", "/informes/pedidos-sin-remito", "/informes/abc-clientes", "/informes/abc-productos"):
    rr = c.get(ruta); check(f"{ruta} sigue respondiendo con remitos de mostrador en la base [{rr.status_code}]", rr.status_code == 200)

# ---------------- 6) remito interno desde factura ----------------
cand = q("""select f.id, cast(f.pedido_id as integer) from facturas f join pedidos p on p.id = cast(f.pedido_id as integer)
            where p.estado != 'ANULADO' and p.id not in (select pedido_id from remitos where estado != 'ANULADO')""")
cand = [(f, p) for f, p in cand if p not in usados]
fid, fped = cand[0]; usados.add(fped)
fid_u = f"{fid[:8]}-{fid[8:12]}-{fid[12:16]}-{fid[16:20]}-{fid[20:]}"
r = c.post(f"/remitos/interno/desde_factura/{fid_u}", params={"metodo_entrega": "FLETE_TERCERO"})
check(f"desde factura: FLETE_TERCERO no es un método válido acá -> 400 [{r.status_code}]", r.status_code == 400 and "METODO_ENTREGA_INVALIDO" in r.json()["detail"])
r = c.post(f"/remitos/interno/desde_factura/{fid_u}", params={"metodo_entrega": "MOSTRADOR"}); ji = r.json()
check(f"desde factura MOSTRADOR -> 200, remito interno MOSTRADOR ENTREGADO sin número [{r.status_code}]", r.status_code == 200 and ji["metodo_entrega"] == "MOSTRADOR" and ji["numero_legal"] is None and ji["estado"] == "ENTREGADO" and h(ji["domicilio_entrega_id"]) == OFICINA and ji["transporte_id"] is None)
check("desde factura: la factura queda vinculada al remito y lleva todo lo pendiente del pedido", q("select count(*) from facturas_remitos where factura_id=? and remito_id=?", fid, h(ji["id"]))[0][0] == 1 and pendientes(fped) == [])
r2 = c.post(f"/remitos/interno/desde_factura/{fid_u}", params={"metodo_entrega": "MOSTRADOR"})
check("desde factura, segunda vez: no crea otro remito, devuelve el mismo", r2.status_code == 200 and r2.json()["id"] == ji["id"] and q("select count(*) from remitos where pedido_id=? and estado != 'ANULADO'", fped)[0][0] == 1)

cand2 = [(f, p) for f, p in q("""select f.id, cast(f.pedido_id as integer) from facturas f join pedidos p on p.id = cast(f.pedido_id as integer)
            where p.estado != 'ANULADO' and p.id not in (select pedido_id from remitos where estado != 'ANULADO')""") if p not in usados]
fid2, fped2 = cand2[0]; usados.add(fped2)
r3 = c.post(f"/remitos/interno/desde_factura/{fid2[:8]}-{fid2[8:12]}-{fid2[12:16]}-{fid2[16:20]}-{fid2[20:]}", params={"metodo_entrega": "REMITO_EXTERNO"})
check(f"desde factura REMITO_EXTERNO -> 200, BORRADOR sin número (viaja con la etiqueta de un tercero, no sale en el acto) [{r3.status_code}]", r3.status_code == 200 and r3.json()["metodo_entrega"] == "REMITO_EXTERNO" and r3.json()["estado"] == "BORRADOR" and r3.json()["numero_legal"] is None and r3.json()["transporte_id"] is None)

# ---------------- 7) impresión ----------------
def pdf_texto(remito_id):
    rp = c.get(f"/remitos/{remito_id}/pdf"); assert rp.status_code == 200, (rp.status_code, rp.text[:300])
    d = fitz.open(stream=rp.content, filetype="pdf"); return " ".join(" ".join(p.get_text().split()) for p in d)
pg = libre(rosa=True, transporte=False, cuit="11111111119")
rg = armar(pg, "MOSTRADOR").json(); tg = pdf_texto(rg["id"])
razon_g = q("select c.razon_social from pedidos p join clientes c on c.id=p.cliente_id where p.id=?", pg)[0][0]
check(f"PDF: cliente con CUIT genérico ({razon_g}, 11111111119) -> el número NO se imprime (ni con guiones) y el nombre sí", not re.search(r"11-?1{8}-?9", tg) and razon_g.upper() in tg)
check("PDF de mostrador: el domicilio impreso es el de la oficina (Roseti 1482)", "ROSETI 1482" in tg)
check("PDF: CUIT genérico -> condición de IVA 'Cons. Final'", "Cons. Final" in tg)
pn = libre(rosa=False, transporte=False)
cuit_n = q("select c.cuit from pedidos p join clientes c on c.id=p.cliente_id where p.id=?", pn)[0][0]
rn = armar(pn, "REMITO_EXTERNO").json(); tn = pdf_texto(rn["id"])
if re.sub(r"\D", "", cuit_n or "") in ("00000000000", "11111111119", "11111111111", "99999999999"):
    pn = libre(rosa=False, transporte=False); rn = armar(pn, "REMITO_EXTERNO").json(); tn = pdf_texto(rn["id"]); cuit_n = q("select c.cuit from pedidos p join clientes c on c.id=p.cliente_id where p.id=?", pn)[0][0]
check(f"PDF: un cliente con CUIT real ({cuit_n}) SÍ imprime su número", cuit_n and cuit_n in tn)
check("PDF Rosa: no muestra precio ni subtotal ni signo $", "$" not in tg and "precio" not in tg.lower() and "subtotal" not in tg.lower())
nums = q("select numero_legal from remitos where numero_legal is not null and id in (?, ?)", h(rg["id"]), h(rn["id"]))
check(f"numeración al imprimir: Rosa y no-Rosa salen por el 0015, nunca por el 17 [{[n[0] for n in nums]}]", len(nums) == 2 and all(n[0].startswith("0015-") for n in nums) and not any(n[0].startswith("17-") for n in nums))
check("el 0015 es correlativo (el segundo número es el primero + 1)", int(sorted(n[0] for n in nums)[1].split("-")[1]) == int(sorted(n[0] for n in nums)[0].split("-")[1]) + 1)
from backend.remitos.remito_engine import es_cuit_generico
check("es_cuit_generico: con/sin guiones, los cuatro genéricos sí; un CUIT real y None no", all(es_cuit_generico(x) for x in ("00000000000", "11111111119", "11-11111111-1", "99999999999", "00-00000000-0")) and not es_cuit_generico("30-71560397-3") and not es_cuit_generico(None))
antes_num = q("select numero_legal from remitos where id=?", h(rg["id"]))[0][0]
r0 = c.get(f"/remitos/{rg['id']}/pdf")
check("reimprimir no vuelve a numerar (idempotente)", r0.status_code == 200 and q("select numero_legal from remitos where id=?", h(rg["id"]))[0][0] == antes_num and antes_num.startswith("0015-"))

# ---------------- 8) la oficina y los clientes Rosa ----------------
from backend.clientes.service import ClienteService
from backend.clientes.models import Domicilio
db = S()
con = sqlite3.connect(TMP); con.execute("delete from domicilios where id=?", (OFICINA,)); con.commit(); con.close()
dom = ClienteService.ensure_domicilio_oficina(db); db.commit()
check("ensure_domicilio_oficina restaura la fila si falta (y es idempotente)", dom.calle == "Roseti" and dom.numero == "1482" and ClienteService.ensure_domicilio_oficina(db).id == dom.id and q("select count(*) from domicilios where id=?", OFICINA)[0][0] == 1)
cli_rosa = q("select id from clientes limit 1")[0][0]
con = sqlite3.connect(TMP); con.execute("delete from domicilios where id=?", (OFICINA,)); con.execute("delete from domicilios_clientes where cliente_id=?", (cli_rosa,)); con.commit(); con.close()
db.expire_all()
import uuid as _u
ClienteService._ensure_domicilio_rosa(_u.UUID(cli_rosa), db); db.commit()
check("_ensure_domicilio_rosa ya no deja el vínculo colgado: crea la oficina antes de vincularla", q("select count(*) from domicilios where id=?", OFICINA)[0][0] == 1 and q("select count(*) from domicilios_clientes where cliente_id=? and domicilio_id=?", cli_rosa, OFICINA)[0][0] == 1)
db.close()

del c; gc.collect(); eng.dispose()
try: os.remove(TMP)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
