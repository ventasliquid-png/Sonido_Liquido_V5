"""Auditoria CA H1 (S881): guardar un pedido NO debe reescribir los renglones de una factura que ya tiene CAE aunque este guardada
como BORRADOR (ingesta vieja, MODO ESPEJO). Sobre una COPIA de la base de P del 06/10 (35 facturas BORRADOR con CAE reales)."""
import sys, os, shutil, sqlite3, glob
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
TMP = os.path.join(RAIZ, "scratch", "test_espejo_cae_tmp.db")
shutil.copyfile(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261008_1224.db", TMP)   # estado ANTES de las migraciones 051-058 (la copia mas nueva ya las tiene)
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
def snap(fid):
    its = q("select descripcion, cantidad, precio_unitario_neto, subtotal_neto from facturas_items where factura_id=? order by id", fid)
    tot = q("select total, neto_gravado, iva_21 from facturas where id=?", fid)[0]
    return (tuple(its), tot)
def body(pid):
    return [{"id": i, "producto_id": pr, "cantidad": ca, "precio_unitario": pu, "descuento_porcentaje": dp, "descuento_importe": di}
            for i, pr, ca, pu, dp, di in q("select id, producto_id, cantidad, precio_unitario, descuento_porcentaje, descuento_importe from pedidos_items where pedido_id=? order by id", pid)]

# ---- las 35 facturas con CAE guardadas como BORRADOR: guardar su pedido sin tocarlo no las cambia ----
facturas = q("select id, numero_comprobante, pedido_id from facturas where estado='BORRADOR' and cae is not null and trim(cae)!='' and pedido_id is not null order by numero_comprobante")
check(f"la copia trae las facturas BORRADOR con CAE reales ({len(facturas)})", len(facturas) >= 30)
antes = {fid: snap(fid) for fid, _, _ in facturas}
pedidos_guardados = set(); fallos_http = []; huerfanas = []
for fid, num, pid in facturas:
    if not q("select 1 from pedidos where id=?", pid):
        huerfanas.append(num); continue          # la factura apunta a un pedido que ya no existe (datos de P)
    if pid in pedidos_guardados: continue
    pedidos_guardados.add(pid)
    r = c.patch(f"/pedidos/{pid}", json={"items": body(pid)})
    if r.status_code != 200: fallos_http.append((num, pid, r.status_code))
check(f"se guardaron sin error los {len(pedidos_guardados)} pedidos de esas facturas (fallos: {fallos_http})", not fallos_http)
check(f"hallazgo de datos: facturas con CAE cuyo pedido ya NO existe: {huerfanas} (2546 y 2547: pedidos #44 y #51)", sorted(huerfanas) == [2546, 2547])
cambiadas = [(num, ) for fid, num, pid in facturas if num not in huerfanas and snap(fid) != antes[fid]]
check(f"NINGUNA de las facturas con CAE cambio tras guardar su pedido (cambiaron {len(cambiadas)}: {[x[0] for x in cambiadas][:12]})", not cambiadas)

# ---- un BORRADOR genuino (sin CAE) sigue sincronizandose con el pedido, como diseñado en V5.9 ----
sin_cae = q("""select f.id, f.pedido_id from facturas f where f.estado='BORRADOR' and (f.cae is null or trim(f.cae)='') and f.pedido_id is not null
               and (select count(*) from pedidos_items i where i.pedido_id=f.pedido_id) >= 1 order by f.numero_comprobante desc, f.created_at desc limit 1""")
check("hay un BORRADOR sin CAE para probar que el espejo legitimo sigue andando", bool(sin_cae))
if sin_cae:
    fid, pid = sin_cae[0]
    it = body(pid); it[0]["cantidad"] = it[0]["cantidad"] + 1
    r = c.patch(f"/pedidos/{pid}", json={"items": it})
    its = q("select cantidad from facturas_items where factura_id=? order by id", fid)
    check(f"BORRADOR sin CAE: tras cambiar el pedido [{r.status_code}] la factura tiene la cantidad nueva ({its[0][0]} == {it[0]['cantidad']})", r.status_code == 200 and its and its[0][0] == it[0]["cantidad"])

del c; eng.dispose()
try: os.remove(TMP)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
