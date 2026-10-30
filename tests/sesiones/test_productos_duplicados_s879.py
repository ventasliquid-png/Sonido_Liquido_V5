"""Card #152 (S879): duplicados de producto. Normalizacion propia (numeros, unidades, talles), migracion 048 sobre una
COPIA de la base de P, alta por la API y sugerencias. No toca normalize_name (clientes)."""
import sys, os, shutil, sqlite3, glob, subprocess
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)

from backend.productos.normalizacion import normalizar_producto as N, similitud as S, UMBRAL_SUGERENCIA
from backend.core.utils.text import normalize_name

# ---------- funciones puras ----------
check("Bidon 5 L  !=  Bidon 1 L  (antes daban igual)", N("Bidon 5 L") != N("Bidon 1 L"))
check("Alcohol 70 botella 1 litro  !=  Alcohol 70 botella 5 litro", N("Alcohol 70 botella 1 litro") != N("Alcohol 70 botella 5 litro"))
check("Bidón 5 lts == bidon 5 litros == 5L bidon (unidad escrita de cualquier forma)", N("Bidón 5 lts") == N("bidon 5 litros") == N("5L bidon"))
check("Guante Talle M  !=  Guante Talle L", N("Guante nitrilo Talle M") != N("Guante nitrilo Talle L"))
check("Talle L != Talle XL", N("Guante Talle L") != N("Guante Talle XL"))
check("acentos, mayusculas y orden no importan: Barbijo Cónico == conico BARBIJO", N("Barbijo Cónico") == N("conico BARBIJO"))
check("ruido (x, de, por, con) no cuenta: Pack camilleros x 2 rollos == Pack camilleros 2 rollos", N("Pack camilleros x 2 rollos") == N("Pack camilleros 2 rollos"))
check("decimales: 1,5 L == 1.5 lts", N("Soda 1,5 L") == N("Soda 1.5 lts"))
check("1,5 L != 15 L", N("Soda 1,5 L") != N("Soda 15 L"))
check("«botella de litro» == «botella 1 litro» (litro suelto = 1 litro)", N("Surizime L5 botella de litro") == N("Surizime L5 botella 1 litro"))
check("L5 != L10 (codigo de producto)", N("Surizime L5 botella") != N("Surizime L10 botella"))
check("porcentaje se conserva: Alcohol 70 % != Alcohol 96 %", N("Alcohol 70 % bidon") != N("Alcohol 96 % bidon"))
check("500 ml == 500 cc", N("Agua 500 ml") == N("agua 500 cc"))
check("100 u == 100 unidades", N("Guante caja 100 u") == N("guante caja 100 unidades"))
check("vacio / None / solo ruido -> ''", N("") == "" and N(None) == "" and N("de la") == "")
check("la clave entra en nombre_canon (<= 300)", len(N("a " * 400)) <= 300)
# los clientes siguen igual: normalize_name NO se toco
check("normalize_name (clientes) sin cambios: sigue siendo la bolsa de palabras", normalize_name("EL TALLER S.R.L.") == "ELSRLTALLER" and normalize_name("Bidon 5 L") == normalize_name("Bidon 1 L"))

# ---------- similitud (sugerir, nunca bloquear) ----------
caso = S("Surgizime L5 botella 1 litro", "Surizime L5 botella de litro")
check(f"typo + «de»: Surgizime L5 botella 1 litro ~ Surizime L5 botella de litro ({caso:.2f} >= {UMBRAL_SUGERENCIA})", caso >= UMBRAL_SUGERENCIA)
check("L5 vs L10 -> 0 (medida distinta, no es el mismo)", S("Surizime L5 botella", "Surizime L10 botella") == 0.0)
check("1 litro vs 5 litros -> 0", S("Surizime L5 botella 1 litro", "Surizime L5 botella 5 litros") == 0.0)
check("talle M vs talle L -> 0 (no se sugiere el talle equivocado)", S("Guante nitrilo Talle M", "Guante nitrilo Talle L") == 0.0)
check("plural: Barbijos rectos ~ Barbijo recto", S("Barbijos rectos", "Barbijo recto") >= UMBRAL_SUGERENCIA)
check("productos distintos no se sugieren: Cofia Descartable vs Cubrezapatos par", S("Cofia Descartable", "Cubrezapatos par") < UMBRAL_SUGERENCIA)
check("identico -> 1.0", S("Barbijo Cónico", "barbijo conico") == 1.0)

