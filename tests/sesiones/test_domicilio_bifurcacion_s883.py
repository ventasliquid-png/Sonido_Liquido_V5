r"""S883, Card #158: un domicilio NUEVO de un solo cliente nace con el espejo (Bit 21) encendido en la tabla puente y el primer guardado con notas lo BIFURCABA (clon + re-vinculo), dejando un duplicado
y un huerfano. La bifurcacion es copy-on-write de un domicilio COMPARTIDO por varios clientes: solo ahi corresponde, y solo si las notas realmente cambian.
Sobre una COPIA de la base de P de las 15:51."""
import sys, os, shutil, sqlite3
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
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
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261009_1551.db"
T = os.path.join(RAIZ, "scratch", "test_bifurc_tmp.db"); copiar_p(ORIG, T)
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
def h(u): return u.replace("-", "")
def uu(x): return f"{x[:8]}-{x[8:12]}-{x[12:16]}-{x[16:20]}-{x[20:]}"

CLI1 = "069bd7c5be294d88a1df92c856239a7f"   # Centro Pet
CLI2 = q("select id from clientes where id != ? and activo=1 limit 1", CLI1)[0][0]
prov = q("select id from provincias where upper(nombre) like 'BUENOS%' limit 1")[0][0]
def links(c): return q("select domicilio_id, flags from domicilios_clientes where cliente_id=?", c)
def alta(c, **extra):
    p = {"calle": "Calle de Prueba", "numero": "100", "localidad": "CABA", "provincia_id": prov, "es_entrega": True, "es_fiscal": False}; p.update(extra)
    r = cli.post(f"/clientes/{uu(c)}/domicilios", json=p); return r
def ficha(**extra):
    """Lo que manda la ficha del cliente al guardar un domicilio: siempre notas y observaciones (aunque esten vacias) y las flags de la tabla puente."""
    p = {"calle": "Calle de Prueba", "numero": "100", "localidad": "CABA", "provincia_id": prov, "notas_logistica": "", "observaciones": "", "flags": 2097152, "es_entrega": True}; p.update(extra); return p

n_dom0, n_lnk0 = q("select count(*) from domicilios")[0][0], q("select count(*) from domicilios_clientes")[0][0]
# ---- A) el caso del bug: un domicilio nuevo de UN cliente, primer guardado con notas vacias
r = alta(CLI1); d1 = r.json().get("id", "") if r.status_code == 201 else ""
check(f"A: alta del domicilio nuevo [{r.status_code}], nace con el espejo (Bit 21) en la tabla puente por defecto {q('select flags from domicilios_clientes where domicilio_id=?', h(d1))}", r.status_code == 201 and q("select flags from domicilios_clientes where domicilio_id=?", h(d1)) == [(2097152,)])
r = cli.put(f"/clientes/{uu(CLI1)}/domicilios/{d1}", json=ficha())
d1b = r.json().get("id", "") if r.status_code == 200 else ""
check(f"A: guardar sin tocar las notas NO bifurca: el id es el mismo [{r.status_code}] {d1b[:8]} vs {d1[:8]}", r.status_code == 200 and d1b == d1)
check("A: y no quedan ni un domicilio de mas ni un huerfano (1 domicilio y 1 vinculo mas que al principio)", q("select count(*) from domicilios")[0][0] == n_dom0 + 1 and q("select count(*) from domicilios_clientes")[0][0] == n_lnk0 + 1)

# ---- B) domicilio de un solo cliente, notas que SI cambian: se edita en el lugar (no hay a quien aislar)
r = cli.put(f"/clientes/{uu(CLI1)}/domicilios/{d1}", json=ficha(notas_logistica="Tocar timbre 2", observaciones="Portón verde"))
check(f"B: cambiar de verdad las notas de un domicilio de un solo cliente lo edita en el lugar (mismo id) [{r.status_code}]", r.status_code == 200 and r.json().get("id") == d1)
check("B: las notas quedaron guardadas y sigue habiendo 1 solo domicilio nuevo", q("select notas_logistica, observaciones from domicilios where id=?", h(d1)) == [("Tocar timbre 2", "Portón verde")] and q("select count(*) from domicilios")[0][0] == n_dom0 + 1)

# ---- C) domicilio COMPARTIDO por dos clientes: copy-on-write (la bifurcacion de siempre) solo si las notas cambian de verdad
q_con = sqlite3.connect(T); q_con.execute("insert into domicilios_clientes (cliente_id, domicilio_id, flags, es_predeterminado) values (?, ?, 2097152, 0)", (CLI2, h(d1))); q_con.commit(); q_con.close()
r = cli.put(f"/clientes/{uu(CLI1)}/domicilios/{d1}", json=ficha(notas_logistica="Tocar timbre 2", observaciones="Portón verde"))
check(f"C: compartido y SIN cambio de notas: no bifurca [{r.status_code}] mismo id={r.json().get('id') == d1}", r.status_code == 200 and r.json().get("id") == d1 and q("select count(*) from domicilios")[0][0] == n_dom0 + 1)
r = cli.put(f"/clientes/{uu(CLI1)}/domicilios/{d1}", json=ficha(notas_logistica="Solo para el cliente 1: llamar antes", observaciones="Portón verde"))
nuevo = r.json().get("id", "") if r.status_code == 200 else ""
check(f"C: compartido y con notas que cambian: bifurca (copy-on-write), el cliente 1 pasa a su copia [{r.status_code}]", r.status_code == 200 and bool(nuevo) and nuevo != d1 and q("select count(*) from domicilios_clientes where cliente_id=? and domicilio_id=?", CLI1, h(nuevo))[0][0] == 1)
check("C: el cliente 2 sigue con el domicilio original, con sus notas sin tocar", q("select domicilio_id from domicilios_clientes where cliente_id=? and domicilio_id=?", CLI2, h(d1)) != [] and q("select notas_logistica from domicilios where id=?", h(d1)) == [("Tocar timbre 2",)])
check("C: la copia tiene las notas nuevas y el cliente 1 ya no apunta al original", nuevo and q("select notas_logistica from domicilios where id=?", h(nuevo)) == [("Solo para el cliente 1: llamar antes",)] and q("select count(*) from domicilios_clientes where cliente_id=? and domicilio_id=?", CLI1, h(d1))[0][0] == 0)

del cli; eng.dispose()
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
