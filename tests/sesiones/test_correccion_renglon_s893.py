r"""S893, Carlos 26/10: «las discrepancias no pueden vivir solo en una nota: si un remito salió con m y quedó p (se perdió, se rechazó, volvió, no salió todo), eso tiene que mover
el renglón del pedido; si no, el sistema cree que el pedido se cumplió y la realidad es que debemos». La CORRECCIÓN de un renglón (POST /remitos/{id}/correccion):
(1) migrate_069 (corrige_item_id y causa en remitos_items, idempotente, sin tocar datos); (2) las guardas (causa, remito con número y no anulado, 0 <= quedó < lo de hoy, no se corrige
una corrección); (3) el efecto: un renglón negativo atado al de origen, el pedido vuelve a deber la diferencia y, si estaba CUMPLIDO, se reabre; lo impreso y lo que salió del remito de
origen no cambian; «llegó» y DIFERENCIA_RECEPCION según la causa; notas con autor; (4) la ficha lo muestra; (5) una corrección no se imprime, no se anula por la vía común y se deshace
con motivo; (6) «Nuevo remito» (F4) elige un pedido: GET /remitos/pedidos-por-remitar.
(7) [Carlos 26/10] QUIÉN CARGA CON LA PÉRDIDA: con el transporte que eligió el comprador (FLETE_TERCERO), mostrador o su guía (y los remitos sin método) lo que se PIERDE es del comprador: se anota,
se factura lo que salió y el pedido no vuelve a deber (renglón de corrección con cantidad_remitida en 0); con el flete nuestro (bit 48 FLETE_A_CARGO_NUESTRO del pedido, o un remito con TRANSPORTE_PROPIO) mueve el pedido; no salió todo, se rechazó
y volvió mueven siempre. Sobre una COPIA de P con migrate_066, 068 y 069."""
import sys, os, shutil, sqlite3, glob, subprocess
from _esquema_p import asegurar_esquema, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
# [S895] Fijada a la copia de P del 28/10 12:52, ANTERIOR al despliegue del paquete (Tomy relanzó a las 13:03): esta prueba corre migraciones sobre la copia de P
# y con una copia más nueva ya vienen aplicadas (SKIP). Mismo criterio que las de la S890 (auditoría de CA, 28/10).
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261028_1252.db"
TMP = os.path.join(RAIZ, "scratch", "test_correccion_renglon_s893"); os.makedirs(TMP, exist_ok=True)
T = os.path.join(TMP, "P.db"); shutil.copyfile(ORIG, T)
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
def correr(nombre):
    return subprocess.run([PY, "-X", "utf8", os.path.join(RAIZ, "scripts", nombre)], capture_output=True, text=True, encoding="utf-8",
                          env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
def q(sql, *a):
    con = sqlite3.connect(T); x = con.execute(sql, a).fetchall(); con.commit(); con.close(); return x
r66, r68 = correr("migrate_066_remitos_genoma_fecha_emision.py"), correr("migrate_068_remitos_oc.py")
check(f"setup: copia de P con migrate_066 y 068 [rc {r66.returncode}, {r68.returncode}]", r66.returncode == 0 and r68.returncode == 0)

# ---- (1) migrate_069
cols_antes = [c[1] for c in q("pragma table_info(remitos_items)")]
r69 = correr("migrate_069_remitos_items_correccion.py")
cols = [c[1] for c in q("pragma table_info(remitos_items)")]
check(f"migrate_069 [rc {r69.returncode}]: agrega remitos_items.corrige_item_id y causa (antes no estaban)",
      r69.returncode == 0 and "corrige_item_id" not in cols_antes and "corrige_item_id" in cols and "causa" in cols and "069_remitos_items_correccion registrada" in r69.stdout)
check("todos los renglones quedan como renglón común (NULL, NULL)", q("select count(*) from remitos_items where corrige_item_id is not null or causa is not null")[0][0] == 0)
check("idempotente: otra vez, SKIP", "SKIP" in correr("migrate_069_remitos_items_correccion.py").stdout)
asegurar_esquema(T)

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
def hx(x): return str(x).replace("-", "")
def rid(numero): return q("select id from remitos where numero_legal=?", numero)[0][0]
def corregir(remito_id, item_id, real, causa, nota=None):
    return cli.post(f"/remitos/{remito_id}/correccion", json={"remito_item_id": item_id, "cantidad_real": real, "causa": causa, "nota": nota})
def entregada(pedido_item_id):
    return q("""select coalesce(sum(ri.cantidad_remitida),0) from remitos_items ri join remitos r on r.id=ri.remito_id
                where ri.pedido_item_id=? and r.estado != 'ANULADO'""", pedido_item_id)[0][0]
BIT_FIRME, BIT_CUMPLIDO, BIT_DIFERENCIA = 1 << 33, 1 << 34, 1 << 42

# ---- (6) «Nuevo remito» (F4): el pedido se elige entre los que tienen algo por remitir
lista = cli.get("/remitos/pedidos-por-remitar").json()
ids = [p["pedido_id"] for p in lista["pedidos"]]
estados = {r[0]: r[1] for r in q("select id, estado from pedidos")}
check(f"pedidos-por-remitar: {len(ids)} pedidos abiertos con algo pendiente, todos PENDIENTE o RESERVADO y ninguno CUMPLIDO ni ANULADO",
      len(ids) > 0 and all(estados[i] in ("PENDIENTE", "RESERVADO") for i in ids) and 136 not in ids)
f0 = lista["pedidos"][0]
check("cada fila trae pedido, cliente, renglones pendientes (> 0) y un resumen", all(k in f0 for k in ("pedido_id", "cliente", "oc", "fecha", "renglones_pendientes", "resumen")) and all(p["renglones_pendientes"] > 0 for p in lista["pedidos"]))
check("por «#<pedido>» trae ese pedido", [p["pedido_id"] for p in cli.get("/remitos/pedidos-por-remitar", params={"q": f"#{f0['pedido_id']}"}).json()["pedidos"]] == [f0["pedido_id"]])
check("por una palabra del cliente (sin acentos ni mayúsculas) lo trae", f0["pedido_id"] in [p["pedido_id"] for p in cli.get("/remitos/pedidos-por-remitar", params={"q": f0["cliente"].split()[0].lower()}).json()["pedidos"]])
check("un texto que no existe no trae nada", cli.get("/remitos/pedidos-por-remitar", params={"q": "zzzqqq"}).json()["total"] == 0)

# ---- (2) guardas
q("update remitos set metodo_entrega='TRANSPORTE_PROPIO' where numero_legal='0015-00003030'")   # en P es mostrador: acá sale con flete propio, para que la pérdida sea NUESTRA
q("update pedidos set flags_estado = flags_estado | ? where id=(select pedido_id from remitos where numero_legal='0015-00003033')", 1 << 48)   # el flete de ese pedido es NUESTRO (bit 48, Nike 26/10)
R30, I30 = rid("0015-00003030"), q("select id from remitos_items where remito_id=?", rid("0015-00003030"))[0][0]   # 0015-3030: ENTREGADO, pedido 136 CUMPLIDO, 876
PI30 = q("select pedido_item_id from remitos_items where id=?", I30)[0][0]
r = corregir(R30, I30, 800, "SE_ROMPIO")
check("una causa que no existe: 409 CAUSA_INVALIDA", r.status_code == 409 and "CAUSA_INVALIDA" in r.text)
r = corregir(R30, 999999, 800, "SE_PERDIO")
check("un renglón que no es de ese remito: 409 RENGLON_AJENO_AL_REMITO", r.status_code == 409 and "RENGLON_AJENO_AL_REMITO" in r.text)
r = corregir(R30, I30, 876, "SE_PERDIO")
check("dejar el renglón igual (876 de 876): 409 SIN_DIFERENCIA", r.status_code == 409 and "SIN_DIFERENCIA" in r.text)
r = corregir(R30, I30, 900, "SE_PERDIO")
check("dejar MÁS de lo que tiene: 409 SIN_DIFERENCIA (una corrección solo baja)", r.status_code == 409 and "SIN_DIFERENCIA" in r.text)
r = corregir(R30, I30, -1, "SE_PERDIO")
check("una cantidad negativa: 409 CANTIDAD_NEGATIVA", r.status_code == 409 and "CANTIDAD_NEGATIVA" in r.text)
anul = q("select r.id, ri.id from remitos r join remitos_items ri on ri.remito_id=r.id where r.estado='ANULADO' and r.numero_legal is not null limit 1")[0]
r = corregir(anul[0], anul[1], 0, "SE_PERDIO")
check("un remito anulado: 409 REMITO_ANULADO", r.status_code == 409 and "REMITO_ANULADO" in r.text)
sin_num = cli.post("/remitos/armar", json={"pedido_id": f0["pedido_id"], "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": q("select id from pedidos_items where pedido_id=? limit 1", f0["pedido_id"])[0][0], "cantidad": 1}]})
if sin_num.status_code == 200:
    rs = sin_num.json(); its = q("select id from remitos_items where remito_id=?", hx(rs["id"]))
    r = corregir(rs["id"], its[0][0], 0, "NO_SALIO")
    check("un remito sin número (todavía no salió): 409 REMITO_SIN_NUMERO", r.status_code == 409 and "REMITO_SIN_NUMERO" in r.text)
