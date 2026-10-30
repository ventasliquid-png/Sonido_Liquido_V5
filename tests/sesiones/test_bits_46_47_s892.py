r"""S892, Nike (Sello de Oro, 23/10, cuarta consulta): dos calificadores irreversibles de RemitoFlags.
Bit 46 CIRCULACION_ROSA: un 0015 de un pedido Rosa (cuando lo despacha un transporte hace falta un remito de verdad): EGRESO + este bit; no se
factura. Bit 47 SALIDA_CONFIRMADA: una persona (o la guía, o la copia firmada) confirmó que salió; sin el bit, la salida es la asumida al emitir.
(1) Valores de Nike. (2) La función del genoma. (3) migrate_067 sobre una copia de P (simulando una base que ya tenía la 066 de ayer): los 6
Rosa con 0015 reales de P y los remitos EN_CAMINO / ENTREGADO; idempotente; no toca otros bits. (4) Los endpoints: «Salió sin papel» y «Retiró el
transporte» confirman; imprimir NO confirma; un Rosa con 0015 queda con el bit 46 sea por la impresión o sin papel. (5) Insignia (estática)."""
import sys, os, shutil, sqlite3, glob, subprocess, io
from _esquema_p import asegurar_esquema, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.remitos.genoma import calcular_flags, describir
from backend.remitos.constants import RemitoFlags as F

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ROSA, NO_COM = 1 << 12, 1 << 11
B46, B47 = 1 << 46, 1 << 47

# ---- (1) los valores que dio Nike
check("CIRCULACION_ROSA = 1 << 46 = 70368744177664 y SALIDA_CONFIRMADA = 1 << 47 = 140737488355328 (los de Nike)",
      int(F.CIRCULACION_ROSA) == 70368744177664 == B46 and int(F.SALIDA_CONFIRMADA) == 140737488355328 == B47)

# ---- (2) la función del genoma
def m(flags_prev, num, est, pf): return describir(calcular_flags(flags_prev, num, est, pf))["marcas"]
check("Rosa con 0015 -> CIRCULACION_ROSA, también en borrador y en camino; el Blanco con 0015 no la tiene",
      "CIRCULACION_ROSA" in m(0, "0015-00000001", "BORRADOR", ROSA) and "CIRCULACION_ROSA" in m(0, "0015-00000001", "EN_CAMINO", ROSA)
      and "CIRCULACION_ROSA" not in m(0, "0015-00000001", "BORRADOR", 0))
check("el RI (Rosa sin traslado) y el remito sin número NO llevan CIRCULACION_ROSA",
      "CIRCULACION_ROSA" not in m(0, "RI-00000001", "BORRADOR", ROSA) and "CIRCULACION_ROSA" not in m(0, None, "BORRADOR", ROSA))
check("clase EGRESO se mantiene en el Rosa con 0015 (Nike: nace EGRESO y enciende el 46)",
      describir(calcular_flags(0, "0015-00000001", "BORRADOR", ROSA))["clase"] == "EGRESO")
check("SALIDA_CONFIRMADA: EN_CAMINO y ENTREGADO sí (alguien despachó o recibió); BORRADOR con número y sin número no (es la salida asumida)",
      "SALIDA_CONFIRMADA" in m(0, "0015-00000001", "EN_CAMINO", 0) and "SALIDA_CONFIRMADA" in m(0, "0015-00000001", "ENTREGADO", 0)
      and "SALIDA_CONFIRMADA" not in m(0, "0015-00000001", "BORRADOR", 0) and "SALIDA_CONFIRMADA" not in m(0, None, "BORRADOR", 0))
check("irreversibles: un remito con el bit 47 que vuelve a BORRADOR, o con el 46 cuyo pedido deja de ser Rosa, los conserva",
      "SALIDA_CONFIRMADA" in m(B47, "0015-00000001", "BORRADOR", 0) and "CIRCULACION_ROSA" in m(B46, "0015-00000001", "BORRADOR", 0))
check("una Rosa de avíos (no comercial) con 0015 también lleva el 46",
      "CIRCULACION_ROSA" in m(0, "0015-00000001", "BORRADOR", ROSA | NO_COM))

