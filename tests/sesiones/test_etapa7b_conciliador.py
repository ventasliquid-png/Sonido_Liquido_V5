"""Etapa 7b -- conciliador factura <-> PR, end to end contra COPIAS descartables de pilot_v5x.db.
Nunca toca la base viva. Cada escenario arranca de una copia fresca.
Datos reales de D: pedido #24 (Genesis Bag, CUIT 30717179842) == factura ARCA 2526 guardada en
ingesta_facturas_raw (toallas x3 a 42350 + toallas cortas x1 a 33500)."""
import shutil, sys, os, sqlite3
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5")
os.chdir(r"C:\dev\Sonido_Liquido_V5")

import backend.main as main_module
from backend.main import app
from backend.core.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

SCRATCH = r"C:\dev\Sonido_Liquido_V5\scratch\pilot_v5x_etapa7b_test.db"
DOM = "0358b5a6d2ec461caec2c3978930499a"
TRANS = "44264d5c43a147d3997fd558d38b3db6"

checks = []
def check(desc, cond):
    checks.append((desc, bool(cond)))
    print(("[OK]  " if cond else "[FAIL]"), desc)

engine = None
def copia_fresca():
    global engine
    if engine is not None:
        engine.dispose()
    copiar_p("pilot_v5x.db", SCRATCH)
    engine = create_engine(f"sqlite:///{SCRATCH}")
    Session = sessionmaker(bind=engine)
    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override
    return TestClient(app)

def sql(q, args=()):
    con = sqlite3.connect(SCRATCH); cur = con.cursor(); cur.execute(q, args); r = cur.fetchall(); con.close(); return r

def raw_id(numero):
    return sql("SELECT id FROM ingesta_facturas_raw WHERE filename LIKE ? LIMIT 1", (f"%{numero}%",))[0][0]

def raw_uuid(numero):
    import uuid
    return str(uuid.UUID(raw_id(numero)))

def armar(client, items):
    r = client.post("/remitos/armar", json={"pedido_id": 24, "domicilio_entrega_id": DOM, "transporte_id": TRANS,
                                             "items": [{"pedido_item_id": a, "cantidad": b} for a, b in items]})
    assert r.status_code == 200, r.text
    return r.json()

def token(client):
    r = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

def ri_de(remito, pedido_item_id):
    return next(i["id"] for i in remito["items"] if i["pedido_item_id"] == pedido_item_id)

# La factura 2526 tiene 5 renglones = el pedido #24 entero (40..44).
PEDIDO_24 = [(40, 3), (41, 1), (42, 1), (43, 2), (44, 2)]
def emp_completo(pr):
    return [{"item_pdf": i, "remito_item_id": ri_de(pr, pid)} for i, (pid, _) in enumerate(PEDIDO_24)]

# =========================================================== 1. camino feliz
client = copia_fresca()
pr = armar(client, PEDIDO_24)
facturadas = sql("SELECT cantidad_facturada FROM remitos_items WHERE remito_id = ?", (pr["id"].replace("-", ""),))
check("Regla de nacimiento: PR blanco nace con cantidad_facturada = 0 en sus 5 renglones", [f[0] for f in facturadas] == [0.0] * 5)
legacy = sql("SELECT COUNT(*) FROM remitos_items WHERE cantidad_facturada IS NULL")[0][0]
check(f"Los renglones legacy siguen en NULL (no se tocan: {legacy})", legacy >= 31)

rid = raw_uuid("00002526")
c = client.get(f"/ingesta/raw/{rid}/conciliacion/candidatos").json()
check("Candidatos: tipo FACTURA_A leido del PDF", c["factura"]["tipo_comprobante"] == "FACTURA_A")
check("Candidatos: sin bloqueos", c["bloqueos"] == [])
check("Candidatos: aparece el PR recien armado, con 5 renglones pendientes",
      any(p["remito_id"] == pr["id"] and len(p["renglones"]) == 5 for p in c["prs"]))
check("Candidatos: el remito legacy de Genesis (pedido 48, facturada NULL) NO aparece",
      all(p["pedido_id"] == 24 for p in c["prs"]))