else:
    check(f"un remito sin número (todavía no salió): 409 REMITO_SIN_NUMERO [no se pudo armar: {sin_num.status_code} {sin_num.text[:120]}]", False)
check("ninguna guarda dejó rastro: no hay renglones de corrección", q("select count(*) from remitos_items where corrige_item_id is not null")[0][0] == 0)

# ---- (3) el efecto, en el caso real: 0015-3030, 876 unidades, el pedido 136 estaba CUMPLIDO
antes = q("select cantidad_declarada, cantidad_remitida, cantidad_recibida from remitos_items where id=?", I30)[0]
ped_antes = q("select estado, flags_estado from pedidos where id=136")[0]
check("antes: el pedido 136 figura CUMPLIDO y el renglón tiene entregado 876 de 876", ped_antes[0] == "CUMPLIDO" and entregada(PI30) == 876 and antes == (876.0, 876.0, None))
r = corregir(R30, I30, 800, "SE_PERDIO", "se mojó en el camión")
j = r.json() if r.status_code == 200 else {}
check(f"corregir a 800 por «se perdió» [{r.status_code}]: diferencia 76, el pedido se reabre, le quedan 76 por remitir",
      r.status_code == 200 and j.get("diferencia") == 76 and j.get("quedo") == 800 and j.get("pedido_reabierto") is True and j.get("pendiente_del_renglon") == 76)