# ---- (3) la migración sobre una copia de P
ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_*.db"))[-1]
TMP = os.path.join(RAIZ, "scratch", "test_bits_46_47_s892"); os.makedirs(TMP, exist_ok=True)
T = os.path.join(TMP, "P.db"); shutil.copyfile(ORIG, T)
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
def correr(nombre):
    return subprocess.run([PY, "-X", "utf8", os.path.join(RAIZ, "scripts", nombre)], capture_output=True, text=True, encoding="utf-8",
                          env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
r66 = correr("migrate_066_remitos_genoma_fecha_emision.py")
asegurar_esquema(T)
def q(sql, *a):
    con = sqlite3.connect(T); x = con.execute(sql, a).fetchall(); con.commit(); con.close(); return x
# la base de ayer: la 066 sin los bits nuevos y sin la 067 registrada
q("update remitos set flags_estado = flags_estado & ~? & ~?", B46, B47)
q("delete from _migraciones_aplicadas where id='067_remitos_calificadores_46_47'")
antes = {i: (f, e, n, fs) for i, f, e, n, fs in q("select id, flags_estado, estado, numero_legal, fecha_salida from remitos")}
r = correr("migrate_067_remitos_calificadores_46_47.py")
check(f"migrate_067 sobre la copia de P [rc {r.returncode}]", r.returncode == 0 and "OK" in r.stdout and "067_remitos_calificadores_46_47 registrada" in r.stdout)
rosa0015 = q("select r.numero_legal, r.flags_estado from remitos r join pedidos p on p.id=r.pedido_id where (p.flags_estado>>12)&1=1 and r.numero_legal like '0015-%'")
check(f"los {len(rosa0015)} Rosa con 0015 de P (3011, 3012, 3013, 3016, 3017, 3020) quedan con CIRCULACION_ROSA",
      len(rosa0015) == 6 and all(f & B46 for _, f in rosa0015))
blancos = q("select count(*) from remitos r join pedidos p on p.id=r.pedido_id where (p.flags_estado>>12)&1=0 and r.flags_estado & ?", B46)[0][0]
check("ningún remito de un pedido Blanco la recibe", blancos == 0)
mov = q("select numero_legal, estado, flags_estado from remitos where numero_legal is not null and estado in ('EN_CAMINO','ENTREGADO')")
check(f"los {len(mov)} remitos EN_CAMINO o ENTREGADO quedan con SALIDA_CONFIRMADA", len(mov) > 0 and all(f & B47 for _, _, f in mov))
bor = q("select count(*) from remitos where numero_legal is not null and estado in ('BORRADOR') and flags_estado & ?", B47)[0][0]
check("los BORRADOR con número siguen con la salida asumida (sin el bit 47)", bor == 0)
despues = {i: (f, e, n, fs) for i, f, e, n, fs in q("select id, flags_estado, estado, numero_legal, fecha_salida from remitos")}
solo_46_47 = all((antes[i][0] ^ despues[i][0]) & ~(B46 | B47) == 0 and antes[i][1:] == despues[i][1:] for i in antes)
check("la migración no toca ningún otro bit, estado, número ni fecha", solo_46_47)
r = correr("migrate_067_remitos_calificadores_46_47.py")
check("idempotente: corrida otra vez, SKIP", r.returncode == 0 and "SKIP" in r.stdout)

# ---- (4) los endpoints
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
def pend(rosa):
    return [x for x in q(f"""select p.id, pi.id, pi.cantidad - coalesce((select sum(ri.cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id
        where ri.pedido_item_id=pi.id and r.estado<>'ANULADO'), 0) from pedidos p join pedidos_items pi on pi.pedido_id=p.id
        where p.estado='PENDIENTE' and ((p.flags_estado>>12)&1)={1 if rosa else 0} and (p.flags_estado>>11)&1=0 order by p.id desc""") if x[2] and x[2] > 0]
def armar(pedido, item, cant):
    r = cli.post("/remitos/armar", json={"pedido_id": pedido, "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": item, "cantidad": cant}]})
    return r.json()["id"] if r.status_code == 200 else ""
def fl(rid): return q("select flags_estado from remitos where id=?", rid.replace("-", ""))[0][0]
bl, ro = pend(False), pend(True)
a = armar(*bl[0]); cli.post(f"/remitos/{a}/salida-sin-papel", json={})
check("«Salió sin papel» (Blanco): salida CONFIRMADA y sin CIRCULACION_ROSA", fl(a) & B47 and not fl(a) & B46)
b = armar(*bl[1]); cli.get(f"/remitos/{b}/pdf")
check("imprimir un Blanco NO confirma la salida (queda la asumida al emitir)", not fl(b) & B47 and not fl(b) & B46)
cli.post(f"/remitos/{b}/en-deposito")
check("«Queda en depósito» tampoco la confirma", not fl(b) & B47)
cli.post(f"/remitos/{b}/retiro", json={})
check("«Retiró el transporte»: salida CONFIRMADA", bool(fl(b) & B47))
c = armar(*ro[0]); cli.post(f"/remitos/{c}/salida-sin-papel", json={})
check(f"Rosa real #{ro[0][0]} «Salió sin papel»: CIRCULACION_ROSA y SALIDA_CONFIRMADA", fl(c) & B46 and fl(c) & B47)
otro = next(x for x in ro if x[0] != ro[0][0])
d = armar(*otro); cli.get(f"/remitos/{d}/pdf")
check(f"Rosa #{otro[0]} por la impresión de siempre: CIRCULACION_ROSA, salida todavía asumida", fl(d) & B46 and not fl(d) & B47)

# ---- (5) insignia (estática)
lista = io.open(os.path.join(RAIZ, "frontend", "src", "views", "Logistica", "RemitoListView.vue"), encoding="utf-8").read()
check("listado: insignia «Rosa · no se factura» bajo el número, leyendo el bit 46 con aritmética",
      'data-marca="rosa-no-facturable"' in lista and "tieneBit(remito.flags_estado, 46)" in lista and "Rosa · no se factura" in lista)

del cli; eng.dispose()
for n in (set(os.listdir(SALIDA)) - previos) if os.path.isdir(SALIDA) else []:
    os.remove(os.path.join(SALIDA, n))
_aparte.__exit__(None, None, None)
shutil.rmtree(TMP, ignore_errors=True)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