ev = client.post(f"/ingesta/raw/{rid}/conciliacion/evaluar", json={"remito_ids": [pr["id"]]}).json()
emp = {e["item_pdf"]: (e["remito_item_id"], e.get("como")) for e in ev["emparejamiento"]}
check("Sugerido: 'Toalla 200 mts x 6' -> renglon 40 por nombre", emp[0] == (ri_de(pr, 40), "nombre"))
check("Sugerido: 'Papel higiénico 122' -> renglon 42 por nombre (acento ignorado)", emp[2] == (ri_de(pr, 42), "nombre"))
check("Sugerido: 'Alcohol 70% bidon' -> renglon 43 'Alcohol 70 % bidon' (espacio/puntuacion ignorados)", emp[3] == (ri_de(pr, 43), "nombre"))
check("Sugerido: 'Toallas super cortas caja x 2500' -> renglon 41 por DESCARTE (unico libre de cada lado)", emp[1] == (ri_de(pr, 41), "descarte"))
check("Sugerido completo: sin bloqueos y sin Clase B", ev["bloqueos"] == [] and not any(d["clase"] == "B" for d in ev["diferencias"]))
check("Clase A informativa presente (datos de ARCA)", any(d["clase"] == "A" for d in ev["diferencias"]))

ev_inc = client.post(f"/ingesta/raw/{rid}/conciliacion/evaluar",
                     json={"remito_ids": [pr["id"]], "emparejamiento": [*emp_completo(pr)[:4], {"item_pdf": 4, "remito_item_id": None}]}).json()
check("Operador deja un renglon de factura sin par -> Clase B 'no esta en los PR' (no bloquea)",
      any(d["clase"] == "B" and d.get("item_pdf") == 4 for d in ev_inc["diferencias"]) and ev_inc["bloqueos"] == [])
manual = emp_completo(pr)

r = client.post(f"/ingesta/raw/{rid}/conciliacion/confirmar", json={"remito_ids": [pr["id"]], "emparejamiento": manual})
check("Confirmar SIN sesion -> 401", r.status_code == 401)
r = client.post(f"/ingesta/raw/{rid}/conciliacion/confirmar", json={"remito_ids": [pr["id"]], "emparejamiento": manual}, headers=token(client))
check(f"Confirmar con sesion -> 200 ({r.status_code})", r.status_code == 200)

f = sql("SELECT tipo_comprobante, estado, punto_venta, numero_comprobante, fecha_emision, cae, cuit_comprador, neto_gravado, total FROM facturas WHERE numero_comprobante = 2526")
check(f"Factura REAL registrada: {f}", len(f) == 1 and f[0][0] == "FACTURA_A" and f[0][1] == "AUTORIZADA_AFIP" and f[0][2] == 1)
check("Fecha de emision de ARCA (2026-04-21), no la de carga", f and str(f[0][4]).startswith("2026-04-21"))
check("CAE y CUIT del comprador guardados", f and f[0][5] and f[0][6] == "30717179842")
check("Neto 252350 (suma de los 5 renglones)", f and abs(f[0][7] - 252350.0) < 0.01)
fid = sql("SELECT id FROM facturas WHERE numero_comprobante = 2526")[0][0]
check("Vinculo facturas_remitos creado", sql("SELECT COUNT(*) FROM facturas_remitos WHERE factura_id = ?", (fid,))[0][0] == 1)
fi = sql("SELECT remito_item_id FROM facturas_items WHERE factura_id = ?", (fid,))
check(f"5 renglones de factura, todos atados a su renglon de PR", len(fi) == 5 and all(x[0] is not None for x in fi))
fact = dict(sql("SELECT pedido_item_id, cantidad_facturada FROM remitos_items WHERE remito_id = ?", (pr["id"].replace("-", ""),)))
check(f"cantidad_facturada == remitida en los 5 ({fact})", fact == {40: 3.0, 41: 1.0, 42: 1.0, 43: 2.0, 44: 2.0})
check("Sin nota [SISTEMA] (no hubo Clase B)", sql("SELECT COUNT(*) FROM remitos_notas")[0][0] == 0)
check("Auditoria de ingesta: FacturasProcesadas CONCILIADA",
      sql("SELECT COUNT(*) FROM ingesta_facturas_procesadas WHERE estado = 'CONCILIADA'")[0][0] == 1)

c2 = client.get(f"/ingesta/raw/{rid}/conciliacion/candidatos").json()
check("Re-intentar la misma factura -> bloqueo FACTURA_DUPLICADA", any("FACTURA_DUPLICADA" in b for b in c2["bloqueos"]))
check("El PR ya no es candidato (todo facturado)", all(p["remito_id"] != pr["id"] for p in c2["prs"]))
r = client.post(f"/ingesta/raw/{rid}/conciliacion/confirmar", json={"remito_ids": [pr["id"]], "emparejamiento": manual}, headers=token(client))
check("Confirmar duplicada -> 409", r.status_code == 409)

