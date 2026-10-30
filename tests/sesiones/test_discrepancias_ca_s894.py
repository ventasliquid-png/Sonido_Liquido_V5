r"""S894, Carlos 27/10: las discrepancias de Remitos que planteó CA (Intercambio/CA_a_OF/2026-10-26_DISCREPANCIAS_remitos_para_OF.md), con lo que decidió Carlos.
(H15, disc. 9) La clase y el bit 46 los fija el NÚMERO: el pedido puede cambiar de color o de comercial después («siempre es posible que un cliente pase a
    Rosa, incluso cuando haya firmado un 0015 y tenga una factura») y el remito sigue diciendo cómo salió. La congelación va en genoma.sincronizar (el guardado
    de todos los días), no en calcular_flags, que las migraciones usan para reconstruir.
(4) Bit 6 del cliente sin OC: el pedido se guarda con un aviso (X-Aviso-OC) y una nota [SISTEMA]; ya no es un 400. El bit 49 no se prende (Nike: lo prende una persona).
(5) PATCH /remitos/items/{id}/recibido retirado: «llegó» lo bajan solo las correcciones con causa.
(7) La pantalla de entregas del pedido se llama «Entregas y remitos», como el botón.
(H16, disc. 10) (a) «Queda en depósito» no se acepta con la salida confirmada (bit 47). (b) PATCH /fecha no mueve la emisión más allá de una salida registrada.
(2) El freno de bajar un renglón por debajo de lo entregado dice la salida (anular el remito o cargar una corrección), como ya lo decía el de lo facturado.
Sobre una COPIA de P con migrate_066, 067, 068 y 069 (las del despliegue)."""
import sys, os, shutil, sqlite3, glob, subprocess, io
from datetime import datetime, timedelta
from types import SimpleNamespace as NS
from urllib.parse import unquote
from _esquema_p import asegurar_esquema, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.remitos import genoma
from backend.remitos.genoma import calcular_flags, describir
from backend.remitos.constants import RemitoFlags as F

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
NC, ROSA = 1 << 11, 1 << 12
B46, B47, BIT49 = 1 << 46, 1 << 47, 1 << 49
D = lambda f: describir(f)

# ---- (H15) la congelación en sincronizar, sin base
def rem(flags, num, est, pf):
    return NS(pedido=NS(flags_estado=pf), items=[], flags_estado=int(flags), numero_legal=num, estado=est, fecha_emision=None, fecha_salida=None)
salio_blanco = int(F.EGRESO | F.EMITIDO | F.RETIRADO)
check("el riesgo de H15 existe en la función pura: recalcular un 0015 Blanco con el pedido pasado a Rosa le prende el 46",
      "CIRCULACION_ROSA" in D(calcular_flags(salio_blanco, "0015-00009999", "BORRADOR", ROSA))["marcas"])
r = rem(salio_blanco, "0015-00009999", "BORRADOR", ROSA); genoma.sincronizar(r)
check(f"sincronizar: un 0015 que salió Blanco sigue EGRESO y sin el 46 aunque el pedido pase a Rosa {D(r.flags_estado)}",
      D(r.flags_estado)["clase"] == "EGRESO" and "CIRCULACION_ROSA" not in D(r.flags_estado)["marcas"])
r = rem(salio_blanco | B46, "0015-00009999", "BORRADOR", 0); genoma.sincronizar(r)
check("un 0015 que salió de tránsito Rosa conserva el 46 aunque el pedido pase a Blanco (irreversible, Nike 23/10)", "CIRCULACION_ROSA" in D(r.flags_estado)["marcas"])
r = rem(salio_blanco, "0015-00009999", "ENTREGADO", NC); genoma.sincronizar(r)
check(f"un 0015 comercial sigue EGRESO si el pedido pasa a no comercial, y el estado y la logística se siguen calculando {D(r.flags_estado)}",
      (D(r.flags_estado)["clase"], D(r.flags_estado)["logistica"]) == ("EGRESO", "RECIBIDO"))
