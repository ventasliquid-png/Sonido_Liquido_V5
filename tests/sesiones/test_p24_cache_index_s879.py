"""P24 (S879): index.html se sirve con Cache-Control: no-cache (revalida siempre); los bundles con hash y el resto no cambian."""
import sys, os, glob
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
from backend.main import app, static_dir
from fastapi.testclient import TestClient
c = TestClient(app, raise_server_exceptions=False)
check(f"existe la SPA compilada en {os.path.basename(os.path.dirname(static_dir))}/static", os.path.isfile(os.path.join(static_dir, "index.html")))
r = c.get("/")
check(f"GET / -> 200 [{r.status_code}] y es el index.html", r.status_code == 200 and b"<div id=\"app\"" in r.content)
check(f"GET / lleva Cache-Control: no-cache [{r.headers.get('cache-control')}]", r.headers.get("cache-control") == "no-cache")
r2 = c.get("/index.html")
check(f"GET /index.html lleva Cache-Control: no-cache [{r2.headers.get('cache-control')}]", r2.status_code == 200 and r2.headers.get("cache-control") == "no-cache")
r3 = c.get("/una-ruta-del-router-de-vue")
check(f"ruta de la SPA (fallback a index.html) tambien [{r3.headers.get('cache-control')}]", r3.status_code == 200 and r3.headers.get("cache-control") == "no-cache")
etag = r.headers.get("etag")
check(f"sigue habiendo ETag [{etag}]", bool(etag))
check(f"index.html es chico: reenviarlo entero en cada carga no cuesta nada ({len(r.content)} bytes)", len(r.content) < 5000)
fav = os.path.join(static_dir, "favicon.svg")
if os.path.isfile(fav):
    r5 = c.get("/favicon.svg")
    check(f"otros archivos de static NO cambian (favicon sin no-cache) [{r5.headers.get('cache-control')}]", r5.status_code == 200 and r5.headers.get("cache-control") != "no-cache")
js = glob.glob(os.path.join(static_dir, "assets", "*.js"))
if js:
    r6 = c.get("/assets/" + os.path.basename(js[0]))
    check(f"los bundles con hash NO cambian (sin no-cache) [{r6.headers.get('cache-control')}]", r6.status_code == 200 and r6.headers.get("cache-control") != "no-cache")
rh = c.get("/health")
check(f"/health responde (lo usa la espera del lanzador) [{rh.status_code}]", rh.status_code == 200)
r7 = c.get("/ruta-api-inexistente-que-no-existe-xyz")
check(f"rutas desconocidas siguen sirviendo la SPA, no 404 [{r7.status_code}]", r7.status_code == 200)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
