r"""migrate_063 (S888, Card #177 v3): agrega pedidos_items.kit_grupo (INTEGER NULL) para el numero de kit de cada renglon. Sobre COPIAS CRUDAS de la base de P del 16/10 15:24 (sin la columna).
Verifica: lo que agrega, que NO cambia ningun dato, que es idempotente, las guardas (sin tabla, columna ya existente, bit 47 ya prendido), que auto_migrar la descubre y que el codigo de hoy
(ORM) lee la base migrada."""
import sys, os, shutil, sqlite3, subprocess, hashlib
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261016_1524.db"
SCRIPT = os.path.join(RAIZ, "scripts", "migrate_063_pedidos_items_kit_grupo.py")
os.makedirs(os.path.join(RAIZ, "scratch"), exist_ok=True)
def copia(n):
    p = os.path.join(RAIZ, "scratch", n); shutil.copyfile(ORIG, p); return p     # copia CRUDA: sin el ayudante _esquema_p
def migrar(db):
    r = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True, encoding="utf-8", errors="replace", env=dict(os.environ, DATABASE_URL="sqlite:///" + db, PYTHONIOENCODING="utf-8"))
    return r.returncode, r.stdout + r.stderr
def q(db, sql, *a):
    con = sqlite3.connect(db); v = con.execute(sql, a).fetchall(); con.close(); return v
def huella(db, tabla, sin=()):
    """hash del contenido de una tabla, sin las columnas indicadas"""
    cols = [r[1] for r in q(db, f"pragma table_info({tabla})") if r[1] not in sin]
    h = hashlib.sha256()
    for fila in q(db, f"select {', '.join(cols)} from {tabla} order by 1"): h.update(repr(fila).encode())
    return h.hexdigest()
TABLAS = ["pedidos", "remitos", "remitos_items", "facturas", "facturas_items", "clientes", "productos", "domicilios"]

A = copia("test_migrate_063_a.db")
check("partida: la copia cruda NO tiene la columna ni la migracion registrada", "kit_grupo" not in {r[1] for r in q(A, "pragma table_info(pedidos_items)")} and q(A, "select count(*) from _migraciones_aplicadas where id='063_pedidos_items_kit_grupo'")[0][0] == 0)
antes = {t: huella(A, t) for t in TABLAS}; antes["pedidos_items"] = huella(A, "pedidos_items"); filas = q(A, "select count(*) from pedidos_items")[0][0]
n_mig = q(A, "select count(*) from _migraciones_aplicadas")[0][0]
rc, out = migrar(A)
check(f"corre sin error [{rc}]: {[l for l in out.splitlines() if 'OK --' in l]}", rc == 0 and "[migrate_063] OK --" in out and "ERROR" not in out)
col = {r[1]: r for r in q(A, "pragma table_info(pedidos_items)")}
check(f"la columna kit_grupo existe, es INTEGER y admite NULL (notnull=0) {col.get('kit_grupo')}", "kit_grupo" in col and col["kit_grupo"][2].upper() == "INTEGER" and col["kit_grupo"][3] == 0)
check(f"los {filas} renglones quedan con kit_grupo NULL (no se inventa ningun kit)", q(A, "select count(*) from pedidos_items where kit_grupo is not null")[0][0] == 0 and q(A, "select count(*) from pedidos_items")[0][0] == filas)
check("la migracion queda registrada (sesion 888) y es la unica nueva", q(A, "select nro_sesion from _migraciones_aplicadas where id='063_pedidos_items_kit_grupo'") == [(888,)] and q(A, "select count(*) from _migraciones_aplicadas")[0][0] == n_mig + 1)
check("no cambia NINGUN dato: pedidos_items (salvo la columna nueva) y pedidos, remitos, remitos_items, facturas, facturas_items, clientes, productos y domicilios quedan identicos",
      huella(A, "pedidos_items", sin=("kit_grupo",)) == antes["pedidos_items"] and all(huella(A, t) == antes[t] for t in TABLAS))