r = rem(int(F.EGRESO), None, "BORRADOR", ROSA); genoma.sincronizar(r)
check("un remito SIN número sigue al pedido: pasado a Rosa es INTERNO", D(r.flags_estado)["clase"] == "INTERNO")
r = rem(int(F.EGRESO), "0015-00009999", "BORRADOR", ROSA); genoma.sincronizar(r)
check("al tomar número (todavía sin estado) se calcula: un 0015 de un pedido Rosa nace EGRESO + 46", D(r.flags_estado)["clase"] == "EGRESO" and "CIRCULACION_ROSA" in D(r.flags_estado)["marcas"])
r = rem(int(F.EGRESO | F.EMITIDO), "0015-00009999", "ANULADO", NC); genoma.sincronizar(r)
check("anulado: la clase queda y el estado pasa a ANULADO", D(r.flags_estado)["clase"] == "EGRESO" and D(r.flags_estado)["estado"] == "ANULADO")

# ---- la copia de P, con las migraciones del despliegue
ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_*.db"))[-1]
TMP = os.path.join(RAIZ, "scratch", "test_discrepancias_ca_s894"); os.makedirs(TMP, exist_ok=True)
T = os.path.join(TMP, "P.db"); shutil.copyfile(ORIG, T)
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
def correr(nombre):
    return subprocess.run([PY, "-X", "utf8", os.path.join(RAIZ, "scripts", nombre)], capture_output=True, text=True, encoding="utf-8",
                          env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
def q(sql, *a):
    con = sqlite3.connect(T); x = con.execute(sql, a).fetchall(); con.commit(); con.close(); return x
rc = [correr(n).returncode for n in ("migrate_066_remitos_genoma_fecha_emision.py", "migrate_067_remitos_calificadores_46_47.py",
                                     "migrate_068_remitos_oc.py", "migrate_069_remitos_items_correccion.py")]
check(f"setup: copia de P ({os.path.basename(ORIG)}) con migrate_066, 067, 068 y 069 {rc}", rc == [0, 0, 0, 0])
asegurar_esquema(T)
rosa0015 = q("select count(*) from remitos r join pedidos p on p.id=r.pedido_id where (p.flags_estado>>12)&1=1 and r.numero_legal like '0015-%' and r.flags_estado & ?", B46)[0][0]
check(f"las migraciones siguen prendiendo el 46 en los Rosa con 0015 de P (la congelación no las toca): {rosa0015}", rosa0015 == 6)

from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
import backend.remitos.router as _router
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(_router.__file__))))
_aparte = imagenes_aparte(BASE); _aparte.__enter__()
SALIDA = os.path.join(BASE, "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida")
previos = set(os.listdir(SALIDA)) if os.path.isdir(SALIDA) else set()
def fl(rid): return q("select flags_estado from remitos where id=?", rid.replace("-", ""))[0][0]
def blancos():
    vistos, out = set(), []
    for p, i, x in q("""select p.id, pi.id, pi.cantidad - coalesce((select sum(ri.cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id
                        where ri.pedido_item_id=pi.id and r.estado<>'ANULADO'), 0) from pedidos p join pedidos_items pi on pi.pedido_id=p.id
                        where p.estado='PENDIENTE' and (p.flags_estado>>12)&1=0 and (p.flags_estado>>11)&1=0 order by p.id desc"""):
        if x and x > 0 and p not in vistos:
            vistos.add(p); out.append((p, i, x))
    return out
def armar(pedido, item, cant):
    r = cli.post("/remitos/armar", json={"pedido_id": pedido, "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": item, "cantidad": cant}]})
    return r.json()["id"] if r.status_code == 200 else ""
bl = blancos()
check(f"hay al menos tres pedidos Blancos con algo por remitir en la copia ({len(bl)})", len(bl) >= 3)
dia = lambda n: (datetime.now() - timedelta(days=n)).strftime("%Y-%m-%d")

# ---- (H15) de punta a punta: un 0015 Blanco, el pedido pasa a Rosa y vuelve, el remito se guarda
p0 = bl[0][0]
a = armar(*bl[0]); cli.get(f"/remitos/{a}/pdf")
check(f"el remito del pedido Blanco #{p0} toma número: EGRESO sin el 46 {D(fl(a))}", D(fl(a))["clase"] == "EGRESO" and not fl(a) & B46)
r = cli.patch(f"/pedidos/{p0}/circuito-bipolar", json={"is_interno": True})
check(f"el pedido pasa a Rosa con el remito ya numerado (no se frena) [{r.status_code}]", r.status_code == 200 and q("select flags_estado from pedidos where id=?", p0)[0][0] & ROSA)
r = cli.patch(f"/remitos/{a}/fecha", json={"fecha": dia(1), "motivo": "prueba S894"})
check(f"se guarda el remito (cambio de fecha) [{r.status_code}] y sigue EGRESO sin el 46: dice cómo salió {D(fl(a))}",
      r.status_code == 200 and D(fl(a))["clase"] == "EGRESO" and not fl(a) & B46)
