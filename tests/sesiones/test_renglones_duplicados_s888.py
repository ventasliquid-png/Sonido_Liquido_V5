r"""S888, Card #179 (prerrequisito de la Card #177, kits del pedido): un pedido puede tener DOS renglones del MISMO producto (el kit del pedido los usa), y el Remito Manual y la ingesta
en modo VINCULAR_PARCIAL los emparejaban por nombre / producto y caían siempre en el PRIMERO.
[S893, Carlos 26/10] El Remito Manual se retiró (tag remito-manual-original): sus comprobaciones (1) y (1b) pasaron al armado desde el pedido (POST /remitos/armar), que elige el renglón por
pedido_item_id y por eso nunca se confunde con un renglón repetido; la (2) mide si la guarda de cantidades acumula dentro del mismo remito.
(1) Armado desde el pedido: dos renglones del mismo producto salen cada uno con su cantidad y la guarda juzga el renglón elegido.
(2) La guarda de cantidades acumula lo que ya tomó cada renglón dentro del mismo remito (antes dos líneas de 5 contra un renglón de 8 pasaban las dos).
(3) Ingesta: la guarda de los modos VINCULAR_* y los renglones del remito en VINCULAR_PARCIAL toman, por producto, el primer renglón todavía no usado.
Sobre una COPIA de la base de P del 15/10 16:01 (se le agregan renglones repetidos a los pedidos 48, 123 y 82)."""
import sys, os, shutil, sqlite3, json, uuid, io, re
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
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261015_1601.db"
os.makedirs(os.path.join(RAIZ, "scratch"), exist_ok=True)
T = os.path.join(RAIZ, "scratch", "test_renglones_duplicados_tmp.db"); copiar_p(ORIG, T)
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
def ejecutar(sql, *a):
    con = sqlite3.connect(T); cur = con.execute(sql, a); con.commit(); n = cur.lastrowid; con.close(); return n
def detalle(r): return (r.json() or {}).get("detail", "") if r.headers.get("content-type", "").startswith("application/json") else r.text
def renglon_extra(pedido, producto, cantidad):
    precio = q("select precio_unitario from pedidos_items where pedido_id=? and producto_id=? order by id limit 1", pedido, producto)[0][0] or 0.0
    return ejecutar("insert into pedidos_items (pedido_id, producto_id, cantidad, precio_unitario, descuento_porcentaje, descuento_importe, subtotal, nota) values (?,?,?,?,0,0,?,?)",
                    pedido, producto, cantidad, precio, cantidad * precio, "renglon repetido (prueba S888)")
def items_del_remito(remito_id): return sorted(q("select pedido_item_id, cantidad_remitida from remitos_items where remito_id=?", str(remito_id).replace("-", "")))
def nombre(producto): return q("select nombre from productos where id=?", producto)[0][0]

# ---- partida: pedidos con renglones repetidos del mismo producto
A48 = 90;  B48 = renglon_extra(48, 154, 24.0)      # 48: Jabón Bac, 60 + 24
A123 = 235; B123 = renglon_extra(123, 214, 100.0)  # 123: 360 + 100 del mismo producto
A131 = 253                                         # 131: un solo renglón de 8 (para la guarda que acumula)
A82 = 181; B82 = renglon_extra(82, 175, 40.0)      # 82: veterinarios, 200 (100 ya remitidos) + 40
check(f"partida: los pedidos 48, 123 y 82 tienen dos renglones del mismo producto ({A48}/{B48}, {A123}/{B123}, {A82}/{B82}) y el 131 uno solo",
      len(q("select id from pedidos_items where pedido_id=48 and producto_id=154")) == 2 and len(q("select id from pedidos_items where pedido_id=123 and producto_id=214")) == 2
      and len(q("select id from pedidos_items where pedido_id=82 and producto_id=175")) == 2 and len(q("select id from pedidos_items where pedido_id=131")) == 1)
check("partida: ninguno de los pedidos 48, 123 ni 131 tiene remitos", q("select count(*) from remitos where pedido_id in (48,123,131)")[0][0] == 0)

