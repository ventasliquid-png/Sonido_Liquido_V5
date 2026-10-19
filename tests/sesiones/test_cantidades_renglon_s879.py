"""Card #154 (S879): pedido / remitido / facturado por renglon, guarda de edicion y absorcion al armar el remito.
Sobre una COPIA de la base de P de hoy (datos reales). Nunca toca bases vivas."""
import sys, os, shutil, re, sqlite3, glob, itertools
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from backend.facturacion.models import Factura, FacturaItem
from backend.pedidos.models import PedidoItem, Pedido
from backend.remitos.models import RemitoItem
from backend.pedidos.cantidades import facturado_por_renglon

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
TMP = os.path.join(RAIZ, "scratch", "test_cantidades_tmp.db")
copiar_p(sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_*.db"))[-1], TMP)
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
def sql(s, *a):
    con = sqlite3.connect(TMP); con.execute(s, a); con.commit(); con.close()

LIBRES = """select p.id, (p.flags_estado & 4096) > 0, (select count(*) from pedidos_items i where i.pedido_id=p.id)
  from pedidos p where p.id not in (select pedido_id from remitos where estado != 'ANULADO') and p.estado != 'ANULADO' order by p.id"""
usados = set()
def libre(rosa=False, min_items=1):
    for pid, r, n in q(LIBRES):
        if pid in usados or bool(r) != rosa or n < min_items: continue
        usados.add(pid); return pid
    return None
def items(pid): return [r[0] for r in q("select id from pedidos_items where pedido_id=? order by id", pid)]
def fijar(pi, cant): sql("update pedidos_items set cantidad=?, subtotal=precio_unitario*? where id=?", cant, cant, pi)

num = itertools.count(880001)
db = S()
def factura(pid, pi, cant, tipo="FACTURA_B", estado="AUTORIZADA_AFIP"):
    ped = db.get(Pedido, pid)
    f = Factura(cliente_id=ped.cliente_id, pedido_id=pid, tipo_comprobante=tipo, estado=estado, punto_venta=9999, numero_comprobante=next(num))
    db.add(f); db.flush()
    db.add(FacturaItem(factura_id=f.id, pedido_item_id=pi, descripcion="prueba", cantidad=cant, precio_unitario_neto=1.0, subtotal_neto=cant))
    db.commit(); return f.id
def nums(pi):
    db.expire_all(); it = db.get(PedidoItem, pi)
    return dict(rem=round(it.cantidad_remitida, 4), fac=round(it.cantidad_facturada, 4), acre=round(it.cantidad_acreditada, 4), neta=round(it.cantidad_facturada_neta, 4),
                sin_rem=round(it.facturado_sin_remitir, 4), rem_sin=round(it.remitido_sin_facturar, 4), piso=round(it.cantidad_minima_editable, 4))
def body_items(pid, cambios=None, quitar=None):
    out = []
    for i, prod, cant, pu in q("select id, producto_id, cantidad, precio_unitario from pedidos_items where pedido_id=? order by id", pid):
        if quitar and i in quitar: continue
        out.append({"id": i, "producto_id": prod, "cantidad": (cambios or {}).get(i, cant), "precio_unitario": pu, "descuento_porcentaje": 0.0, "descuento_importe": 0.0})
    return out
def cant_db(pi): return q("select cantidad from pedidos_items where id=?", pi)[0][0]

# ---------- A) pedido con dos renglones: sin facturas, todo en cero ----------
P1 = libre(min_items=2); X, Y = items(P1)[:2]; fijar(X, 20); fijar(Y, 5)
n = nums(X); check(f"sin facturas: todo en cero {n}", all(v == 0 for v in n.values()))
factura(P1, X, 20, tipo="FACTURA_B", estado="BORRADOR")
n = nums(X); check(f"un BORRADOR NO cuenta como facturado {n}", n["fac"] == 0 and n["piso"] == 0)
factura(P1, X, 50, estado="ANULADA")
n = nums(X); check(f"una factura ANULADA tampoco {n}", n["fac"] == 0)

# ---------- B) factura vigente de 10 sobre un pedido de 20, antes de cualquier remito ----------
factura(P1, X, 10)
n = nums(X); check(f"factura vigente 10: facturada 10, facturado sin remitir 10, piso 10, nada remitido {n}", (n["fac"], n["sin_rem"], n["piso"], n["rem"], n["rem_sin"]) == (10, 10, 10, 0, 0))
r = c.patch(f"/pedidos/items/{X}", json={"cantidad": 8}); check(f"PATCH /pedidos/items: bajar a 8 (< facturado 10) -> 400 CANTIDAD_BAJO_FACTURADO [{r.status_code}]", r.status_code == 400 and "CANTIDAD_BAJO_FACTURADO" in r.text)
check("y no se grabó nada: la cantidad sigue en 20", cant_db(X) == 20)
r = c.patch(f"/pedidos/{P1}", json={"items": body_items(P1, {X: 5})}); check(f"PATCH /pedidos/id (el Guardar del canvas): bajar a 5 -> 400 [{r.status_code}]", r.status_code == 400 and "CANTIDAD_BAJO_FACTURADO" in r.text)
check("el mensaje habla de nota de crédito", "nota de crédito" in r.text)
check("y no se grabó nada: la cantidad sigue en 20", cant_db(X) == 20)
r = c.patch(f"/pedidos/{P1}", json={"items": body_items(P1, quitar={X})}); check(f"PATCH /pedidos/id: quitar el renglón facturado -> 400 [{r.status_code}]", r.status_code == 400 and "CANTIDAD_BAJO_FACTURADO" in r.text and "eliminar" in r.text)
check("el renglón sigue existiendo", q("select count(*) from pedidos_items where id=?", X)[0][0] == 1)
r = c.patch(f"/pedidos/{P1}", json={"items": body_items(P1, {X: 10})}); check(f"bajar JUSTO a lo facturado (10) se puede [{r.status_code}]", r.status_code == 200 and cant_db(X) == 10)
r = c.patch(f"/pedidos/{P1}", json={"items": body_items(P1, {X: 30})}); check(f"subir la cantidad siempre se puede [{r.status_code}]", r.status_code == 200 and cant_db(X) == 30)
r = c.patch(f"/pedidos/{P1}", json={"items": body_items(P1, quitar={Y})}); check(f"quitar un renglón SIN facturar sigue funcionando [{r.status_code}]", r.status_code == 200 and q("select count(*) from pedidos_items where id=?", Y)[0][0] == 0)
fijar(X, 20)

# ---------- C) notas de crédito y de débito ----------
factura(P1, X, 4, tipo="NOTA_CREDITO_B")
n = nums(X); check(f"NC de 4: acreditada 4, neta 6, piso 6 {n}", (n["acre"], n["neta"], n["piso"], n["fac"]) == (4, 6, 6, 10))
factura(P1, X, 3, tipo="NOTA_DEBITO_B")
n = nums(X); check(f"una ND no cuenta (ajusta importes, no cantidades) {n}", (n["fac"], n["acre"], n["neta"]) == (10, 4, 6))
r = c.patch(f"/pedidos/items/{X}", json={"cantidad": 5}); check(f"con la NC, bajar a 5 (< neto 6) sigue rechazado [{r.status_code}]", r.status_code == 400)
r = c.patch(f"/pedidos/items/{X}", json={"cantidad": 6}); check(f"con la NC, bajar a 6 (= neto) se puede [{r.status_code}]", r.status_code == 200 and cant_db(X) == 6)
fijar(X, 20)

# ---------- D) cálculo por lote y sin caché desactualizada ----------
lote = facturado_por_renglon(db, [X, Y, None, 999999999])
check(f"facturado_por_renglon en una sola consulta: {lote}", lote.get(X) == (10.0, 4.0) and 999999999 not in lote)
P2 = libre(); X2 = items(P2)[0]; fijar(X2, 20)
it = db.get(PedidoItem, X2); antes = it.cantidad_facturada
factura(P2, X2, 7)
check(f"sin caché vieja en la misma sesión: antes {antes}, después {it.cantidad_facturada}", antes == 0 and it.cantidad_facturada == 7)

# ---------- E) absorción al armar: factura adelantada a la entrega ----------
P3 = libre(); X3 = items(P3)[0]; fijar(X3, 20); factura(P3, X3, 10)
def armar(pid, pi, cant): return c.post("/remitos/armar", json={"pedido_id": pid, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": pi, "cantidad": cant}]})
def facts(pi): return [r[0] for r in q("select ri.cantidad_facturada from remitos_items ri join remitos r on r.id=ri.remito_id where ri.pedido_item_id=? and r.estado != 'ANULADO' order by ri.id", pi)]
r = armar(P3, X3, 4); check(f"armar 4 con 10 facturados sin remitir: 200 [{r.status_code}]", r.status_code == 200)
check(f"el renglón nace con cantidad_facturada = 4 (absorbió lo facturado) {facts(X3)}", facts(X3) == [4.0])
r = armar(P3, X3, 4); check(f"segundo remito de 4: [{r.status_code}] -> {facts(X3)}", r.status_code == 200 and facts(X3) == [4.0, 4.0])
r = armar(P3, X3, 5); check(f"tercero de 5: solo quedaban 2 por absorber -> {facts(X3)}", r.status_code == 200 and facts(X3) == [4.0, 4.0, 2.0])
n = nums(X3); check(f"balance final: remitido 13, facturado 10, facturado sin remitir 0, remitido sin facturar 3 {n}", (n["rem"], n["fac"], n["sin_rem"], n["rem_sin"]) == (13, 10, 0, 3))
r = armar(P3, X3, 8); check(f"no se puede remitir más que el pedido (20 - 13 = 7 pendientes): 409 [{r.status_code}]", r.status_code == 409)

# ---------- F) sin factura adelantada, todo como antes ----------
P4 = libre(); X4 = items(P4)[0]
r = armar(P4, X4, 1); check(f"sin facturado: el renglón nace con cantidad_facturada 0.0 como siempre [{r.status_code}] {facts(X4)}", r.status_code == 200 and facts(X4) == [0.0])
P5 = libre(); X5 = items(P5)[0]; fijar(X5, 20)
armar(P5, X5, 6); factura(P5, X5, 10)
n = nums(X5); check(f"remito de 6 y después factura de 10: facturado sin remitir 4 (balance, no cruce remito a remito) {n}", (n["rem"], n["fac"], n["sin_rem"], n["rem_sin"]) == (6, 10, 4, 0))
armar(P5, X5, 9); check(f"el remito siguiente (9) absorbe solo los 4 que faltaban {facts(X5)}", facts(X5) == [0.0, 4.0])

# ---------- G) rosa / no aplica: no se absorbe ----------
PR = libre(rosa=True)
if PR:
    XR = items(PR)[0]; fijar(XR, 20); factura(PR, XR, 5)
    r = armar(PR, XR, 3); check(f"pedido ROSA con factura adelantada: el renglón sigue 'no aplica' (NULL) [{r.status_code}] {facts(XR)}", r.status_code == 200 and facts(XR) == [None])
else:
    print("      (no hay pedido rosa libre en la copia: se omite)")
P6 = libre(); X6 = items(P6)[0]; fijar(X6, 20); factura(P6, X6, 10)
r = c.post("/remitos/armar", json={"pedido_id": P6, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": X6, "cantidad": 4, "motivo_no_facturable": "MUESTRA_SIN_CARGO"}]})
check(f"con motivo abierto (muestra) tampoco se absorbe [{r.status_code}] {facts(X6)}", r.status_code == 200 and facts(X6) == [None])

# ---------- H) datos viejos: remitido o facturado MAYOR que lo pedido (en P: renglon 127 del pedido 72, 100 pedidos / 150 remitidos) ----------
fijar(X3, 10)   # P3: remitido 13, facturado 10 -> el pedido quedo en 10 (remitido 13 > pedido 10, como el caso real)
b0 = body_items(P3)
r = c.patch(f"/pedidos/{P3}", json={"items": b0}); check(f"legado: guardar el pedido SIN tocar la cantidad (remitido 13 > pedido 10) no se bloquea [{r.status_code}]", r.status_code == 200 and cant_db(X3) == 10)
r = c.patch(f"/pedidos/{P3}", json={"items": body_items(P3, {X3: 9})}); check(f"legado: BAJARLA (10 -> 9) sí se rechaza, está por debajo de lo remitido [{r.status_code}]", r.status_code == 400)
r = c.patch(f"/pedidos/{P3}", json={"items": body_items(P3, {X3: 12})}); check(f"legado: subirla (10 -> 12) se puede aunque siga debajo de lo remitido [{r.status_code}]", r.status_code == 200 and cant_db(X3) == 12)
fijar(X5, 8)    # P5: remitido 15, facturado 10, pedido 8 (facturado y remitido por encima)
r = c.patch(f"/pedidos/{P5}", json={"items": body_items(P5)}); check(f"legado con facturado 10 > pedido 8: guardar sin tocar -> 200 [{r.status_code}]", r.status_code == 200)
r = c.patch(f"/pedidos/items/{X5}", json={"cantidad": 8}); check(f"legado: PATCH /pedidos/items con la misma cantidad por debajo de lo facturado no agrega un bloqueo nuevo (lo frena la guarda vieja de lo remitido) [{r.status_code}]", r.status_code == 400)

db.close(); del c; eng.dispose()
try: os.remove(TMP)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
