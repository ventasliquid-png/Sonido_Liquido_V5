r"""S888, Card #177 v3 (kits del pedido), paso 1: el SERVIDOR. Nike ratifico el diseno con Sello de Oro el 19/10/2026.
(1) Nombres canonicos: PedidoItem.kit_grupo (entero 1..99, NULL = sin kit), PedidoFlags.ES_KIT = bit 47 del PEDIDO; nunca es_kit / en_kit en el renglon.
(2) El bit ES_KIT lo calcula el servidor al guardar: prendido con al menos un kit valido (2 o mas renglones con el mismo kit_grupo), apagado si ninguno; congelado en CUMPLIDO / ANULADO.
(3) kit_grupo viaja en el alta, la edicion del pedido (ausente = no se toca; null = sin kit), el renglon suelto, el alta de renglon, el borrado y el clon.
(4) Un renglon facturado (cantidad_facturada > 0) y un pedido nacido de una factura (bit 38) no cambian de kit.
(5) POST /pedidos/kits/reparto: el reparto del precio del kit entre sus renglones (PAREJO / ABSORBE), por renglon, en neto, a centavos exactos.
Sobre una COPIA de la base de P del 15/10 16:01 (con pedidos_items.kit_grupo agregada por el ayudante _esquema_p, que hace el mismo ALTER TABLE que migrate_063)."""
import sys, os, shutil, sqlite3, re, io, random
from decimal import Decimal
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from backend.pedidos.constants import PedidoFlags as PF, STATE_MASK
from backend.pedidos import kits
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
def leer(p): return io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261015_1601.db"
os.makedirs(os.path.join(RAIZ, "scratch"), exist_ok=True)
T = os.path.join(RAIZ, "scratch", "test_kit_grupo_tmp.db"); copiar_p(ORIG, T)
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
    con = sqlite3.connect(T); con.execute(sql, a); con.commit(); con.close()
def detalle(r): return (r.json() or {}).get("detail", "") if r.headers.get("content-type", "").startswith("application/json") else r.text
BIT = 1 << 47
def bit47(pid): return bool(q("select flags_estado from pedidos where id=?", pid)[0][0] & BIT)
def grupos(pid): return [g for (g,) in q("select kit_grupo from pedidos_items where pedido_id=? order by id", pid)]
def ids(pid): return [i for (i,) in q("select id from pedidos_items where pedido_id=? order by id", pid)]

# ---------------- (1) nombres canonicos y el bit
check("PedidoFlags.ES_KIT es el bit 47 = 140737488355328", int(PF.ES_KIT) == 1 << 47 == 140737488355328)
check("ningun otro bit del pedido coincide con ES_KIT y no esta en la mascara de estados", sum(1 for f in PF if int(f) & BIT) == 1 and not (int(STATE_MASK) & BIT))
modelos, esquemas = leer("backend/pedidos/models.py"), leer("backend/pedidos/schemas.py")
item_src = modelos[modelos.index("class PedidoItem(Base):"):]
check("el renglon tiene kit_grupo (Integer, nullable) y NO tiene es_kit ni en_kit (nombres canonicos)",
      re.search(r"kit_grupo = Column\(Integer, nullable=True\)", item_src) and not re.search(r"\b(es_kit|en_kit)\b", item_src) and not re.search(r"\b(es_kit|en_kit)\b", esquemas))
check("la columna kit_grupo existe en la copia y todos los renglones previos quedan en NULL", {r[1] for r in q("pragma table_info(pedidos_items)")} >= {"kit_grupo"} and q("select count(*) from pedidos_items where kit_grupo is not null")[0][0] == 0)
check("ningun pedido de P trae el bit 47 prendido (estaba libre)", q("select count(*) from pedidos where (flags_estado & ?) != 0", BIT)[0][0] == 0)

# ---------------- (2) funciones puras
check("kits_validos: un numero con un solo renglon no es kit; con 2 o mas si", kits.kits_validos([1, 3, None]) == {} and kits.kits_validos([1, 1, 3, None, 2, 2, 2]) == {1: 2, 2: 3} and not kits.hay_kit_valido([None, None]) and kits.hay_kit_valido([4, 4]))

