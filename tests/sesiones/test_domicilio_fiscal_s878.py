"""Guardar un domicilio FISCAL por la ficha ya no da 500 (S878, bug de Tomy: transporte en un domicilio nuevo). Sobre una COPIA de la base de P."""
import sys, os, shutil, sqlite3, uuid
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5"); os.chdir(r"C:\dev\Sonido_Liquido_V5")
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
TMP = r"C:\dev\Sonido_Liquido_V5\scratch\test_dom_fiscal_tmp.db"
copiar_p(r"C:\dev\Sonido_Liquido_V5\scratch\pilot_v5x_P_migrada_20260930.db", TMP)
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
cid = str(uuid.UUID(q("select id from clientes limit 1")[0][0])); tid = str(uuid.UUID(q("select id from empresas_transporte limit 1")[0][0]))
prov = str(q("select id from provincias limit 1")[0][0])
base = {"calle": "AV. ARTURO ILLIA", "numero": "4873", "cp": "1663", "localidad": "SAN MIGUEL", "provincia_id": prov, "es_fiscal": True}
r = c.post(f"/clientes/{cid}/domicilios", json=base); check(f"alta de un domicilio fiscal nuevo: 201 [{r.status_code}]", r.status_code == 201); dom = r.json()["id"]
real = dict(base, transporte_id=tid, es_entrega=True, activo=True, observaciones="", notas_logistica="", maps_link="", contacto_id=None, id=dom, cliente_id=cid)
# 1) la primera vez se bifurca (espejo por defecto); 2) las siguientes pasaban por el camino que daba 500
ids = [dom]
for i in range(1, 4):
    r = c.put(f"/clientes/{cid}/domicilios/{ids[-1]}", json=real)
    check(f"guardado {i} por la ficha (transporte + es_fiscal=true): 200 [{r.status_code}] y no 500", r.status_code == 200)
    if r.status_code == 200: ids.append(r.json()["id"])
r = c.put(f"/clientes/{cid}/domicilios/{dom}", json=real)
check(f"guardar de nuevo sobre el id ORIGINAL (el caso de Tomy): no es 500 [{r.status_code}]", r.status_code != 500)
r = c.put(f"/clientes/{cid}/domicilios/{ids[-1]}", json={"transporte_id": tid, "es_fiscal": True})
check(f"solo transporte + es_fiscal sobre el domicilio vigente: 200 [{r.status_code}]", r.status_code == 200)
fisc = q("select count(*) from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=? and d.es_fiscal=1", cid.replace("-", ""))[0][0]
check(f"después de los guardados el cliente tiene UN solo domicilio fiscal (hay {fisc})", fisc == 1)
trp = q("select count(*) from domicilios d join domicilios_clientes dc on dc.domicilio_id=d.id where dc.cliente_id=? and d.es_fiscal=1 and d.transporte_id is not null", cid.replace("-", ""))[0][0]
check("el domicilio fiscal vigente quedó con el transporte guardado", trp == 1)
del c
try: os.remove(TMP)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
