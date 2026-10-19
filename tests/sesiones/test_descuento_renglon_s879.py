"""Card #159 (S879): descuento por renglon por unidad, centavos exactos, porcentaje a 4 decimales y conservado al cambiar la cantidad.
Sobre una COPIA de la base de P de hoy (datos reales, incluido el pedido 122 de Tomy). Nunca toca bases vivas."""
import sys, os, shutil, sqlite3, glob
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.pedidos.descuentos import redondear, descuento_normalizado, importe_conservando_unitario

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)

# ---------- funciones puras ----------
check("redondear(2.675, 2) = 2.68 (el round de Python da 2.67 por el binario)", redondear(2.675, 2) == 2.68)
check("redondear(2.553191489361702, 4) = 2.5532", redondear(2.553191489361702, 4) == 2.5532)
check("descuento_normalizado(2400, 2.553191489361702) = (2400.0, 2.5532)", descuento_normalizado(2400, 2.553191489361702) == (2400.0, 2.5532))
check("descuento_normalizado(2400.008, None) = (2400.01, 0.0)", descuento_normalizado(2400.008, None) == (2400.01, 0.0))
check("descuento_normalizado(None, None) = (0.0, 0.0)", descuento_normalizado(None, None) == (0.0, 0.0))
check("conservar por unidad: 2400 en 2 unidades -> 3 unidades = 3600", importe_conservando_unitario(2400, 2, 3) == 3600.0)
check("conservar por unidad: 2400 en 2 -> 1 unidad = 1200", importe_conservando_unitario(2400, 2, 1) == 1200.0)
check("conservar por unidad: 1000 en 3 -> 4 unidades = 1333.33 (a centavos)", importe_conservando_unitario(1000, 3, 4) == 1333.33)
check("sin descuento previo o sin cantidad previa no inventa nada", importe_conservando_unitario(0, 2, 3) == 0.0 and importe_conservando_unitario(500, 0, 3) == 500.0 and importe_conservando_unitario(None, 2, 3) == 0.0)

# ---------- API sobre la copia de P ----------
TMP = os.path.join(RAIZ, "scratch", "test_descuento_tmp.db")
shutil.copyfile(sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_*.db"))[-1], TMP)
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
def item(i): return q("select cantidad, precio_unitario, descuento_porcentaje, descuento_importe, subtotal from pedidos_items where id=?", i)[0]
def body(pid, cambios):
    out = []
    for i, prod, cant, pu, dp, di in q("select id, producto_id, cantidad, precio_unitario, descuento_porcentaje, descuento_importe from pedidos_items where pedido_id=? order by id", pid):
        it = {"id": i, "producto_id": prod, "cantidad": cant, "precio_unitario": pu, "descuento_porcentaje": dp, "descuento_importe": di}
        it.update(cambios.get(i, {})); out.append(it)
    return out

# el pedido 122 de Tomy (L5 2 x 47000, descuento 2400 y porcentaje de 15 decimales) viene en la copia
fila = q("select id, pedido_id from pedidos_items where pedido_id=122 and descuento_importe > 0")
check(f"el pedido 122 de Tomy esta en la copia con su porcentaje de 15 decimales {fila and q('select descuento_porcentaje from pedidos_items where id=?', fila[0][0])}", bool(fila))
L5, P122 = fila[0]
r = c.patch(f"/pedidos/{P122}", json={"items": body(P122, {})})
check(f"guardar el pedido 122 SIN tocarlo: 200 [{r.status_code}]", r.status_code == 200)
cant, pu, dp, di, sub = item(L5)
check(f"el porcentaje queda a 4 decimales ({dp}) y el importe sigue en 2400.0 ({di}), subtotal {sub}", dp == 2.5532 and di == 2400.0 and sub == 91600.0)
tot = q("select total from pedidos where id=?", P122)[0][0]
check(f"el total del pedido no cambia (221672.0): {tot}", abs(tot - 221672.0) < 0.01)

# guardar tipeando un porcentaje redondeado: el importe llega con fracciones de centavo y se redondea
r = c.patch(f"/pedidos/{P122}", json={"items": body(P122, {L5: {"descuento_porcentaje": 2.5532, "descuento_importe": 2400.008}})})
cant, pu, dp, di, sub = item(L5)
check(f"importe 2400.008 se guarda a centavos: {di} (2400.01) y subtotal {sub}", r.status_code == 200 and di == 2400.01 and abs(sub - 91599.99) < 0.001)
r = c.patch(f"/pedidos/{P122}", json={"items": body(P122, {L5: {"descuento_porcentaje": 2.553191489361702, "descuento_importe": 2400.0}})})

# ajuste de cantidad por /items/{id}: el descuento acompana a la cantidad (por unidad)
r = c.patch(f"/pedidos/items/{L5}", json={"cantidad": 3})
cant, pu, dp, di, sub = item(L5)
check(f"PATCH /pedidos/items: 2 -> 3 unidades [{r.status_code}]: descuento 3600.0 ({di}), subtotal 3 x 47000 - 3600 = 137400 ({sub}), porcentaje intacto ({dp})",
      r.status_code == 200 and di == 3600.0 and sub == 137400.0 and dp == 2.5532)
check(f"precio efectivo por unidad = 45800 ({sub / cant})", abs(sub / cant - 45800.0) < 1e-9)
r = c.patch(f"/pedidos/items/{L5}", json={"cantidad": 1})
cant, pu, dp, di, sub = item(L5)
check(f"y de 3 a 1: descuento 1200.0 ({di}), subtotal 45800 ({sub})", r.status_code == 200 and di == 1200.0 and sub == 45800.0)
r = c.patch(f"/pedidos/items/{L5}", json={"cantidad": 2, "descuento_importe": 1000.005})
cant, pu, dp, di, sub = item(L5)
check(f"si mandan un descuento explicito se respeta (a centavos): {di}", r.status_code == 200 and di == 1000.01)
r = c.patch(f"/pedidos/items/{L5}", json={"precio_unitario": 48000})
cant, pu, dp, di, sub = item(L5)
check(f"cambiar solo el precio no toca el importe ({di}) y recalcula el subtotal ({sub})", r.status_code == 200 and di == 1000.01 and abs(sub - (2 * 48000 - 1000.01)) < 0.001)

# alta de un pedido nuevo con descuentos fraccionados
cli = q("select id from clientes limit 1")[0][0]
prod = q("select id from productos where activo=1 limit 1")[0][0]
import uuid
r = c.post("/pedidos/tactico", json={"cliente_id": str(uuid.UUID(cli)), "items": [
    {"producto_id": prod, "cantidad": 3, "precio_unitario": 47000, "descuento_porcentaje": 2.553191489361702, "descuento_importe": 3600.0049}]})
check(f"POST /pedidos/tactico con descuentos sin redondear: {r.status_code}", r.status_code in (200, 201))
if r.status_code in (200, 201):
    nid = r.json()["id"]
    cant, pu, dp, di, sub = q("select cantidad, precio_unitario, descuento_porcentaje, descuento_importe, subtotal from pedidos_items where pedido_id=?", nid)[0]
    check(f"alta: porcentaje 2.5532 ({dp}), importe 3600.0 ({di}), subtotal 137400.0 ({sub})", dp == 2.5532 and di == 3600.0 and sub == 137400.0)

del c; eng.dispose()
try: os.remove(TMP)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
