"""Gestion Domicilios (/clientes/hub/list) con bit_identidad NULL heredado de P. Sobre COPIAS, nunca bases vivas."""
import sys, os, shutil, sqlite3, subprocess, gc
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
PRISTINA = r"C:\dev\Sonido_Liquido_V5\scratch\pilot_v5x_P_copia_20260930.db"
TMP = r"C:\dev\Sonido_Liquido_V5\scratch\test_hub_null_tmp.db"
ZUV = "8aeb5a99-8c7d-45e5-b382-7d101ef66958"
copiar_p(PRISTINA, TMP)
eng = create_engine(f"sqlite:///{TMP}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
c = TestClient(app, raise_server_exceptions=False)
def hub():
    r = c.get("/clientes/hub/list"); return r, (r.json() if r.status_code == 200 else [])
def q(sql):
    con = sqlite3.connect(TMP); v = con.execute(sql).fetchall(); con.close(); return v

# 1) solo el codigo: el NULL sigue en la base
check("antes: la base tiene exactamente 1 domicilio con bit_identidad NULL", q("select count(*) from domicilios where bit_identidad is null")[0][0] == 1)
r, lst = hub()
check(f"codigo solo: /clientes/hub/list ya no da 500 [{r.status_code}] y trae los 76 domicilios [{len(lst)}]", r.status_code == 200 and len(lst) == 76)
fila = next((x for x in lst if x["calle"] == "Zuviría"), None)
check("codigo solo: la fila Zuviria 5747 sale con bit_identidad 0 (NULL tolerado)", fila is not None and fila["bit_identidad"] == 0)

# 2) migracion sobre la misma copia
antes = q("select id, bit_identidad from domicilios order by id")
def migrar():
    env = dict(os.environ, DATABASE_URL=f"sqlite:///{TMP}")
    return subprocess.run([sys.executable, r"scripts\migrate_046_domicilios_bit_identidad_null.py"], env=env, capture_output=True, text=True)
eng.dispose()
m1 = migrar(); check(f"migracion 1: OK [{m1.stdout.strip().splitlines()[-1] if m1.stdout.strip() else m1.stderr[-200:]}]", m1.returncode == 0 and "1 domicilio(s)" in m1.stdout)
despues = q("select id, bit_identidad from domicilios order by id")
cambiadas = [(a, b) for a, b in zip(antes, despues) if a != b]
check(f"migracion: cambia UNA sola fila, la de Zuviria, de NULL a 1 (activa) [{cambiadas}]", len(cambiadas) == 1 and cambiadas[0][0][1] is None and cambiadas[0][1][1] == 1 and cambiadas[0][1][0].replace('-', '') == ZUV.replace('-', ''))
check("migracion: las demas 75 filas quedan idénticas (incluidos los 0)", len(antes) == len(despues) == 76)
check("migracion: ya no queda ningun NULL y la migracion quedo registrada", q("select count(*) from domicilios where bit_identidad is null")[0][0] == 0 and q("select count(*) from _migraciones_aplicadas where id='046_domicilios_bit_identidad_null'")[0][0] == 1)
m2 = migrar(); check("migracion 2 (idempotente): SKIP sin tocar nada", m2.returncode == 0 and "SKIP" in m2.stdout and q("select id, bit_identidad from domicilios order by id") == despues)
eng = create_engine(f"sqlite:///{TMP}"); S = sessionmaker(bind=eng)
r, lst = hub(); fila = next((x for x in lst if x["calle"] == "Zuviría"), None)
check("despues de migrar: hub/list 200 y Zuviria sale ACTIVA (bit_identidad & 1)", r.status_code == 200 and fila and (fila["bit_identidad"] & 1) == 1)
# 3) el resto de la pantalla de logistica del pedido sigue sano
check("logistica del pedido sigue 200 (empresas, nodos)", c.get("/logistica/empresas").status_code == 200 and c.get("/logistica/nodos").status_code == 200)
del c; gc.collect(); eng.dispose()
try: os.remove(TMP)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