# ---------- migracion 048 sobre una copia de la base de P ----------
ult = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261006_1600.db"   # estado ANTES de la 048 (la copia mas nueva de P ya la tiene)
TMP = os.path.join(RAIZ, "scratch", "test_prod_dup_tmp.db")
copiar_p(ult, TMP)
con = sqlite3.connect(TMP)
nombres0 = con.execute("select id, nombre, sku, rubro_id from productos order by id").fetchall()
n0 = len(nombres0)
con.close()
env = dict(os.environ); env["DATABASE_URL"] = "sqlite:///" + TMP; env["PYTHONIOENCODING"] = "utf-8"
r = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_048_productos_nombre_canon.py")], capture_output=True, text=True, encoding="utf-8", env=env)
print(r.stdout.strip())
check(f"migracion 048: sale 0 y registra la base [{r.returncode}]", r.returncode == 0 and "OK" in r.stdout)
r2 = subprocess.run([sys.executable, os.path.join(RAIZ, "scripts", "migrate_048_productos_nombre_canon.py")], capture_output=True, text=True, encoding="utf-8", env=env)
check("migracion 048: la segunda corrida se saltea (idempotente)", r2.returncode == 0 and "SKIP" in r2.stdout)
con = sqlite3.connect(TMP)
filas = con.execute("select id, nombre, nombre_canon, sku, rubro_id from productos order by id").fetchall()
check(f"los {n0} productos siguen (misma cantidad) con el mismo nombre, SKU y rubro", len(filas) == n0 and [(a, b, d, e) for a, b, c, d, e in filas] == nombres0)
check("ningun producto con la clave en NULL o vacia", all(c for _, _, c, _, _ in filas))
check("la clave de cada producto es la de la funcion nueva", all(c == N(n) for _, n, c, _, _ in filas))
claves = {}
for i, n, c, _, _ in filas: claves.setdefault(c, []).append(n)
dups = {c: v for c, v in claves.items() if len(v) > 1}
check(f"entre los {n0} productos reales de P solo chocan DUPLICADOS REALES (mismo nombre salvo mayusculas/espacios): {len(dups)} grupo(s)",
      all(len({" ".join(x.upper().split()) for x in v}) == 1 for v in dups.values()))
for c, v in dups.items(): print("      duplicado real:", v)
# sugerencias entre productos reales: lista para revisar a ojo
pares = []
for i, (_, a, _, _, _) in enumerate(filas):
    for _, b, _, _, _ in filas[i + 1:]:
        sc = S(a, b)
        if sc >= UMBRAL_SUGERENCIA: pares.append((round(sc, 2), a, b))
print(f"      pares de productos reales que el sistema SUGERIRIA como parecidos ({len(pares)}):")
for p in sorted(pares, reverse=True)[:12]: print("        ", p)
con.close()

# ---------- API sobre la copia ----------
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
eng = create_engine(f"sqlite:///{TMP}"); Ses = sessionmaker(bind=eng)
def ov():
    db = Ses()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
c = TestClient(app, raise_server_exceptions=False)
rubro = filas and sqlite3.connect(TMP).execute("select rubro_id from productos limit 1").fetchone()[0]
def alta(nombre):
    return c.post("/productos", json={"nombre": nombre, "rubro_id": rubro, "costos": {"costo_reposicion": 100}})
r = alta("Zzprueba Bidon 5 L"); check(f"alta «Zzprueba Bidon 5 L»: 200 [{r.status_code}]", r.status_code == 200)
r = alta("Zzprueba Bidon 1 L"); check(f"alta «Zzprueba Bidon 1 L» (otra presentacion): 200 y no 409 [{r.status_code}]", r.status_code == 200)
r = alta("zzprueba bidón 5 litros"); check(f"alta del MISMO producto escrito distinto: 409 [{r.status_code}]", r.status_code == 409)
r = alta("Zzprueba Guante Talle M"); check(f"alta talle M: 200 [{r.status_code}]", r.status_code == 200)
r = alta("Zzprueba Guante Talle L"); check(f"alta talle L (antes bloqueada): 200 [{r.status_code}]", r.status_code == 200)
r = alta("Zzprueba Surizime L5 botella de litro"); check(f"alta Surizime: 200 [{r.status_code}]", r.status_code == 200)
r = alta("Zzprueba Surgizime L5 botella 1 litro")
check(f"alta con typo: NO se bloquea (la sugerencia es aparte) [{r.status_code}]", r.status_code == 200)
# sugerencias por la API (la ruta /similares no la pisa /{producto_id})
r = c.get("/productos/similares", params={"nombre": "Zzprueba Surgizime L5 botella 1 litro"})
check(f"GET /productos/similares: 200 y no 422 [{r.status_code}]", r.status_code == 200)
nombres = [x["nombre"] for x in r.json()] if r.status_code == 200 else []
check(f"sugiere el producto parecido ({nombres})", "Zzprueba Surizime L5 botella de litro" in nombres)
r = c.get("/productos/similares", params={"nombre": "Zzprueba Guante Talle XL"})
check(f"talle XL no sugiere ni M ni L [{[x['nombre'] for x in r.json()]}]", r.status_code == 200 and not [x for x in r.json() if "Guante" in x["nombre"]])
# clave automatica en cualquier camino de alta y al renombrar
from backend.productos import models as pm
db = Ses()
p = pm.Producto(nombre="Zzprueba fallback Detergente 5 L", rubro_id=rubro, activo=True, sku=987654)
db.add(p); db.commit(); pid = p.id
check("producto creado por otro camino (ORM directo) recibe su nombre_canon", p.nombre_canon == N("Zzprueba fallback Detergente 5 L"))
db.close()
r = c.put(f"/productos/{pid}", json={"nombre": "Zzprueba fallback Detergente 10 L"})
check(f"renombrar por la API [{r.status_code}]", r.status_code == 200)
canon = sqlite3.connect(TMP).execute("select nombre_canon from productos where id=?", (pid,)).fetchone()[0]
check("al renombrar, nombre_canon sigue al nombre", canon == N("Zzprueba fallback Detergente 10 L"))
r = alta("Zzprueba fallback Detergente 10 L"); check(f"el producto del camino alternativo (renombrado) SI cuenta para duplicados: 409 [{r.status_code}]", r.status_code == 409)
r = alta("Zzprueba fallback Detergente 5 L"); check(f"y el nombre viejo quedo libre: 200 [{r.status_code}]", r.status_code == 200)

del c
eng.dispose()
try: os.remove(TMP)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