ped = q("select estado, flags_estado, nota from pedidos where id=136")[0]
check("el pedido 136 deja de estar CUMPLIDO: PENDIENTE, bit FIRME prendido y CUMPLIDO apagado, con una nota [SISTEMA] «Reabierto»",
      ped[0] == "PENDIENTE" and ped[1] & BIT_FIRME and not ped[1] & BIT_CUMPLIDO and "[SISTEMA] Reabierto" in (ped[2] or "") and "se perdió" in ped[2].lower())
check("lo entregado neto del renglón del pedido es 800 (la corrección descuenta, como la devolución de la Etapa 6)", entregada(PI30) == 800)
desp = q("select cantidad_declarada, cantidad_remitida, cantidad_recibida from remitos_items where id=?", I30)[0]
check("el renglón de origen conserva lo IMPRESO y lo que SALIÓ (876) y su «llegó» es lo que quedó (800)", desp == (876.0, 876.0, 800.0))
corr = q("select ri.id, ri.remito_id, ri.cantidad_remitida, ri.cantidad_declarada, ri.corrige_item_id, ri.causa, r.numero_legal, r.estado, r.metodo_entrega from remitos_items ri join remitos r on r.id=ri.remito_id where ri.corrige_item_id=?", I30)
check("hay UN renglón de corrección: -76, atado al de origen, causa SE_PERDIO, en un remito nuevo SIN número que nace ENTREGADO",
      len(corr) == 1 and corr[0][2] == -76 and corr[0][3] == -76 and corr[0][4] == I30 and corr[0][5] == "SE_PERDIO" and corr[0][6] is None and corr[0][7] == "ENTREGADO")
