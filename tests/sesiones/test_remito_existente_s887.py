r"""S887, pedido de Carlos (15/10): el sistema tiene que decir, en el pedido, si ya tiene remito y cuál es, y el freno del duplicado dice cuál es en vez de mandar a buscarlo en un listado.
(1) GET /remitos/resumen_por_pedido: los remitos vigentes (sin anulados) de cada pedido, para el Tablero de Pedidos.
(2) Un remito (armar; el Remito Manual se retiró en la S893) de un pedido ya remitido se frena con CANTIDAD_EXCEDE_PEDIDO y el aviso nombra el remito que ya existe (número, estado, fecha); si el pedido no tiene remitos, el aviso no aparece.
Sobre una COPIA de la base de P del 15/10 16:01 (el pedido 128 de Wullich tiene el remito 0015-00003027; el 48 no tiene ninguno)."""
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
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261015_1601.db"
os.makedirs(os.path.join(RAIZ, "scratch"), exist_ok=True)
T = os.path.join(RAIZ, "scratch", "test_remito_existente_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
c = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v

# ---- (1) el resumen por pedido
r = c.get("/remitos/resumen_por_pedido")
d = r.json() if r.status_code == 200 else {}
check(f"GET /remitos/resumen_por_pedido responde [{r.status_code}] (la ruta no la tapa /{{remito_id}}) con un diccionario de {len(d)} pedidos", r.status_code == 200 and isinstance(d, dict) and len(d) > 50)
vigentes = q("select count(*) from remitos where estado <> 'ANULADO'")[0][0]
check(f"trae exactamente los remitos vigentes ({sum(len(v) for v in d.values())} de {vigentes}); los anulados no figuran", sum(len(v) for v in d.values()) == vigentes)
anulados = {x[0] for x in q("select id from remitos where estado = 'ANULADO'")}
check("ningún remito anulado aparece en el resumen", not any(x["id"] in anulados for v in d.values() for x in v))
w = d.get("128", [])
check(f"el pedido 128 (Wullich) muestra su remito 0015-00003027 en BORRADOR {w and [(x['numero_legal'], x['estado']) for x in w]}", len(w) == 1 and w[0]["numero_legal"] == "0015-00003027" and w[0]["estado"] == "BORRADOR" and w[0]["fecha_creacion"].startswith("2026-10-15"))
check("un pedido sin remitos (el 48) no figura", "48" not in d)
dos = {k: v for k, v in d.items() if len(v) >= 2}
check(f"los pedidos con dos remitos vigentes (72 y 115) los traen ordenados por fecha: {sorted(dos)}", set(dos) == {"72", "115"} and all(v[0]["fecha_creacion"] <= v[1]["fecha_creacion"] for v in dos.values()))
check("el listado normal de remitos y el remito suelto siguen respondiendo (la ruta nueva no rompió el orden de rutas)",
      c.get("/remitos/").status_code == 200 and c.get(f"/remitos/{w[0]['id']}").status_code == 200)

# ---- (2) el freno dice cuál remito ya existe
antes = q("select count(*) from remitos")[0][0]
r = c.post("/remitos/armar", json={"pedido_id": 128, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": 246, "cantidad": 360}]})
det = (r.json() or {}).get("detail", "") if r.headers.get("content-type", "").startswith("application/json") else r.text
check(f"armar un remito de un pedido ya remitido (128) se frena [{r.status_code}] con CANTIDAD_EXCEDE_PEDIDO", r.status_code == 409 and det.startswith("CANTIDAD_EXCEDE_PEDIDO"))
check(f"el aviso nombra el remito que ya existe y dónde reimprimirlo: {det[-215:]!r}", "El Pedido #128 ya tiene remito: 0015-00003027 (borrador, del 15/10/2026)" in det and "reimprimilo desde ahí" in det and "«Entregas y remitos»" in det)
check("el frenado no dejó ningún remito nuevo", q("select count(*) from remitos")[0][0] == antes)
r = c.post("/remitos/armar", json={"pedido_id": 48, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": 90, "cantidad": 9999}]})
det = (r.json() or {}).get("detail", "") if r.headers.get("content-type", "").startswith("application/json") else r.text
check(f"un pedido SIN remitos (el 48) que se pasa de lo pedido se frena igual, pero sin el aviso de remito existente [{r.status_code}]",
      r.status_code == 409 and det.startswith("CANTIDAD_EXCEDE_PEDIDO") and "ya tiene remito" not in det)
check("una cantidad que sí cabe en el pedido sin remitos (el 48) arma el remito como siempre", c.post("/remitos/armar", json={"pedido_id": 48, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": 90, "cantidad": 60}]}).status_code == 200)
r2 = c.get("/remitos/resumen_por_pedido").json()
check(f"y el resumen ya lo muestra: el 48 pasa a tener 1 remito {r2.get('48') and [(x['estado'], x['numero_legal']) for x in r2['48']]}", len(r2.get("48", [])) == 1 and r2["48"][0]["estado"] == "ENTREGADO")

app.dependency_overrides.clear()
try: eng.dispose(); os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