# ---------------- (3) calcular_reparto: el ejemplo de Carlos (O3 + Bac + guantes = $33.500, kit a $31.000)
o3, bac, gua = {"cantidad": 1, "precio_unitario": 18000.0, "descuento_importe": 0.0}, {"cantidad": 1, "precio_unitario": 7600.0, "descuento_importe": 0.0}, {"cantidad": 1, "precio_unitario": 7900.0, "descuento_importe": 0.0}
r = kits.calcular_reparto([o3, bac, gua], precio_kit=31000.0)
sub = [x["subtotal"] for x in r["items"]]
check(f"PAREJO a $31.000: suma 33.500, rebaja 2.500 (7,46%), reparto proporcional {sub} (el centavo que sobra del redondeo va al O3, el renglon mas grande) y suma exacta $31.000,00",
      r["suma"] == 33500.0 and r["rebaja_importe"] == 2500.0 and r["rebaja_porcentaje"] == 7.46 and sub == [16656.71, 7032.84, 7310.45] and round(sum(sub), 2) == 31000.0 and not r["sin_cambios"])
check("el descuento queda POR RENGLON (importe y % del precio de lista), no global: O3 -$1.343,29 (7,4627%)", r["items"][0]["descuento_importe"] == 1343.29 and r["items"][0]["descuento_porcentaje"] == 7.4627)
check("7,46% no supera el umbral de advertencia (8%); un kit a $30.000 (10,45%) si", r["supera_umbral"] is False and r["umbral_porcentaje"] == 8.0
      and kits.calcular_reparto([o3, bac, gua], precio_kit=30000.0)["supera_umbral"] is True and kits.calcular_reparto([o3, bac, gua], precio_kit=30000.0)["rebaja_porcentaje"] == 10.45)
from fractions import Fraction
exacto = [Fraction(b) * Fraction(31000, 33500) for b in (18000, 7600, 7900)]
check(f"control independiente con fracciones exactas: 18000, 7600 y 7900 x 31000/33500 = {[round(float(x), 4) for x in exacto]}; cada renglon queda a menos de 2 centavos del valor exacto", all(abs(float(e) - s) < 0.02 for e, s in zip(exacto, sub)))
for precio in (33500.0, 34000.0):
    rr = kits.calcular_reparto([o3, bac, gua], precio_kit=precio)
    check(f"precio del kit ${precio:,.0f} (igual o mayor a la suma): NO se modifica nada (el cliente nunca paga mas que con los renglones sueltos)",
          rr["sin_cambios"] and [x["descuento_importe"] for x in rr["items"]] == [0.0, 0.0, 0.0] and [x["subtotal"] for x in rr["items"]] == [18000.0, 7600.0, 7900.0] and rr["rebaja_importe"] == 0.0 and not rr["supera_umbral"])
# ABSORBE: el regalo (una bandeja) queda a $0 y el precio de lo demas se mantiene
bandeja = {"cantidad": 1, "precio_unitario": 5000.0, "descuento_importe": 0.0}
r = kits.calcular_reparto([o3, bandeja], precio_kit=18000.0, modo="ABSORBE", absorbe_indice=1)
check("ABSORBE: kit O3 + bandeja a $18.000 -> la bandeja absorbe la rebaja y queda a $0 (descuento 100%), el O3 no cambia",
      [x["subtotal"] for x in r["items"]] == [18000.0, 0.0] and r["items"][1]["descuento_importe"] == 5000.0 and r["items"][1]["descuento_porcentaje"] == 100.0 and r["items"][0]["descuento_importe"] == 0.0)