RC, IC = corr[0][1], corr[0][0]
f_origen = q("select flags_estado from remitos where id=?", R30)[0][0]
check("el genoma del remito de origen prende DIFERENCIA_RECEPCION (bit 42: llegó distinto de lo que salió)", f_origen & BIT_DIFERENCIA)
notas_o = q("select texto, autor_id, remito_item_id from remitos_notas where remito_id=? and texto like '[CORRECCIÓN]%'", R30)
notas_c = q("select texto, autor_id from remitos_notas where remito_id=? and texto like '[CORRECCIÓN]%'", RC)
check("queda una nota con autor en el remito de origen (sobre el renglón, con la causa, la cantidad y lo que escribió el operador) y otra en el de corrección",
      len(notas_o) == 1 and notas_o[0][1] == 1 and notas_o[0][2] == I30 and "Se perdió" in notas_o[0][0] and "76" in notas_o[0][0] and "se mojó en el camión" in notas_o[0][0]
      and len(notas_c) == 1 and "0015-00003030" in notas_c[0][0])
check("el pedido vuelve a figurar entre los que tienen algo por remitir (F4 lo ofrece, con 76)",
      any(p["pedido_id"] == 136 and "76" in p["resumen"] for p in cli.get("/remitos/pedidos-por-remitar", params={"q": "#136"}).json()["pedidos"]))

# ---- (4) la ficha
fo = cli.get("/remitos/ficha/0015-00003030").json()
it = fo["items"][0]
check("la ficha dice quién carga con el riesgo de esa entrega: flete propio -> PROPIO",
      cli.get("/remitos/ficha/0015-00003030").json()["remito"]["riesgo_entrega"] == "PROPIO" and cli.get("/remitos/ficha/0015-00003031").json()["remito"]["riesgo_entrega"] == "COMPRADOR")
check("la ficha del remito de origen: salió 876, corregido 76, quedó 800, llegó 800, con su corrección (causa y cantidad) y el pedido PENDIENTE",
      it["salio"] == 876 and it["impreso"] == 876 and it["corregido"] == 76 and it["quedo"] == 800 and it["llego"] == 800 and len(it["correcciones"]) == 1
      and it["correcciones"][0]["causa"] == "SE_PERDIO" and it["correcciones"][0]["cantidad"] == 76 and fo["pedido"]["estado"] == "PENDIENTE"
      and "DIFERENCIA_RECEPCION" in fo["remito"]["genoma"]["marcas"] and fo["remito"]["es_correccion"] is False)
fc = cli.get(f"/remitos/ficha/{RC}").json()
check("la ficha del remito de corrección: es_correccion, su renglón dice a qué remito corrige (0015-00003030) y por qué",
      fc["remito"]["es_correccion"] is True and fc["items"][0]["corrige"]["numero_legal"] == "0015-00003030" and fc["items"][0]["causa"] == "SE_PERDIO" and fc["items"][0]["salio"] == -76)
lst = cli.get("/remitos/").json()
mio = next((x for x in lst if hx(x["id"]) == hx(RC)), None)
check("el listado de remitos incluye la corrección con corrige_item_id y causa en su renglón", mio is not None and mio["items"][0]["corrige_item_id"] == I30 and mio["items"][0]["causa"] == "SE_PERDIO")

# ---- una segunda corrección sobre el mismo renglón: «volvió» (llegó todo y volvió una parte)
r = corregir(R30, I30, 790, "VOLVIO")
check(f"una segunda corrección sobre el mismo renglón, calculada sobre lo que tiene HOY (800): «volvió» y quedan 790 [{r.status_code}]",
      r.status_code == 200 and r.json()["diferencia"] == 10 and r.json()["pedido_reabierto"] is False and r.json()["pendiente_del_renglon"] == 86 and entregada(PI30) == 790)