# =========================================================== 1b. factura parcial
client = copia_fresca()
pr = armar(client, PEDIDO_24)
# Fixture en la COPIA descartable: el renglon de toallas pasa a remitido 5 (la factura dice 3).
con = sqlite3.connect(SCRATCH)
con.execute("UPDATE remitos_items SET cantidad_remitida = 5 WHERE id = ?", (ri_de(pr, 40),)); con.commit(); con.close()
rid = raw_uuid("00002526")
ev = client.post(f"/ingesta/raw/{rid}/conciliacion/evaluar", json={"remito_ids": [pr["id"]], "emparejamiento": emp_completo(pr)}).json()
check("Parcial: factura 3 de 5 remitidas -> clase PARCIAL informativa, no B, sin bloqueo",
      any(d["clase"] == "PARCIAL" for d in ev["diferencias"]) and not any(d["clase"] == "B" for d in ev["diferencias"]) and ev["bloqueos"] == [])
r = client.post(f"/ingesta/raw/{rid}/conciliacion/confirmar", json={"remito_ids": [pr["id"]], "emparejamiento": emp_completo(pr)}, headers=token(client))
check("Parcial confirma -> 200", r.status_code == 200)
c3 = client.get(f"/ingesta/raw/{raw_uuid('00002546')}/conciliacion/candidatos").json()
p = next((p for p in c3["prs"] if p["remito_id"] == pr["id"]), None)
check("Tras la parcial, el PR sigue candidato con 2 toallas pendientes de facturar",
      p is not None and len(p["renglones"]) == 1 and abs(p["renglones"][0]["pendiente_facturar"] - 2) < 0.001)

# =========================================================== 2. Clase B: concilia y anota
client = copia_fresca()
pr = armar(client, [(40, 2), (41, 1), (42, 1), (43, 2), (44, 2)])      # salieron 2 toallas, la factura 2526 dice 3
rid = raw_uuid("00002526")
manual = emp_completo(pr)
ev = client.post(f"/ingesta/raw/{rid}/conciliacion/evaluar", json={"remito_ids": [pr["id"]], "emparejamiento": manual}).json()
check("Clase B detectada: factura 3, quedaban 2 por facturar", any(d["clase"] == "B" and "facturó de más" in d["detalle"] for d in ev["diferencias"]))
check("Clase B NO bloquea (decision de Carlos 28/09)", ev["bloqueos"] == [])
r = client.post(f"/ingesta/raw/{rid}/conciliacion/confirmar", json={"remito_ids": [pr["id"]], "emparejamiento": manual}, headers=token(client))
check("Confirma igual -> 200", r.status_code == 200)
fact = dict(sql("SELECT pedido_item_id, cantidad_facturada FROM remitos_items WHERE remito_id = ?", (pr["id"].replace("-", ""),)))
rem = dict(sql("SELECT pedido_item_id, cantidad_remitida FROM remitos_items WHERE remito_id = ?", (pr["id"].replace("-", ""),)))
check(f"cantidad_facturada = lo que dice la factura (3) aunque se remitieron 2 -> resta -1 visible ({fact[40]} vs {rem[40]})",
      fact[40] == 3.0 and rem[40] == 2.0)
notas = sql("SELECT texto, remito_item_id, autor_id FROM remitos_notas")
check(f"Nota [SISTEMA] en el PR, colgada del renglon y con autor real: {notas}",
      len(notas) == 1 and notas[0][0].startswith("[SISTEMA] ") and "clase B" in notas[0][0]
      and notas[0][1] == ri_de(pr, 40) and notas[0][2] is not None)

# =========================================================== 3. Clase C y otros bloqueos
client = copia_fresca()
pr = armar(client, PEDIDO_24)
rid_jorgito = raw_uuid("00002496")
ev = client.post(f"/ingesta/raw/{rid_jorgito}/conciliacion/evaluar", json={"remito_ids": [pr["id"]], "emparejamiento": [{"item_pdf": 0, "remito_item_id": ri_de(pr, 40)}]}).json()
check("Clase C: factura a Jorgito contra PR de Genesis -> clase C", any(d["clase"] == "C" for d in ev["diferencias"]))
check("Clase C bloquea", any("CLASE_C" in b for b in ev["bloqueos"]))
r = client.post(f"/ingesta/raw/{rid_jorgito}/conciliacion/confirmar", json={"remito_ids": [pr["id"]], "emparejamiento": [{"item_pdf": 0, "remito_item_id": ri_de(pr, 40)}]}, headers=token(client))
check("Confirmar clase C -> 409 y no se crea factura", r.status_code == 409 and sql("SELECT COUNT(*) FROM facturas WHERE numero_comprobante = 2496")[0][0] == 0)