cli.patch(f"/pedidos/{p0}/circuito-bipolar", json={"is_interno": False})
cli.patch(f"/remitos/{a}/fecha", json={"fecha": dia(2), "motivo": "prueba S894, vuelta"})
check("el ida y vuelta Blanco -> Rosa -> Blanco ya no deja el 46 prendido", not fl(a) & B46 and D(fl(a))["clase"] == "EGRESO")

# ---- (4) bit 6 sin OC
cl6 = q("select id from clientes where flags_estado & 64 limit 1")
if not cl6:
    cl6 = q("select cliente_id from pedidos where id=?", p0)
    q("update clientes set flags_estado = flags_estado | 64 where id=?", cl6[0][0])
cl6 = cl6[0][0]
prod = q("select producto_id, precio_unitario from pedidos_items where pedido_id=? limit 1", p0)[0]
base = {"cliente_id": cl6, "fecha": "2026-10-27T10:00:00", "estado": "PENDIENTE",
        "items": [{"producto_id": prod[0], "cantidad": 1, "precio_unitario": prod[1] or 100}]}
r = cli.post("/pedidos/tactico", json=base)
nuevo = r.json().get("id") if r.status_code == 201 else None
aviso = unquote(r.headers.get("x-aviso-oc", ""))
check(f"cliente con el bit 6 y el pedido sin OC: se guarda [{r.status_code}] (antes, 400 ORDEN DE COMPRA REQUERIDA)", r.status_code == 201 and nuevo)
check(f"y el servidor avisa (X-Aviso-OC): «{aviso}»", "exige orden de compra" in aviso)
nota = q("select nota, flags_estado from pedidos where id=?", nuevo)[0] if nuevo else ("", 0)
check("queda la nota [SISTEMA] «Guardado sin OC» y el bit 49 sigue apagado (lo prende una persona)", "[SISTEMA] Guardado sin OC" in (nota[0] or "") and not int(nota[1] or 0) & BIT49)
r = cli.post("/pedidos/tactico", json=dict(base, oc="4512"))
check(f"con OC no hay aviso ni nota [{r.status_code}]", r.status_code == 201 and "x-aviso-oc" not in r.headers
      and "Guardado sin OC" not in (q("select nota from pedidos where id=?", r.json()["id"])[0][0] or ""))
r = cli.post("/pedidos/tactico", json=dict(base, oc="S/N"))
check(f"con «S/N» tampoco (es la omisión explícita, como antes) [{r.status_code}]", r.status_code == 201 and "x-aviso-oc" not in r.headers)

# ---- (5) recibido retirado
r = cli.patch("/remitos/items/1/recibido", json={"cantidad_recibida": -5})
from backend.remitos.service import RemitosService
from backend.remitos import schemas as _sch
check(f"PATCH /remitos/items/{{id}}/recibido ya no existe [{r.status_code}], ni su servicio ni su esquema",
      r.status_code in (404, 405) and not any("/recibido" in getattr(rt, "path", "") for rt in app.routes)
      and not hasattr(RemitosService, "set_cantidad_recibida") and not hasattr(_sch, "CantidadRecibidaUpdate"))

# ---- (H16 a) sin papel y después «queda en depósito»
b = armar(*bl[1]); cli.post(f"/remitos/{b}/salida-sin-papel", json={})
r = cli.post(f"/remitos/{b}/en-deposito")
check(f"«Salió sin papel» (bit 47) y después «Queda en depósito»: 409 SALIDA_CONFIRMADA [{r.status_code}] y no queda EN_DEPOSITO",
      r.status_code == 409 and "SALIDA_CONFIRMADA" in r.text and not fl(b) & int(F.EN_DEPOSITO) and fl(b) & B47)
c = armar(*bl[2]); cli.get(f"/remitos/{c}/pdf")
r = cli.post(f"/remitos/{c}/en-deposito")
check(f"un remito impreso (salida asumida, sin el 47) sí puede quedar en depósito, como el caso Rizobacter [{r.status_code}]", r.status_code == 200 and fl(c) & int(F.EN_DEPOSITO))