check("«volvió» no cambia lo que llegó (llegó 800: llegó todo lo que no se perdió, y después volvió una parte)", q("select cantidad_recibida from remitos_items where id=?", I30)[0][0] == 800)
r = corregir(R30, I30, 795, "SE_PERDIO")
check("y no se puede «corregir» hacia arriba de lo que tiene hoy (795 > 790): 409 SIN_DIFERENCIA", r.status_code == 409 and "SIN_DIFERENCIA" in r.text)

# ---- (5) una corrección no se imprime, no se anula por la vía común, no se borra, no se corrige
r = corregir(RC, IC, 0, "SE_PERDIO")
check("un renglón de corrección no se corrige: 409 RENGLON_DE_CORRECCION", r.status_code == 409 and "RENGLON_DE_CORRECCION" in r.text)
r = cli.get(f"/remitos/{RC}/pdf")
check("no tiene papel: el PDF es 409 CORRECCION_NO_SE_IMPRIME y no toma número", r.status_code == 409 and "CORRECCION_NO_SE_IMPRIME" in r.text and q("select numero_legal from remitos where id=?", RC)[0][0] is None)
r = cli.post(f"/remitos/{RC}/anular", json={"motivo": "x"})
check("«anular» no vale para una corrección: 409 ES_UNA_CORRECCION", r.status_code == 409 and "ES_UNA_CORRECCION" in r.text)
r = cli.delete(f"/remitos/{RC}")
check("el tacho tampoco (no es BORRADOR): 400", r.status_code == 400)

# ---- deshacer la corrección (la de «se perdió»), con motivo
r = cli.post(f"/remitos/{RC}/deshacer-correccion", json={"motivo": ""})
check("deshacer sin motivo: 422", r.status_code == 422 and "MOTIVO_OBLIGATORIO" in r.text)
r = cli.post(f"/remitos/{R30}/deshacer-correccion", json={"motivo": "x"})
check("deshacer sobre un remito común: 409 NO_ES_CORRECCION", r.status_code == 409 and "NO_ES_CORRECCION" in r.text)
r = cli.post(f"/remitos/{RC}/deshacer-correccion", json={"motivo": "eran 350, no 300"})
check(f"deshacer con motivo [{r.status_code}]: la corrección queda ANULADA, el renglón recupera los 76 (entregado 866 = 876 menos solo lo que volvió)",
      r.status_code == 200 and q("select estado from remitos where id=?", RC)[0][0] == "ANULADO" and entregada(PI30) == 866)
check("«llegó» del renglón de origen se recalcula: sin ninguna corrección de «se perdió» vigente queda NULL (llegó lo que salió)", q("select cantidad_recibida from remitos_items where id=?", I30)[0][0] is None)
check("queda una nota [SISTEMA] en la corrección y otra en el renglón de origen, con el motivo",
      q("select count(*) from remitos_notas where remito_id=? and texto like '[SISTEMA] Corrección deshecha%eran 350%'", RC)[0][0] == 1
      and q("select count(*) from remitos_notas where remito_id=? and remito_item_id=? and texto like '[SISTEMA] Corrección deshecha%'", R30, I30)[0][0] == 1)
r = cli.post(f"/remitos/{RC}/deshacer-correccion", json={"motivo": "otra vez"})
check("deshacer dos veces: 409 REMITO_YA_ANULADO", r.status_code == 409 and "REMITO_YA_ANULADO" in r.text)
r = cli.post(f"/remitos/{RC}/deshacer-anulacion", json={"motivo": "revivir"})
check("una corrección deshecha no se revive: 409 CORRECCION_DESHECHA", r.status_code == 409 and "CORRECCION_DESHECHA" in r.text)
fo2 = cli.get("/remitos/ficha/0015-00003030").json()["items"][0]
check("la ficha del origen ya no cuenta la deshecha: corregido 10 (lo que volvió), quedó 866", fo2["corregido"] == 10 and fo2["quedo"] == 866 and len(fo2["correcciones"]) == 1)