try: kits.calcular_reparto([o3, bandeja], precio_kit=10000.0, modo="ABSORBE", absorbe_indice=1); err = None
except ValueError as e: err = str(e)
check(f"ABSORBE: si la rebaja es mayor que el renglon que la absorbe se rechaza (KIT_ABSORBE_NO_ALCANZA) {err and err[:60]}", err and err.startswith("KIT_ABSORBE_NO_ALCANZA"))
# la base es el importe ACTUAL de cada renglon (ya con su descuento, ej. el 5% de un cliente) y el porcentaje da lo mismo que el precio
a, b = {"cantidad": 2, "precio_unitario": 500.0, "descuento_importe": 50.0}, {"cantidad": 1, "precio_unitario": 1050.0, "descuento_importe": 0.0}
rp, rq = kits.calcular_reparto([a, b], precio_kit=1800.0), kits.calcular_reparto([a, b], porcentaje=10.0)
check("la base es lo que cada renglon vale HOY (con su descuento previo): [950 + 1050] -> $1.800 deja 855,00 y 945,00; su descuento TOTAL pasa a 145 (14,5%) y 105 (10%)",
      rp["suma"] == 2000.0 and [x["subtotal"] for x in rp["items"]] == [855.0, 945.0] and [x["descuento_importe"] for x in rp["items"]] == [145.0, 105.0] and [x["descuento_porcentaje"] for x in rp["items"]] == [14.5, 10.0])
check("informar un 10% da lo mismo que informar el precio $1.800", rp["items"] == rq["items"] and rq["precio_kit"] == 1800.0)
tres = {"cantidad": 1, "precio_unitario": 100.0, "descuento_importe": 0.0}
r = kits.calcular_reparto([tres, tres, tres], precio_kit=100.0)
check(f"los centavos del redondeo van al renglon mas grande y la suma da exacto: {[x['subtotal'] for x in r['items']]}", [x["subtotal"] for x in r["items"]] == [33.33, 33.33, 33.34])
azar = random.Random(888); mal = 0
for _ in range(300):
    its = [{"cantidad": azar.choice([1, 2, 3, 5, 12, 0.5]), "precio_unitario": round(azar.uniform(1, 20000), 2), "descuento_importe": 0.0} for _ in range(azar.randint(2, 6))]
    for x in its: x["descuento_importe"] = round(x["cantidad"] * x["precio_unitario"] * azar.choice([0, 0, 0.05, 0.1]), 2)
    rr = kits.calcular_reparto(its, porcentaje=round(azar.uniform(0.5, 30), 2))
    tot = sum(Decimal(repr(x["subtotal"])) for x in rr["items"])
    if tot != Decimal(repr(rr["precio_kit"])) or any(x["subtotal"] < 0 for x in rr["items"]): mal += 1
check(f"300 kits al azar (2 a 6 renglones, con descuentos previos): la suma de los renglones da EXACTAMENTE el precio del kit en todos [{mal} desvios]", mal == 0)
casos = {"menos de dos renglones": ([o3], dict(precio_kit=1.0), "KIT_MENOS_DE_DOS"), "sin precio ni porcentaje": ([o3, bac], {}, "KIT_PRECIO_O_PORCENTAJE"),
         "precio y porcentaje a la vez": ([o3, bac], dict(precio_kit=1.0, porcentaje=5.0), "KIT_PRECIO_O_PORCENTAJE"), "porcentaje 101": ([o3, bac], dict(porcentaje=101.0), "KIT_PORCENTAJE_INVALIDO"),
         "precio negativo": ([o3, bac], dict(precio_kit=-1.0), "KIT_PRECIO_NEGATIVO"), "ABSORBE sin renglon": ([o3, bac], dict(precio_kit=1000.0, modo="ABSORBE"), "KIT_ABSORBE_SIN_RENGLON"),
         "modo inexistente": ([o3, bac], dict(precio_kit=1000.0, modo="REPARTO"), "KIT_MODO_INVALIDO"), "suma cero": ([{"cantidad": 1, "precio_unitario": 0.0}, {"cantidad": 1, "precio_unitario": 0.0}], dict(precio_kit=0.0), "KIT_SUMA_CERO")}
for nombre, (its, kw, codigo) in casos.items():
    try: kits.calcular_reparto(its, **kw); e = None
    except ValueError as ex: e = str(ex)
    check(f"rechaza «{nombre}» con {codigo}", e and e.startswith(codigo))

