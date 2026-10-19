r"""S888, Card #179 (prerrequisito de la Card #177, kits del pedido): un pedido puede tener DOS renglones del MISMO producto (el kit del pedido los usa), y el Remito Manual y la ingesta
en modo VINCULAR_PARCIAL los emparejaban por nombre / producto y caían siempre en el PRIMERO.
(1) Remito Manual: ManualRemitoItem trae pedido_item_id y el servidor lo usa; sin él (clientes viejos) empareja por nombre y, con repetidos, toma el primer renglón todavía no usado.
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

# ---- (1) Remito Manual SIN pedido_item_id (cliente viejo): dos líneas del mismo nombre toman dos renglones distintos
n48 = nombre(154)
r = c.post("/remitos/manual", json={"pedido_id": 48, "items": [{"descripcion": n48, "cantidad": 60}, {"descripcion": n48, "cantidad": 24}]})
rid = r.json().get("id") if r.status_code == 200 else None
check(f"manual por nombre, 2 líneas del mismo producto: se crea [{r.status_code}] {'' if r.status_code == 200 else detalle(r)[:140]}", r.status_code == 200 and rid)
check(f"cada línea tomó SU renglón: {items_del_remito(rid) if rid else None} (antes las dos caían en el {A48})", rid and items_del_remito(rid) == sorted([(A48, 60.0), (B48, 24.0)]))
check("el pedido quedó entregado por completo: no se marcó «Remito Parcial» en la nota", "Remito Parcial" not in (q("select nota from pedidos where id=48")[0][0] or ""))

# ---- (1b) Remito Manual CON pedido_item_id: manda el id, aunque el nombre sea el mismo
n123 = nombre(214)
r = c.post("/remitos/manual", json={"pedido_id": 123, "items": [{"pedido_item_id": B123, "descripcion": n123, "cantidad": 100}]})
rid = r.json().get("id") if r.status_code == 200 else None
check(f"manual con pedido_item_id del SEGUNDO renglón: se crea [{r.status_code}] y lleva ese renglón, no el primero: {items_del_remito(rid) if rid else None}", rid and items_del_remito(rid) == [(B123, 100.0)])
check("y el pedido figura con remito parcial (el primer renglón de 360 quedó pendiente)", "Remito Parcial" in (q("select nota from pedidos where id=123")[0][0] or ""))
r = c.post("/remitos/manual", json={"pedido_id": 123, "items": [{"pedido_item_id": B123, "descripcion": n123, "cantidad": 1}]})
check(f"la guarda juzga el renglón elegido: el segundo ya está remitido por completo, 1 más se frena [{r.status_code}] con CANTIDAD_EXCEDE_PEDIDO", r.status_code == 409 and detalle(r).startswith("CANTIDAD_EXCEDE_PEDIDO"))
nr = q("select count(*) from remitos")[0][0]
r = c.post("/remitos/manual", json={"pedido_id": 123, "items": [{"pedido_item_id": A123, "descripcion": n123, "cantidad": 361}]})
check(f"y el primero, que tiene 360 pendientes, rechaza 361 [{r.status_code}]", r.status_code == 409 and detalle(r).startswith("CANTIDAD_EXCEDE_PEDIDO") and "360" in detalle(r))
r = c.post("/remitos/manual", json={"pedido_id": 123, "items": [{"pedido_item_id": A123, "descripcion": n123, "cantidad": 360}]})
rid = r.json().get("id") if r.status_code == 200 else None
check(f"los 360 del primer renglón sí salen [{r.status_code}]: {items_del_remito(rid) if rid else None}", rid and items_del_remito(rid) == [(A123, 360.0)])
nr = q("select count(*) from remitos")[0][0]
r = c.post("/remitos/manual", json={"pedido_id": 131, "items": [{"pedido_item_id": B48, "descripcion": nombre(148), "cantidad": 1}]})
check(f"un pedido_item_id de OTRO pedido se rechaza [{r.status_code}] con RENGLON_AJENO_AL_PEDIDO y no deja remito", r.status_code == 409 and detalle(r).startswith("RENGLON_AJENO_AL_PEDIDO") and q("select count(*) from remitos")[0][0] == nr)

# ---- (2) la guarda acumula lo que ya tomó cada renglón dentro del mismo remito
n131 = nombre(148)
r = c.post("/remitos/manual", json={"pedido_id": 131, "items": [{"descripcion": n131, "cantidad": 5}, {"descripcion": n131, "cantidad": 5}]})
check(f"dos líneas de 5 contra un único renglón de 8 se frenan [{r.status_code}] (antes pasaban las dos): {detalle(r)[:110]}", r.status_code == 409 and detalle(r).startswith("CANTIDAD_EXCEDE_PEDIDO") and "3.0" in detalle(r))
check("y no quedó ningún remito del pedido 131", q("select count(*) from remitos where pedido_id=131")[0][0] == 0)
p117 = q("select id, producto_id, cantidad from pedidos_items where pedido_id=117 order by id")[0]   # los clientes de los pedidos 131 y 117 no tienen domicilio en la copia de P: se le pasa el del cliente del 48
dom48 = q("select id from domicilios where cliente_id=(select cliente_id from pedidos where id=48) limit 1")[0][0]
r = c.post("/remitos/manual", json={"pedido_id": 117, "domicilio_entrega_id": dom48, "items": [{"descripcion": nombre(p117[1]), "cantidad": p117[2]}]})
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
srv, sch, vue = leer("backend/remitos/service.py"), leer("backend/remitos/schemas.py"), leer("frontend/src/views/Logistica/ManualRemitoView.vue")
check("ManualRemitoItem declara pedido_item_id opcional", re.search(r"class ManualRemitoItem\(BaseModel\):[\s\S]{0,700}pedido_item_id: Optional\[int\] = None", sch))
check("create_manual y la guarda de la ingesta usan los ayudantes y ya no toman «el primero» por nombre o producto",
      "RemitosService._renglon_del_item_manual(original_items, item, asignado)" in srv and "RemitosService._renglon_de_la_linea(pedido_items_check, p_item.producto_id, usados_check)" in srv
      and "RemitosService._renglon_de_la_linea(pedido_items, p_item.producto_id, usados_parcial)" in srv
      and "target_pi = next((pi for pi in original_items if pi.producto.nombre" not in srv and "target_p_item = next((pi for pi in pedido_items if str(pi.producto_id)" not in srv)
check("la pantalla del Remito Manual guarda el id del renglón y lo manda en el payload",
      "pedido_item_id: i.id," in vue and "pedido_item_id: i.pedido_item_id ?? null," in vue)

app.dependency_overrides.clear()
try: eng.dispose(); os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