rid = raw_uuid("00002526")
doble = [{"item_pdf": 0, "remito_item_id": ri_de(pr, 40)}, {"item_pdf": 1, "remito_item_id": ri_de(pr, 40)}]
ev = client.post(f"/ingesta/raw/{rid}/conciliacion/evaluar", json={"remito_ids": [pr["id"]], "emparejamiento": doble}).json()
check("Emparejamiento con renglon de PR repetido -> bloqueo", any("usado dos veces" in b for b in ev["bloqueos"]))
ev = client.post(f"/ingesta/raw/{rid}/conciliacion/evaluar", json={"remito_ids": [pr["id"]], "emparejamiento": [{"item_pdf": 0, "remito_item_id": ri_de(pr, 40)}]}).json()
check("Emparejamiento incompleto -> bloqueo", any("EMPAREJAMIENTO_INCOMPLETO" in b for b in ev["bloqueos"]))
ev = client.post(f"/ingesta/raw/{rid}/conciliacion/evaluar", json={"remito_ids": []}).json()
check("Sin PR elegido -> bloqueo", any("PR_REQUERIDO" in b for b in ev["bloqueos"]))

c = client.get(f"/ingesta/raw/{raw_uuid('00002458')}/conciliacion/candidatos").json()
check("Ceretti (CUIT fuera del padron de D) -> aviso contra natura, sin PR", c["prs"] == [] and any("CUIT_FUERA_DEL_PADRON" in a for a in c["avisos"]))
c = client.get(f"/ingesta/raw/{raw_uuid('00002591')}/conciliacion/candidatos").json()
check("2591 (ya registrada por el camino viejo como FACTURA_B espejo) -> FACTURA_DUPLICADA pese al tipo distinto",
      any("FACTURA_DUPLICADA" in b for b in c["bloqueos"]))

# =========================================================== 4. unidades: NC/ND y regla de nacimiento
from backend.ingesta.conciliador import ConciliadorService
from backend.remitos.service import RemitosService
from backend.remitos.constants import RemitoFlags
from backend.pedidos.constants import PedidoFlags
from sqlalchemy.orm import sessionmaker as _sm
db = _sm(bind=engine)()
enc = {"clase_comprobante": "NOTA_CREDITO", "tipo_comprobante": "NOTA_CREDITO_A", "numero_comprobante": 999, "punto_venta": 1,
       "cae": "1", "cuit": "30717179842", "tipo_warning": None}
check("Una NC no se concilia contra un PR: ES_AJUSTE (va por el flujo de 7d)", any("ES_AJUSTE" in b for b in ConciliadorService._bloqueos_de_comprobante(db, enc)))
enc = {**enc, "clase_comprobante": None, "tipo_comprobante": None, "tipo_warning": "x"}
check("Tipo ilegible se rechaza (nunca adivina)", any("TIPO_DESCONOCIDO" in b for b in ConciliadorService._bloqueos_de_comprobante(db, enc)))
db.close()

class O:  # objeto minimo con flags_estado
    def __init__(self, f): self.flags_estado = f
check("Nacimiento: PR con CIRCUITO_ROSA -> NULL", RemitosService._facturada_al_nacer(O(int(RemitoFlags.CIRCUITO_ROSA)), O(0)) is None)
check("Nacimiento: pedido NO_FISCAL_FORCE (manual, sin flag en el PR) -> NULL", RemitosService._facturada_al_nacer(O(0), O(int(PedidoFlags.NO_FISCAL_FORCE))) is None)
check("Nacimiento: pedido ES_NO_COMERCIAL -> NULL", RemitosService._facturada_al_nacer(O(0), O(int(PedidoFlags.ES_NO_COMERCIAL))) is None)
check("Nacimiento: blanco comercial -> 0.0", RemitosService._facturada_al_nacer(O(0), O(0)) == 0.0)

engine.dispose()
print()
total = len(checks); ok = sum(1 for _, c in checks if c)
print(f"RESULTADO: {ok}/{total} checks OK")
if ok != total: sys.exit(1)