# ---------------- (4) el servidor: alta, edicion, renglon suelto, borrado, clon
cid = "069bd7c5be294d88a1df92c856239a7f"                      # Centro Pet
cid_u = f"{cid[:8]}-{cid[8:12]}-{cid[12:16]}-{cid[16:20]}-{cid[20:]}"
prods = [p for (p,) in q("select distinct producto_id from pedidos_items order by producto_id limit 4")]
def alta(gs, **extra):
    its = [{"producto_id": prods[k % len(prods)], "cantidad": 2, "precio_unitario": 1000.0 + k, "descuento_porcentaje": 0, "descuento_importe": 0, **({"kit_grupo": g} if g != "ausente" else {})} for k, g in enumerate(gs)]
    p = {"cliente_id": cid_u, "fecha": "2026-10-19T12:00:00", "items": its}; p.update(extra); return c.post("/pedidos/tactico", json=p)
r = alta([1, 1, None]); p1 = r.json().get("id") if r.status_code == 201 else None
check(f"alta con kit_grupo [1, 1, null]: se guarda [{r.status_code}] {grupos(p1) if p1 else detalle(r)[:100]}", p1 and grupos(p1) == [1, 1, None])
check("y el servidor prendio el bit ES_KIT (hay un kit valido: dos renglones con el 1)", p1 and bit47(p1))
check("el GET del pedido devuelve kit_grupo en cada renglon", p1 and [i.get("kit_grupo") for i in c.get(f"/pedidos/{p1}").json()["items"]] == [1, 1, None])
for gs, quiere, txt in (([1, 2], False, "dos numeros distintos con un renglon cada uno (1 + 3, no hay kits)"), ([1, 1, 2, 2], True, "dos kits"), ([None, None], False, "sin kits"), ([5], False, "un solo renglon con numero")):
    r = alta(gs); i = r.json().get("id") if r.status_code == 201 else None
    check(f"alta {gs}: {txt} -> bit {'prendido' if quiere else 'apagado'} [{r.status_code}]", i and bit47(i) == quiere and grupos(i) == gs)
r = alta(["ausente", "ausente"]); i = r.json().get("id") if r.status_code == 201 else None
check("un cliente viejo que no manda kit_grupo da de alta como siempre: renglones en NULL y bit apagado", i and grupos(i) == [None, None] and not bit47(i))
for malo in (0, 100, -1, "x"):
    check(f"kit_grupo={malo!r} se rechaza con 422 (va de 1 a 99)", alta([malo, 1]).status_code == 422)

# edicion del pedido (PATCH con items)
p2 = alta([None, None, None]).json()["id"]; ri = ids(p2)
def parche_items(pid, cambios, quitar=()):
    """lo que manda la ficha: todos los renglones; cambios = {indice: kit_grupo}; quitar = indices a los que NO se les manda la clave."""
    items = []
    for k, (rid, pr, ca, pu) in enumerate(q("select id, producto_id, cantidad, precio_unitario from pedidos_items where pedido_id=? order by id", pid)):
        it = {"id": rid, "producto_id": pr, "cantidad": ca, "precio_unitario": pu, "descuento_porcentaje": 0, "descuento_importe": 0}
        if k in cambios and k not in quitar: it["kit_grupo"] = cambios[k]
        items.append(it)
    return c.patch(f"/pedidos/{pid}", json={"items": items})
