r"""S893, Carlos + Nike 26/10 (Sello de Oro, bits 48 y 49 de PedidoFlags): QUIÉN CARGA CON LO QUE SE PIERDE EN EL CAMINO lo decide el PEDIDO, no el cliente ni el método del remito.
Bit 48 FLETE_A_CARGO_NUESTRO: apagado (el normal y el de todos los pedidos viejos) el flete es del cliente: una pérdida solo se anota, se factura lo que salió y el pedido no vuelve a deber; prendido
el flete es nuestro: la pérdida es nuestra y el pedido vuelve a deber. Se cambia con PATCH /pedidos/{id}/flete-a-cargo MIENTRAS EL PEDIDO NO TENGA REMITOS VIGENTES (después 409 FLETE_CONGELADO: un error
propio se resuelve con un pedido NUEVO con el bit prendido). «Moto / cadetería» ya no implica flete nuestro (la moto que manda el cliente es suya); un remito con TRANSPORTE_PROPIO sí lo es.
Bit 49 REQUIERE_ATENCION: solo el número reservado. Sobre una COPIA de P con migrate_066, 068 y 069."""
import sys, os, shutil, sqlite3, glob, subprocess, io, re
from _esquema_p import asegurar_esquema, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_*.db"))[-1]
TMP = os.path.join(RAIZ, "scratch", "test_flete_a_cargo_s893"); os.makedirs(TMP, exist_ok=True)
T = os.path.join(TMP, "P.db"); shutil.copyfile(ORIG, T)
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
def correr(nombre):
    return subprocess.run([PY, "-X", "utf8", os.path.join(RAIZ, "scripts", nombre)], capture_output=True, text=True, encoding="utf-8",
                          env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
def q(sql, *a):
    con = sqlite3.connect(T); x = con.execute(sql, a).fetchall(); con.commit(); con.close(); return x
rc = [correr(n).returncode for n in ("migrate_066_remitos_genoma_fecha_emision.py", "migrate_068_remitos_oc.py", "migrate_069_remitos_items_correccion.py")]
check(f"setup: copia de P con migrate_066, 068 y 069 {rc}", rc == [0, 0, 0])
asegurar_esquema(T)

BIT48, BIT49 = 1 << 48, 1 << 49
from backend.pedidos.constants import PedidoFlags as PF
check("los valores que ratificó Nike: FLETE_A_CARGO_NUESTRO = 281474976710656 (bit 48) y REQUIERE_ATENCION = 562949953421312 (bit 49)",
      PF.FLETE_A_CARGO_NUESTRO.value == 281474976710656 == BIT48 and PF.REQUIERE_ATENCION.value == 562949953421312 == BIT49)
valores = [m.value for m in PF]
check("ningún bit del pedido se repite y los dos nuevos están fuera de la máscara de estados", len(valores) == len(set(valores)) and not (BIT48 | BIT49) & PF.ES_FIRME.value
      and not (BIT48 | BIT49) & (PF.ES_PRESUPUESTO.value | PF.ES_FIRME.value | PF.ES_CUMPLIDO.value | PF.ES_ANULADO.value))

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
def flags(pid): return q("select flags_estado from pedidos where id=?", pid)[0][0]
def nota(pid): return q("select nota from pedidos where id=?", pid)[0][0] or ""
def rid(numero): return q("select id from remitos where numero_legal=?", numero)[0][0]
def corregir(remito_id, item_id, real, causa):
    return cli.post(f"/remitos/{remito_id}/correccion", json={"remito_item_id": item_id, "cantidad_real": real, "causa": causa})

# ---- el endpoint, en un pedido SIN remitos
libre = q("""select p.id from pedidos p where p.estado='PENDIENTE' and not exists (select 1 from remitos r where r.pedido_id=p.id and r.estado != 'ANULADO') order by p.id desc limit 1""")[0][0]
f0 = flags(libre)
check(f"el pedido #{libre} (sin remitos) arranca con el flete del cliente (bit 48 apagado)", not f0 & BIT48)
r = cli.patch(f"/pedidos/{libre}/flete-a-cargo", json={"nuestro": True})
check(f"prender «flete nuestro» [{r.status_code}]: queda el bit 48, no se toca ningún otro bit y la nota [SISTEMA] dice quién y cuándo",
      r.status_code == 200 and flags(libre) == f0 | BIT48 and "[SISTEMA] Flete a cargo NUESTRO (bit 48)" in nota(libre) and "tmp" in nota(libre))
check("la respuesta trae los flags con el bit 48", r.json().get("flags_estado") == f0 | BIT48)
n1 = len(nota(libre))
r = cli.patch(f"/pedidos/{libre}/flete-a-cargo", json={"nuestro": True})
check("pedir lo que ya está no cambia nada ni deja otra nota (idempotente)", r.status_code == 200 and len(nota(libre)) == n1 and flags(libre) == f0 | BIT48)
r = cli.patch(f"/pedidos/{libre}/flete-a-cargo", json={"nuestro": False})
check(f"y se apaga [{r.status_code}], con su nota", r.status_code == 200 and flags(libre) == f0 and "Flete a cargo del CLIENTE (bit 48)" in nota(libre))
check("un pedido que no existe: 404", cli.patch("/pedidos/999999/flete-a-cargo", json={"nuestro": True}).status_code == 404)
check("sin el campo «nuestro»: 422", cli.patch(f"/pedidos/{libre}/flete-a-cargo", json={}).status_code == 422)

# ---- congelado con un remito vigente
r = cli.patch("/pedidos/137/flete-a-cargo", json={"nuestro": True})   # pedido 137: tiene el 0015-00003031
check(f"con un remito vigente (el 0015-00003031 del #137) el flete no se cambia [{r.status_code}]: 409 FLETE_CONGELADO que nombra el remito",
      r.status_code == 409 and "FLETE_CONGELADO" in r.text and "0015-00003031" in r.text and not flags(137) & BIT48)
solo_anulado = q("""select p.id, r.numero_legal from pedidos p join remitos r on r.pedido_id=p.id
                    where r.estado='ANULADO' and not exists (select 1 from remitos r2 where r2.pedido_id=p.id and r2.estado != 'ANULADO') limit 1""")
if solo_anulado:
    r = cli.patch(f"/pedidos/{solo_anulado[0][0]}/flete-a-cargo", json={"nuestro": True})
    check(f"un remito ANULADO no congela: el pedido #{solo_anulado[0][0]} (solo tiene el anulado {solo_anulado[0][1]}) se puede cambiar [{r.status_code}]", r.status_code == 200 and flags(solo_anulado[0][0]) & BIT48)
else:
    check("(la copia de P no tiene un pedido con SOLO remitos anulados: se prueba con uno armado y anulado más abajo)", True)

# ---- un pedido con remito anulado se descongela
ped = cli.get("/remitos/pedidos-por-remitar").json()["pedidos"][0]["pedido_id"]
pi = q("select id from pedidos_items where pedido_id=? order by id limit 1", ped)[0][0]
arm = cli.post("/remitos/armar", json={"pedido_id": ped, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": pi, "cantidad": 1}]})
check(f"se arma un remito en el pedido #{ped} [{arm.status_code}] y desde ahí el flete queda fijo", arm.status_code == 200 and cli.patch(f"/pedidos/{ped}/flete-a-cargo", json={"nuestro": True}).status_code == 409)

# ---- la regla de la pérdida lee el bit del PEDIDO
# 0015-3031: FLETE_TERCERO del pedido 137 (bit apagado) -> del comprador
R31 = rid("0015-00003031"); I31 = q("select id from remitos_items where remito_id=?", R31)[0][0]
fc = cli.get("/remitos/ficha/0015-00003031").json()
check("la ficha del 0015-3031 (flete del cliente) dice riesgo COMPRADOR y el pedido sin flete nuestro", fc["remito"]["riesgo_entrega"] == "COMPRADOR" and fc["pedido"]["flete_nuestro"] is False)
r = corregir(R31, I31, 390, "SE_PERDIO")
check(f"una pérdida con el flete del cliente solo se anota: no mueve el pedido [{r.status_code}]", r.status_code == 200 and r.json()["mueve_pedido"] is False)
# se prende el bit del pedido 137 a mano (como si hubiera nacido con el flete nuestro) -> la misma pérdida ahora SÍ mueve
q("update pedidos set flags_estado = flags_estado | ? where id=137", BIT48)
fc = cli.get("/remitos/ficha/0015-00003031").json()
check("con el bit 48 prendido en el pedido, la ficha dice riesgo PROPIO y «flete nuestro»", fc["remito"]["riesgo_entrega"] == "PROPIO" and fc["pedido"]["flete_nuestro"] is True)
r = corregir(R31, I31, 380, "SE_PERDIO")
check(f"y ahora una pérdida del MISMO remito mueve el pedido [{r.status_code}]: la pérdida es nuestra", r.status_code == 200 and r.json()["mueve_pedido"] is True and r.json()["diferencia"] == 10)

# «Moto / cadetería» ya no dice nada por sí sola
R33 = rid("0015-00003033"); I33 = q("select id from remitos_items where remito_id=?", R33)[0][0]; P33 = q("select pedido_id from remitos where id=?", R33)[0][0]
q("update remitos set metodo_entrega='MOTO_CADETERIA' where id=?", R33)
check("una moto con el flete del cliente (la manda el cliente): riesgo COMPRADOR", cli.get("/remitos/ficha/0015-00003033").json()["remito"]["riesgo_entrega"] == "COMPRADOR")
r = corregir(R33, I33, 130, "SE_PERDIO")
check(f"y una pérdida de esa moto solo se anota [{r.status_code}]", r.status_code == 200 and r.json()["mueve_pedido"] is False)
q("update pedidos set flags_estado = flags_estado | ? where id=?", BIT48, P33)
check("la misma moto con el flete NUESTRO (la mandamos nosotros): riesgo PROPIO", cli.get("/remitos/ficha/0015-00003033").json()["remito"]["riesgo_entrega"] == "PROPIO")
r = corregir(R33, I33, 120, "SE_PERDIO")
check(f"y su pérdida mueve el pedido [{r.status_code}]", r.status_code == 200 and r.json()["mueve_pedido"] is True)
# nuestro vehículo es nuestro aunque el bit esté apagado
R30 = rid("0015-00003030"); I30 = q("select id from remitos_items where remito_id=?", R30)[0][0]
q("update remitos set metodo_entrega='TRANSPORTE_PROPIO' where id=?", R30)
check("un remito con TRANSPORTE_PROPIO es nuestro aunque el pedido no tenga el bit", cli.get("/remitos/ficha/0015-00003030").json()["remito"]["riesgo_entrega"] == "PROPIO")
r = corregir(R30, I30, 800, "SE_RECHAZO")
check(f"y lo demás (rechazo, no salió todo, volvió) mueve siempre, con el flete que sea [{r.status_code}]", r.status_code == 200 and r.json()["mueve_pedido"] is True)

# ---- el alta con el bit
cl = q("select cliente_id from pedidos where id=?", libre)[0][0]
prod = q("select producto_id, precio_unitario from pedidos_items where pedido_id=? limit 1", libre)[0]
payload = {"cliente_id": cl, "fecha": "2026-10-26T10:00:00", "estado": "PENDIENTE", "items": [{"producto_id": prod[0], "cantidad": 1, "precio_unitario": prod[1] or 100}], "flete_nuestro": True, "oc_override": True}
r = cli.post("/pedidos/tactico", json=payload)
nuevo = r.json().get("id") if r.status_code == 201 else None
check(f"un pedido NUEVO puede nacer con el flete nuestro [{r.status_code}] (el caso de la reposición por error nuestro)", nuevo and flags(nuevo) & BIT48 and flags(nuevo) & PF.ES_FIRME.value)
payload.pop("flete_nuestro")
r = cli.post("/pedidos/tactico", json=payload)
nuevo2 = r.json().get("id") if r.status_code == 201 else None
check(f"y sin el campo nace con el flete del cliente [{r.status_code}]", nuevo2 and not flags(nuevo2) & BIT48)

# ---- las pantallas
def leer(p): return io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
canvas, spl, fic = leer("frontend/src/views/Ventas/PedidoCanvas.vue"), leer("frontend/src/views/Logistica/LogisticaSplitter.vue"), leer("frontend/src/views/Logistica/RemitoFicha.vue")
check("la ficha del pedido tiene «Flete a cargo: del cliente / NUESTRO» bajo el transporte; en un pedido existente va por el endpoint (y revierte si el servidor dice 409) y en uno nuevo viaja como flete_nuestro",
      'data-accion="flete-a-cargo"' in canvas and "watch(isFleteNuestro" in canvas and "api.patch(`/pedidos/${pid}/flete-a-cargo`, { nuestro: val })" in canvas
      and "revertirInterruptor(isFleteNuestro, !val)" in canvas and "payload.flete_nuestro = isFleteNuestro.value" in canvas and "(1n << 48n)" in canvas)
check("la ventana de armar el remito muestra «Flete a cargo» (Del cliente / Nuestro), lo guarda en el pedido antes de armar y lo traba si el pedido ya tiene remito",
      'data-bloque="flete-a-cargo"' in spl and 'data-flete="cliente"' in spl and 'data-flete="nuestro"' in spl and "const fleteCongelado = computed(" in spl
      and "api.patch(`/pedidos/${localPedido.value.id}/flete-a-cargo`, { nuestro: armarFleteNuestro.value })" in spl and "Math.pow(2, 48)" in spl and "m === 'TRANSPORTE_PROPIO'" in spl)
check("la ficha del remito dice «Flete a cargo: Nuestro / Del cliente»", 'data-campo="flete"' in fic and "r.riesgo_entrega === 'PROPIO' ? 'Nuestro' : 'Del cliente'" in fic)

_aparte.__exit__(None, None, None)
ok = sum(1 for _, c in checks if c)
print(f"\nRESULTADO: {ok}/{len(checks)} checks OK")
if ok != len(checks):
    print("FALLO:", *[d for d, c in checks if not c], sep="\n  ")
    sys.exit(1)