# ---- el pedido que NO estaba cumplido no se «reabre»; y «no salió todo» baja «llegó» también
R31 = rid("0015-00003031"); I31 = q("select id from remitos_items where remito_id=?", R31)[0][0]
r = corregir(R31, I31, 350, "SE_RECHAZO")
PI31 = q("select pedido_item_id from remitos_items where id=?", I31)[0][0]
CANT31 = q("select cantidad from pedidos_items where id=?", PI31)[0][0]
check(f"0015-3031 (400, pedido 137 PENDIENTE) con 350 «se rechazó» [{r.status_code}]: el pedido NO se reabre (ya estaba abierto) y el renglón vuelve a deber lo que no quedó",
      r.status_code == 200 and r.json()["pedido_reabierto"] is False and r.json()["pendiente_del_renglon"] == CANT31 - 350 and entregada(PI31) == 350)
R33 = rid("0015-00003033"); I33 = q("select id from remitos_items where remito_id=?", R33)[0][0]
r = corregir(R33, I33, 100, "NO_SALIO")
check(f"0015-3033 (144) con 100 «no salió todo» [{r.status_code}]: llegó 100 y el remito lo marca", r.status_code == 200 and q("select cantidad_recibida from remitos_items where id=?", I33)[0][0] == 100
      and q("select flags_estado from remitos where id=?", R33)[0][0] & BIT_DIFERENCIA)
r = corregir(R33, I33, 0, "SE_PERDIO")
PI33 = q("select pedido_item_id from remitos_items where id=?", I33)[0][0]
check("se puede dejar el renglón en CERO (se perdió todo lo que quedaba): llegó 0 y el pedido lo vuelve a deber entero", r.status_code == 200 and q("select cantidad_recibida from remitos_items where id=?", I33)[0][0] == 0 and entregada(PI33) == 0)


# ---- (7) QUIÉN CARGA CON LA PÉRDIDA
# 0015-3028: remito SIN método (anterior a la S876), pedido 132 CUMPLIDO, 5 unidades -> se toma como entrega por el transporte del comprador
R28 = rid("0015-00003028"); I28 = q("select id from remitos_items where remito_id=?", R28)[0][0]; PI28 = q("select pedido_item_id from remitos_items where id=?", I28)[0][0]
check("antes: el pedido 132 figura CUMPLIDO, el remito 3028 no tiene método y la ficha lo da como riesgo del COMPRADOR",
      q("select estado from pedidos where id=132")[0][0] == "CUMPLIDO" and q("select metodo_entrega from remitos where id=?", R28)[0][0] is None and entregada(PI28) == 5
      and cli.get("/remitos/ficha/0015-00003028").json()["remito"]["riesgo_entrega"] == "COMPRADOR")
r = corregir(R28, I28, 3, "SE_PERDIO", "el expreso avisó que se mojó")
j = r.json() if r.status_code == 200 else {}
check(f"se perdieron 2 en el camino con el transporte del comprador [{r.status_code}]: se anota, NO mueve el pedido ni lo reabre y se factura lo que salió",
      r.status_code == 200 and j.get("mueve_pedido") is False and j.get("pedido_reabierto") is False and j.get("diferencia") == 2 and q("select estado from pedidos where id=132")[0][0] == "CUMPLIDO" and entregada(PI28) == 5)
fila = q("select cantidad_declarada, cantidad_remitida, causa, corrige_item_id from remitos_items where corrige_item_id=?", I28)
check(f"queda el registro: renglón de corrección con cantidad_declarada -2 y cantidad_remitida 0 (no mueve nada), causa SE_PERDIO: {fila}", len(fila) == 1 and fila[0] == (-2.0, 0.0, "SE_PERDIO", I28))
check("«llegó» es 3, el remito marca DIFERENCIA_RECEPCION y la nota dice que la pérdida es del comprador y que se factura lo que salió",
      q("select cantidad_recibida from remitos_items where id=?", I28)[0][0] == 3 and q("select flags_estado from remitos where id=?", R28)[0][0] & BIT_DIFERENCIA
      and "pérdida es del comprador" in q("select texto from remitos_notas where remito_id=? and remito_item_id=? and texto like '[CORRECCIÓN]%'", R28, I28)[0][0])
