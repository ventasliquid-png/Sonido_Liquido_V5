r"""S883, Card #171: el alta de un pedido (POST /pedidos/tactico) respeta el tipo elegido: PRESUPUESTO nace con el bit de presupuesto y estado coherente; PENDIENTE (y el valor por defecto) como siempre.
El frontend (PedidoCanvas.vue) manda estado = PRESUPUESTO solo cuando se elige en el alta. Sobre una COPIA de la base de P de las 17:51."""
import sys, os, shutil, sqlite3
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from backend.pedidos.constants import PedidoFlags as PF, STATE_MASK
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261008_1751.db"
T = os.path.join(RAIZ, "scratch", "test_alta_estado_tmp.db"); shutil.copyfile(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v

cid = "069bd7c5be294d88a1df92c856239a7f"                      # Centro Pet
cid_u = f"{cid[:8]}-{cid[8:12]}-{cid[12:16]}-{cid[16:20]}-{cid[20:]}"
pid = q("select producto_id from pedidos_items where pedido_id=111")[0][0]
pid_u = pid   # los productos tienen id entero
n0 = q("select count(*) from pedidos")[0][0]
def alta(**extra):
    p = {"cliente_id": cid_u, "fecha": "2026-10-09T12:00:00", "items": [{"producto_id": pid_u, "cantidad": 10, "precio_unitario": 11020.0, "descuento_porcentaje": 0, "descuento_importe": 0}]}
    p.update(extra); return cli.post("/pedidos/tactico", json=p)
def estado_bits(i):
    e, f = q("select estado, flags_estado from pedidos where id=?", i)[0]; return e, (f & STATE_MASK.value)

r = alta(estado="PRESUPUESTO"); j = r.json() if r.status_code == 201 else {}
check(f"alta como PRESUPUESTO [{r.status_code}] {r.text[:100] if r.status_code != 201 else ''}", r.status_code == 201)
i1 = j.get("id")
check(f"el presupuesto nace con estado PRESUPUESTO y el bit ES_PRESUPUESTO (no el de pedido firme) {estado_bits(i1) if i1 else None}", i1 and estado_bits(i1) == ("PRESUPUESTO", PF.ES_PRESUPUESTO.value))
check("GET del pedido lo devuelve como PRESUPUESTO", i1 and cli.get(f"/pedidos/{i1}").json().get("estado") == "PRESUPUESTO")

r = alta(estado="PENDIENTE"); i2 = r.json().get("id") if r.status_code == 201 else None
check(f"alta como PENDIENTE: estado PENDIENTE y bit ES_FIRME [{r.status_code}] {estado_bits(i2) if i2 else None}", i2 and estado_bits(i2) == ("PENDIENTE", PF.ES_FIRME.value))

r = alta(); i3 = r.json().get("id") if r.status_code == 201 else None
check(f"alta sin indicar el tipo (como siempre): PENDIENTE y bit ES_FIRME [{r.status_code}] {estado_bits(i3) if i3 else None}", i3 and estado_bits(i3) == ("PENDIENTE", PF.ES_FIRME.value))

# GUARDAR LA FICHA de un presupuesto: la ficha mandaba siempre estado=PENDIENTE y el PATCH lo respeta, asi que el presupuesto se volvia pedido firme sin avisar.
# Ahora la ficha NO manda el estado al editar (el estado se cambia con el selector de la ficha).
r = cli.post("/pedidos/tactico", json={"cliente_id": cid_u, "fecha": "2026-10-09T12:00:00", "estado": "PRESUPUESTO", "items": [{"producto_id": pid_u, "cantidad": 10, "precio_unitario": 11020.0}]})
i4 = r.json().get("id")
payload_ficha = {"nota": "editado desde la ficha", "items": [{"producto_id": pid_u, "cantidad": 12, "precio_unitario": 11020.0}]}
r = cli.patch(f"/pedidos/{i4}", json=payload_ficha)
check(f"guardar la ficha SIN mandar el estado deja el presupuesto como PRESUPUESTO [{r.status_code}] {estado_bits(i4)}", r.status_code == 200 and estado_bits(i4) == ("PRESUPUESTO", PF.ES_PRESUPUESTO.value) and q("select nota from pedidos where id=?", i4)[0][0] == "editado desde la ficha")
r = cli.patch(f"/pedidos/{i4}", json=dict(payload_ficha, estado="PENDIENTE"))
check(f"(lo que hacia la ficha antes) mandar estado=PENDIENTE convierte el presupuesto en pedido firme [{r.status_code}] {estado_bits(i4)}", r.status_code == 200 and estado_bits(i4) == ("PENDIENTE", PF.ES_FIRME.value))

# el cambio de estado explicito de la ficha (selector) sigue andando en los dos sentidos
r = cli.patch(f"/pedidos/{i1}", json={"estado": "PENDIENTE"})
check(f"el selector de la ficha pasa el presupuesto a PENDIENTE [{r.status_code}] {estado_bits(i1)}", r.status_code == 200 and estado_bits(i1) == ("PENDIENTE", PF.ES_FIRME.value))
r = cli.patch(f"/pedidos/{i1}", json={"estado": "PRESUPUESTO"})
check(f"y de vuelta a PRESUPUESTO [{r.status_code}] {estado_bits(i1)}", r.status_code == 200 and estado_bits(i1) == ("PRESUPUESTO", PF.ES_PRESUPUESTO.value))

check(f"se crearon solo los 4 pedidos de la prueba [{q('select count(*) from pedidos')[0][0] - n0}]", q("select count(*) from pedidos")[0][0] == n0 + 4)
del cli; eng.dispose()
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