r = parche_items(p2, {0: 7, 1: 7})
check(f"editar el pedido: poner el kit 7 en dos renglones lo convierte en kit y prende el bit [{r.status_code}] {grupos(p2)}", r.status_code == 200 and grupos(p2) == [7, 7, None] and bit47(p2))
r = parche_items(p2, {})
check("guardar SIN mandar kit_grupo (la ficha de hoy, que todavia no lo conoce) NO lo borra: el kit y el bit siguen", r.status_code == 200 and grupos(p2) == [7, 7, None] and bit47(p2))
r = parche_items(p2, {1: None})
check(f"mandar kit_grupo=null en un renglon lo saca del kit: el 7 queda con un solo renglon, deja de ser kit y el servidor apaga el bit [{r.status_code}] {grupos(p2)}", r.status_code == 200 and grupos(p2) == [7, None, None] and not bit47(p2))
# renglon suelto
r = c.patch(f"/pedidos/items/{ri[1]}", json={"kit_grupo": 7})
check(f"PATCH de un renglon suelto: kit_grupo=7 -> vuelve a haber kit y el bit se prende [{r.status_code}]", r.status_code == 200 and grupos(p2) == [7, 7, None] and bit47(p2))
r = c.patch(f"/pedidos/items/{ri[1]}", json={"cantidad": 3})
check("cambiar solo la cantidad de un renglon no toca su kit", r.status_code == 200 and grupos(p2) == [7, 7, None] and bit47(p2))
r = c.post(f"/pedidos/{p2}/items", json={"producto_id": prods[0], "cantidad": 1, "precio_unitario": 500.0, "kit_grupo": 9})
check(f"agregar un renglon con kit_grupo=9: un solo renglon, no hay kit nuevo y el 7 sigue valido [{r.status_code}]", r.status_code == 200 and grupos(p2) == [7, 7, None, 9] and bit47(p2))
r = c.delete(f"/pedidos/items/{ids(p2)[0]}")
check(f"borrar un renglon del kit 7 lo deja con uno solo: deja de ser kit y el bit se apaga [{r.status_code}] {grupos(p2)}", r.status_code == 204 and grupos(p2) == [7, None, 9] and not bit47(p2))
# clon
c.patch(f"/pedidos/items/{ids(p2)[1]}", json={"kit_grupo": 7})
r = c.post(f"/pedidos/{p2}/clone"); pc = r.json().get("id") if r.status_code == 200 else None
check(f"clonar un pedido con kit conserva los numeros y el bit [{r.status_code}] {grupos(pc) if pc else None}", pc and grupos(pc) == [7, 7, 9] and bit47(pc))

# congelado en CUMPLIDO / ANULADO
def cerrar(pid, estado):
    bit = {"CUMPLIDO": PF.ES_CUMPLIDO, "ANULADO": PF.ES_ANULADO}[estado]
    ejecutar("update pedidos set estado=?, flags_estado=(flags_estado & ?) | ? where id=?", estado, ~int(STATE_MASK) & ((1 << 63) - 1) | 0, int(bit), pid)
p3 = alta([1, 1]).json()["id"]; cerrar(p3, "CUMPLIDO")
r = c.patch(f"/pedidos/items/{ids(p3)[0]}", json={"kit_grupo": None})
check(f"pedido CUMPLIDO: el bit queda CONGELADO aunque el kit se deshaga (sigue prendido) [{r.status_code}] {grupos(p3)}", grupos(p3) == [None, 1] and bit47(p3))
p4 = alta([1, 2]).json()["id"]; cerrar(p4, "ANULADO")
r = c.patch(f"/pedidos/items/{ids(p4)[1]}", json={"kit_grupo": 1})
check(f"pedido ANULADO: el bit queda congelado aunque se arme un kit (sigue apagado) [{r.status_code}] {grupos(p4)}", grupos(p4) == [1, 1] and not bit47(p4))

# renglon facturado y pedido nacido de una factura
fact = q("select pi.id, pi.pedido_id from pedidos_items pi where pi.id=181")[0]
r = c.patch(f"/pedidos/items/{fact[0]}", json={"kit_grupo": 1})
check(f"el renglon 181 del pedido 82 tiene facturas vigentes: no se puede marcar de un kit -> 400 KIT_RENGLON_FACTURADO [{r.status_code}] {detalle(r)[:70]}", r.status_code == 400 and "KIT_RENGLON_FACTURADO" in detalle(r) and grupos(82)[2] is None)
r = c.patch(f"/pedidos/items/{fact[0]}", json={"kit_grupo": None})
check(f"mandarle el mismo valor (null) no es un cambio: pasa [{r.status_code}]", r.status_code == 200)
r = parche_items(82, {2: 1})
check(f"y por la edicion del pedido tambien se frena (400) y no cambia nada [{r.status_code}] {grupos(82)}", r.status_code == 400 and "KIT_RENGLON_FACTURADO" in detalle(r) and grupos(82) == [None, None, None])
r = c.patch(f"/pedidos/items/{ids(123)[0]}", json={"kit_grupo": 2})
check(f"un renglon sin factura (pedido 123) si se puede marcar [{r.status_code}]", r.status_code == 200 and grupos(123) == [2])
ejecutar("update pedidos set flags_estado = flags_estado | ? where id=131", int(PF.ORIGEN_FACTURA))
r = c.patch(f"/pedidos/items/{ids(131)[0]}", json={"kit_grupo": 1})
check(f"un pedido que nacio de una factura (bit 38) no agrupa renglones en kits -> 400 KIT_PEDIDO_DE_FACTURA [{r.status_code}] {detalle(r)[:60]}", r.status_code == 400 and "KIT_PEDIDO_DE_FACTURA" in detalle(r))