f28 = cli.get("/remitos/ficha/0015-00003028").json()["items"][0]
check("la ficha: salió 5, corregido 2, quedó 3, y esa corrección figura como «no mueve el pedido»", f28["salio"] == 5 and f28["corregido"] == 2 and f28["quedo"] == 3 and f28["correcciones"][0]["mueve_pedido"] is False and f28["correcciones"][0]["cantidad"] == 2)
check("el pedido 132 no vuelve a figurar entre los que tienen algo por remitar", 132 not in [p["pedido_id"] for p in cli.get("/remitos/pedidos-por-remitar", params={"q": "#132"}).json()["pedidos"]])
# ahora el cliente RECHAZA 1 de las 3 que llegaron: eso sí mueve el pedido, aunque haya salido con su transporte
r = corregir(R28, I28, 2, "SE_RECHAZO")
j = r.json() if r.status_code == 200 else {}
check(f"el cliente rechazó 1 de las 3 [{r.status_code}]: ahora SÍ mueve el pedido (queda 4 entregado de 5), lo reabre y vuelve a deber 1",
      r.status_code == 200 and j.get("mueve_pedido") is True and j.get("pedido_reabierto") is True and entregada(PI28) == 4 and q("select estado from pedidos where id=132")[0][0] == "PENDIENTE" and j.get("pendiente_del_renglon") == 1)
check("«llegó» = lo que salió menos lo que no llegó por las dos causas (5 - 2 - 1 = 2)", q("select cantidad_recibida from remitos_items where id=?", I28)[0][0] == 2)
rc_registro = q("select ri.remito_id from remitos_items ri where ri.corrige_item_id=? and ri.cantidad_remitida = 0", I28)[0][0]
r = cli.post(f"/remitos/{rc_registro}/deshacer-correccion", json={"motivo": "me equivoqué, no se perdió"})
check(f"se deshace el registro de la pérdida del comprador [{r.status_code}]: «llegó» se recalcula con lo que sigue vigente (5 - 1 = 4) y el pedido sigue como estaba (4 entregado)",
      r.status_code == 200 and q("select cantidad_recibida from remitos_items where id=?", I28)[0][0] == 4 and entregada(PI28) == 4)
# 0015-3032 con FLETE_TERCERO explícito: lo mismo que sin método
R32 = rid("0015-00003032"); I32 = q("select id from remitos_items where remito_id=?", R32)[0][0]; PI32 = q("select pedido_item_id from remitos_items where id=?", I32)[0][0]
q("update remitos set metodo_entrega='FLETE_TERCERO' where numero_legal='0015-00003032'")
r = corregir(R32, I32, 6, "SE_PERDIO")
check(f"con FLETE_TERCERO explícito, una pérdida no mueve el pedido (entregado sigue en 8) [{r.status_code}]", r.status_code == 200 and r.json()["mueve_pedido"] is False and entregada(PI32) == 8)
r = corregir(R32, I32, 5, "NO_SALIO")
check(f"pero «no salió todo» mueve siempre, también con el transporte del comprador [{r.status_code}]: de lo que quedaba (6) queda 5 y la diferencia (1) vuelve a deber; lo perdido antes (2) sigue siendo del comprador: entregado 7",
      r.status_code == 200 and r.json()["mueve_pedido"] is True and r.json()["diferencia"] == 1 and entregada(PI32) == 7)
r = corregir(R30, I30, 780, "VOLVIO")
check(f"y «volvió» mueve siempre (con flete propio o no) [{r.status_code}]", r.status_code == 200 and r.json()["mueve_pedido"] is True)

_aparte.__exit__(None, None, None)
ok = sum(1 for _, c in checks if c)
print(f"\nRESULTADO: {ok}/{len(checks)} checks OK")
if ok != len(checks):
    print("FALLO:", *[d for d, c in checks if not c], sep="\n  ")
    sys.exit(1)