def armar(pedido, items):
    return c.post("/remitos/armar", json={"pedido_id": pedido, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": i, "cantidad": n} for i, n in items]})

# ---- (1) Armado desde el pedido: dos renglones del mismo producto salen cada uno con SU cantidad
n48 = nombre(154)
r = armar(48, [(A48, 60), (B48, 24)])
rid = r.json().get("id") if r.status_code == 200 else None
check(f"armar el 48 con los dos renglones del mismo producto: se crea [{r.status_code}] {'' if r.status_code == 200 else detalle(r)[:140]}", r.status_code == 200 and rid)
check(f"cada línea tomó SU renglón: {items_del_remito(rid) if rid else None}", rid and items_del_remito(rid) == sorted([(A48, 60.0), (B48, 24.0)]))

# ---- (1b) elegir el segundo renglón: manda el id, aunque el producto sea el mismo
n123 = nombre(214)
r = armar(123, [(B123, 100)])
rid = r.json().get("id") if r.status_code == 200 else None
check(f"armar el 123 con el SEGUNDO renglón: se crea [{r.status_code}] y lleva ese renglón, no el primero: {items_del_remito(rid) if rid else None}", rid and items_del_remito(rid) == [(B123, 100.0)])
r = armar(123, [(B123, 1)])
check(f"la guarda juzga el renglón elegido: el segundo ya está remitido por completo, 1 más se frena [{r.status_code}] con CANTIDAD_EXCEDE_PEDIDO", r.status_code == 409 and detalle(r).startswith("CANTIDAD_EXCEDE_PEDIDO"))
nr = q("select count(*) from remitos")[0][0]
r = armar(123, [(A123, 361)])
check(f"y el primero, que tiene 360 pendientes, rechaza 361 [{r.status_code}]", r.status_code == 409 and detalle(r).startswith("CANTIDAD_EXCEDE_PEDIDO") and "360" in detalle(r) and q("select count(*) from remitos")[0][0] == nr)
r = armar(123, [(A123, 360)])
rid = r.json().get("id") if r.status_code == 200 else None
check(f"los 360 del primer renglón sí salen [{r.status_code}]: {items_del_remito(rid) if rid else None}", rid and items_del_remito(rid) == [(A123, 360.0)])
nr = q("select count(*) from remitos")[0][0]
r = armar(131, [(B48, 1)])
check(f"un pedido_item_id de OTRO pedido se rechaza [{r.status_code}] con RENGLON_AJENO_AL_PEDIDO y no deja remito", r.status_code == 409 and detalle(r).startswith("RENGLON_AJENO_AL_PEDIDO") and q("select count(*) from remitos")[0][0] == nr)

# ---- (2) la guarda acumula lo que ya tomó cada renglón dentro del mismo remito
r = armar(131, [(A131, 5), (A131, 5)])
check(f"dos líneas de 5 contra un único renglón de 8 se frenan [{r.status_code}] (antes pasaban las dos): {detalle(r)[:110]}", r.status_code == 409 and detalle(r).startswith("CANTIDAD_EXCEDE_PEDIDO"))
check("y no quedó ningún remito del pedido 131", q("select count(*) from remitos where pedido_id=131")[0][0] == 0)
p117 = q("select id, producto_id, cantidad from pedidos_items where pedido_id=117 order by id")[0]
r = armar(117, [(p117[0], p117[2])])
check(f"lo de siempre sigue andando: una línea con la cantidad exacta de un renglón único (pedido 117, {p117[2]:g}) sale [{r.status_code}] {'' if r.status_code == 200 else detalle(r)[:140]}", r.status_code == 200)

# ---- (3) ingesta en VINCULAR_PARCIAL: cada línea de la factura toma un renglón distinto del mismo producto
cliente_id = q("select cliente_id from pedidos where id=82")[0][0]
cuit = q("select cuit from clientes where id=?", cliente_id)[0][0]
def raw(items, numero, cae):
    rid = uuid.uuid4().hex
    parsed = {"cliente": {"cuit": cuit}, "factura": {"numero": numero, "cae": cae, "vto_cae": "2026-10-28", "tipo_comprobante": "FACTURA_A", "fecha_emision": "2026-10-16", "total_neto": 0, "total_final": 0}, "items": items}
    con = sqlite3.connect(T)
    con.execute("insert into ingesta_facturas_raw (id, filename, pdf_bytes, audit_status, parsed_data_raw, flags_estado, created_at) values (?, ?, ?, 'RECIBIDO', ?, 0, datetime('now'))", (rid, "t.pdf", b"%PDF-1.4", json.dumps(parsed)))
    con.commit(); con.close(); return rid
def payload(numero, cae, items, pedido, modo="VINCULAR_PARCIAL"):
    return {"cliente": {"id": cliente_id, "cuit": cuit, "razon_social": "X"}, "factura": {"numero": numero, "cae": cae, "vto_cae": "28/10/2026"}, "items": items, "bultos": 1, "valor_declarado": 0.0, "modo_ingesta": modo, "pedido_id_vinculado": pedido}
vet = nombre(175)
lineas = [{"descripcion": vet, "cantidad": 100.0, "precio_unitario": 9750.0, "producto_id": 175}, {"descripcion": vet, "cantidad": 40.0, "precio_unitario": 9750.0, "producto_id": 175}]
r = c.post(f"/ingesta/raw/{raw([dict(x, subtotal=x['cantidad'] * 9750.0, alicuota_iva=21.0) for x in lineas], '00001-00003901', '86416772099901')}/approve", json=payload("00001-00003901", "86416772099901", lineas, 82))
rem = q("select ri.pedido_item_id, ri.cantidad_remitida from remitos_items ri join remitos r on r.id=ri.remito_id join facturas_remitos fr on fr.remito_id=r.id join facturas f on f.id=fr.factura_id where f.numero_comprobante=3901")
check(f"VINCULAR_PARCIAL con dos líneas del mismo producto sobre el #82 (renglones {A82} con 100 pendientes y {B82} con 40) aprueba [{r.status_code}] {'' if r.status_code == 200 else detalle(r)[:140]}", r.status_code == 200)
check(f"el remito lleva un renglón de cada uno: {sorted(rem)} (antes las dos líneas caían en el {A82})", sorted(rem) == sorted([(A82, 100.0), (B82, 40.0)]))
fi = q("select fi.pedido_item_id, fi.cantidad from facturas_items fi join facturas f on f.id=fi.factura_id where f.numero_comprobante=3901")
check(f"y las líneas de la factura espejo quedan enlazadas a los mismos renglones: {sorted(fi)}", sorted(fi) == sorted([(A82, 100.0), (B82, 40.0)]))

# ---- (3b) la guarda de la ingesta acumula: dos líneas de 5 del mismo producto contra un renglón único de 8 (pedido 131 ya remitido: se usa el 126, de 8 del 179)
a126 = q("select id, producto_id, cantidad from pedidos_items where pedido_id=126 order by id")[0]
cl126 = q("select cliente_id from pedidos where id=126")[0][0]; cuit126 = q("select cuit from clientes where id=?", cl126)[0][0]
l5 = [{"descripcion": nombre(a126[1]), "cantidad": 5.0, "precio_unitario": 100.0, "producto_id": a126[1]}] * 2
p = payload("00001-00003902", "86416772099902", l5, 126); p["cliente"] = {"id": cl126, "cuit": cuit126, "razon_social": "X"}
nf, nr = q("select count(*) from facturas")[0][0], q("select count(*) from remitos")[0][0]
r = c.post(f"/ingesta/raw/{raw([], '00001-00003902', '86416772099902')}/approve", json=p)
check(f"VINCULAR_PARCIAL: 5 + 5 contra un renglón que tiene {a126[2]:g} se frena [{r.status_code}] con CANTIDAD_EXCEDE_PEDIDO y no deja nada", r.status_code == 409 and "CANTIDAD_EXCEDE_PEDIDO" in r.text and q("select count(*) from facturas")[0][0] == nf and q("select count(*) from remitos")[0][0] == nr)

# ---- código: las dos pantallas/servicios usan los ayudantes, no el primero que encuentran
def leer(p): return io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
srv, sch = leer("backend/remitos/service.py"), leer("backend/remitos/schemas.py")
check("la guarda de la ingesta usa los ayudantes y ya no toma «el primero» por nombre o producto; el Remito Manual (y su ayudante) ya no existen",
      "RemitosService._renglon_de_la_linea(pedido_items_check, p_item.producto_id, usados_check)" in srv
      and "RemitosService._renglon_de_la_linea(pedido_items, p_item.producto_id, usados_parcial)" in srv
      and "target_p_item = next((pi for pi in pedido_items if str(pi.producto_id)" not in srv
      and "_renglon_del_item_manual" not in srv and "def create_manual(" not in srv and "ManualRemitoItem" not in sch)

app.dependency_overrides.clear()
try: eng.dispose(); os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