# guardar sin tocar los kits: ningun pedido de P con facturas se bloquea por esta guarda
bloq, probados = [], 0
for (pid,) in q("select distinct pi.pedido_id from pedidos_items pi join facturas_items fi on fi.pedido_item_id=pi.id join facturas f on f.id=fi.factura_id where f.estado='AUTORIZADA_AFIP' order by 1"):
    r = parche_items(pid, {}); probados += 1
    if r.status_code == 400 and "KIT_" in detalle(r): bloq.append(pid)
check(f"guardar (sin kit_grupo) los {probados} pedidos de P que tienen renglones facturados: ninguno se frena por la guarda de kits {bloq}", probados >= 20 and not bloq)
# Rosa y Blanco por igual
rosa = q("select id from pedidos where (flags_estado & 4096) != 0 and estado='PENDIENTE' and id in (select pedido_id from pedidos_items group by pedido_id having count(*)>=2) limit 1")[0][0]
a, b = ids(rosa)[:2]
c.patch(f"/pedidos/items/{a}", json={"kit_grupo": 3}); r = c.patch(f"/pedidos/items/{b}", json={"kit_grupo": 3})
check(f"un pedido ROSA (el {rosa}) arma kits igual que uno Blanco: bit prendido [{r.status_code}]", r.status_code == 200 and bit47(rosa))

# ---------------- (5) el endpoint del reparto
def reparto(**kw): return c.post("/pedidos/kits/reparto", json=kw)
base = {"items": [dict(o3), dict(bac), dict(gua)]}
r = reparto(**base, precio_kit=31000.0); j = r.json() if r.status_code == 200 else {}
check(f"POST /pedidos/kits/reparto: el ejemplo de Carlos da 200 y el mismo reparto [{r.status_code}] {[x['subtotal'] for x in j.get('items', [])]}", r.status_code == 200 and [x["subtotal"] for x in j["items"]] == [16656.71, 7032.84, 7310.45] and j["supera_umbral"] is False)
r = reparto(items=[dict(o3), dict(bandeja)], precio_kit=18000.0, modo="ABSORBE", absorbe_indice=1)
check(f"modo ABSORBE por la API [{r.status_code}]", r.status_code == 200 and [x["subtotal"] for x in r.json()["items"]] == [18000.0, 0.0])
r = reparto(**base)
check(f"sin precio ni porcentaje: 422 con el codigo [{r.status_code}] {detalle(r)[:40]}", r.status_code == 422 and detalle(r).startswith("KIT_PRECIO_O_PORCENTAJE"))
r = reparto(items=[dict(o3, id=181), dict(bac)], precio_kit=1000.0)
check(f"si un renglon ya guardado tiene factura (el 181) no entra en un kit: 409 [{r.status_code}] {detalle(r)[:40]}", r.status_code == 409 and "KIT_RENGLON_FACTURADO" in detalle(r))
n0 = q("select count(*) from pedidos")[0][0], q("select sum(subtotal) from pedidos_items")[0][0]
reparto(**base, precio_kit=1000.0)
check("el reparto solo calcula: no escribe nada en la base", (q("select count(*) from pedidos")[0][0], q("select sum(subtotal) from pedidos_items")[0][0]) == n0)

app.dependency_overrides.clear()
try: eng.dispose(); os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