# ---- (H16 b) la fecha hacia adelante, contra la salida registrada
q("update remitos set fecha_emision=? where id=?", dia(5) + " 10:00:00", c.replace("-", ""))
r = cli.post(f"/remitos/{c}/retiro", json={"fecha": dia(3)})
check(f"emitido hace 5 días, en depósito, lo retiran hace 3 [{r.status_code}]", r.status_code == 200 and q("select fecha_salida from remitos where id=?", c.replace("-", ""))[0][0].startswith(dia(3)))
r = cli.patch(f"/remitos/{c}/fecha", json={"fecha": dia(1), "motivo": "prueba"})
check(f"mover la fecha del remito a ayer, después de la salida: 422 FECHA_POSTERIOR_A_LA_SALIDA [{r.status_code}]", r.status_code == 422 and "FECHA_POSTERIOR_A_LA_SALIDA" in r.text)
r2 = cli.patch(f"/remitos/{c}/fecha", json={"fecha": dia(4), "motivo": "prueba"})
f2 = q("select fecha_emision, fecha_salida from remitos where id=?", c.replace("-", ""))[0]
r = cli.patch(f"/remitos/{c}/fecha", json={"fecha": dia(3), "motivo": "prueba"})
fila = q("select fecha_emision, fecha_salida from remitos where id=?", c.replace("-", ""))[0]
check(f"antes de la salida, o el mismo día, sí [{r2.status_code}, {r.status_code}], y la salida registrada no se mueve {f2} -> {fila}",
      r2.status_code == 200 and r.status_code == 200 and f2[0].startswith(dia(4)) and f2[1].startswith(dia(3)) and fila[0].startswith(dia(3)) and fila[1].startswith(dia(3)))

# ---- (2) el mensaje del piso
from backend.pedidos.cantidades import mensaje_baja_de_cantidad
m1 = mensaje_baja_de_cantidad(NS(cantidad=10.0, cantidad_remitida=6.0, cantidad_facturada_neta=0.0), 5.0) or ""
m2 = mensaje_baja_de_cantidad(NS(cantidad=10.0, cantidad_remitida=0.0, cantidad_facturada_neta=8.0), 5.0) or ""
check(f"bajar por debajo de lo entregado dice la salida: «{m1}»", "ya se entregaron 6 " in m1 and "anulá el remito" in m1 and "corrección" in m1)
check("y por debajo de lo facturado sigue pidiendo la nota de crédito", "CANTIDAD_BAJO_FACTURADO" in m2 and "nota de crédito" in m2)

# ---- las pantallas y el código (estático)
def leer(p): return io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
canvas, spl, fic, lista = (leer("frontend/src/views/Ventas/PedidoCanvas.vue"), leer("frontend/src/views/Logistica/LogisticaSplitter.vue"),
                           leer("frontend/src/views/Logistica/RemitoFicha.vue"), leer("frontend/src/views/Logistica/RemitoListView.vue"))
rped = leer("backend/pedidos/router.py")
check("(4) el pedido: «Guardar» ya no se traba por la OC, el aviso dice «Falta la OC» y se muestra el aviso del servidor",
      "!isOCValid || isClosedOrder" not in canvas and 'data-aviso="falta-oc"' in canvas and "res.headers?.['x-aviso-oc']" in canvas
      and "ORDEN DE COMPRA REQUERIDA" not in rped and 'response.headers["X-Aviso-OC"]' in rped)
check("(7) la pantalla de entregas del pedido se titula «Entregas y remitos» (no «Viajes Activos»)", ">Entregas y remitos</h2>" in spl and "Viajes Activos" not in spl)
check("(H16 a) ni la ficha ni el listado ofrecen «Queda en depósito» con la salida confirmada",
      "!enDeposito && !salidaConfirmada" in fic and "marcas.includes('SALIDA_CONFIRMADA')" in fic and "!enDeposito(remito) && !tieneBit(remito.flags_estado, 47)" in lista)
check("(2) el freno del renglón suelto (PATCH del renglón) dice la misma salida", rped.count("anulá el remito si la mercadería no salió, o cargá una corrección") == 1)

del cli; eng.dispose()
for n in (set(os.listdir(SALIDA)) - previos) if os.path.isdir(SALIDA) else []:
    os.remove(os.path.join(SALIDA, n))
_aparte.__exit__(None, None, None)
shutil.rmtree(TMP, ignore_errors=True)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