rc2, out2 = migrar(A)
check(f"es idempotente: la segunda corrida se saltea [{rc2}] y no cambia nada", rc2 == 0 and "SKIP" in out2 and q(A, "select count(*) from _migraciones_aplicadas")[0][0] == n_mig + 1 and huella(A, "pedidos_items", sin=("kit_grupo",)) == antes["pedidos_items"])

# columna que ya existia (alguien la agrego a mano): no falla y se registra
B = copia("test_migrate_063_b.db"); con = sqlite3.connect(B); con.execute("ALTER TABLE pedidos_items ADD COLUMN kit_grupo INTEGER"); con.execute("UPDATE pedidos_items SET kit_grupo = 4 WHERE id = (SELECT MIN(id) FROM pedidos_items)"); con.commit(); con.close()
rc, out = migrar(B)
check(f"con la columna ya agregada a mano: no falla, no la vuelve a crear ni borra su dato, y registra la migracion [{rc}]", rc == 0 and "ya existe" in out and q(B, "select count(*) from pedidos_items where kit_grupo = 4")[0][0] == 1
      and q(B, "select count(*) from _migraciones_aplicadas where id='063_pedidos_items_kit_grupo'")[0][0] == 1)

# un pedido con el bit 47 ya prendido (estaba libre: no deberia pasar) -> aviso, sin frenar
C = copia("test_migrate_063_c.db"); con = sqlite3.connect(C); con.execute("UPDATE pedidos SET flags_estado = flags_estado | ? WHERE id = (SELECT MIN(id) FROM pedidos)", (1 << 47,)); con.commit(); con.close()
rc, out = migrar(C)
check(f"si algun pedido ya tuviera el bit 47: avisa pero migra [{rc}]", rc == 0 and "AVISO" in out and "bit 47" in out and "kit_grupo" in {r[1] for r in q(C, "pragma table_info(pedidos_items)")})

# base sin la tabla (no es de V5 o esta desactualizada): no hace nada y NO se registra
D = os.path.join(RAIZ, "scratch", "test_migrate_063_d.db")
if os.path.exists(D): os.remove(D)
con = sqlite3.connect(D); con.execute("CREATE TABLE otra_cosa (id INTEGER)"); con.commit(); con.close()
rc, out = migrar(D)
check(f"sin la tabla pedidos_items: avisa, sale 0 y NO queda registrada (se reintenta en el proximo arranque) [{rc}]", rc == 0 and "AVISO" in out and q(D, "select count(*) from _migraciones_aplicadas where id='063_pedidos_items_kit_grupo'")[0][0] == 0)

# auto_migrar la descubre
sys.path.insert(0, os.path.join(RAIZ, "scripts"))
import auto_migrar
ids_ = [m for m, _ in auto_migrar.migraciones_disponibles()]
# [S890] ya no es la ultima: detras vienen 064 y 065. Lo que importa es que se descubre y corre despues de las anteriores (orden por nombre de archivo).
check("auto_migrar descubre la migracion y corre despues de la 062 (orden por nombre de archivo)", "063_pedidos_items_kit_grupo" in ids_
      and ids_.index("063_pedidos_items_kit_grupo") > max(i for i, m in enumerate(ids_) if m.startswith("062_")))

# el codigo de hoy lee la base migrada
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
eng = create_engine(f"sqlite:///{A}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
r = cli.get("/pedidos/"); r2 = cli.get("/pedidos/82")
check(f"el ORM de hoy lee la base migrada: listado y ficha responden 200 y los renglones traen kit_grupo=null [{r.status_code}/{r2.status_code}]",
      r.status_code == 200 and r2.status_code == 200 and all("kit_grupo" in i and i["kit_grupo"] is None for i in r2.json()["items"]))
app.dependency_overrides.clear(); eng.dispose()
for f in (A, B, C, D):
    try: os.remove(f)
    except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
