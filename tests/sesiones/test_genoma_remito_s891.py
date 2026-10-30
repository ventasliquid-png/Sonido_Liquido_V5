r"""S891, paquete 2 de remitos, tramo 1: el genoma del remito (RemitoFlags 29-45, Nike Sello de Oro 22/10) y la fecha de EMISIÓN.
(1) La función pura (backend/remitos/genoma.py): clase por número y pedido, estado, logística, calificadores irreversibles.
(2) migrate_066 sobre una COPIA CRUDA de P: fecha_emision = fecha_creacion en los numerados, salida asumida, genoma de todos, otros bits
    intactos, ningún estado/número tocado, idempotente.
(3) El servidor (evento before_flush) sobre esa copia ya migrada: al tomar número se fijan emisión y salida asumida; IMPRESO al generar
    el PDF; despachar, recibido distinto, anulado, EN_DEPOSITO y salida diferida; cambio de fecha de emisión."""
import sys, os, shutil, sqlite3, glob, subprocess
from datetime import datetime, timedelta
from _esquema_p import asegurar_esquema
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.remitos.genoma import calcular_flags, describir
from backend.remitos.constants import RemitoFlags as F

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
NC, ROSA = 1 << 11, 1 << 12
D = lambda f: describir(f)

# ---- (1) función pura
f = calcular_flags(0, "0015-00003040", "BORRADOR", 0)
check(f"0015 de un pedido comercial: EGRESO / EMITIDO / RETIRADO (salida asumida) {D(f)}", D(f)["clase"] == "EGRESO" and D(f)["estado"] == "EMITIDO" and D(f)["logistica"] == "RETIRADO" and D(f)["activo"])
f = calcular_flags(0, "0015-00003040", "ENTREGADO", NC)
check(f"0015 de un pedido NO COMERCIAL entregado: EGRESO_AVIOS / EMITIDO / RECIBIDO {D(f)}", (D(f)["clase"], D(f)["estado"], D(f)["logistica"]) == ("EGRESO_AVIOS", "EMITIDO", "RECIBIDO"))
f = calcular_flags(0, "RI-00000001", "ENTREGADO", ROSA)
check(f"RI: INTERNO {D(f)}", D(f)["clase"] == "INTERNO" and D(f)["estado"] == "EMITIDO")
f = calcular_flags(0, None, "BORRADOR", ROSA)
check(f"sin número de un pedido Rosa: INTERNO, indeterminado (sin estado ni logística) {D(f)}", D(f)["clase"] == "INTERNO" and D(f)["estado"] is None and D(f)["logistica"] is None)
f = calcular_flags(0, None, "BORRADOR", NC | ROSA)
check("sin número de un pedido no comercial: EGRESO_AVIOS (no comercial manda)", D(f)["clase"] == "EGRESO_AVIOS")
f = calcular_flags(0, "0015-00003040", "ANULADO", 0)
check(f"anulado: ANULADO + FUE_ANULADO, sin logística, no activo {D(f)}", D(f)["estado"] == "ANULADO" and "FUE_ANULADO" in D(f)["marcas"] and D(f)["logistica"] is None and not D(f)["activo"])
f2 = calcular_flags(f, "0015-00003040", "BORRADOR", 0)
check(f"deshacer la anulación: vuelve a EMITIDO y FUE_ANULADO queda (irreversible) {D(f2)}", D(f2)["estado"] == "EMITIDO" and "FUE_ANULADO" in D(f2)["marcas"])
f = calcular_flags(int(F.EN_DEPOSITO), "0015-00003040", "BORRADOR", 0, "2026-10-15 10:00:00", None)
check(f"marcado EN_DEPOSITO y sin salida: sigue EN_DEPOSITO {D(f)}", D(f)["logistica"] == "EN_DEPOSITO")
f = calcular_flags(f, "0015-00003040", "EN_CAMINO", 0, "2026-10-15 10:00:00", "2026-10-22 09:00:00")
check(f"retirado una semana después: RETIRADO + SALIDA_DIFERIDA {D(f)}", D(f)["logistica"] == "RETIRADO" and "SALIDA_DIFERIDA" in D(f)["marcas"])
f = calcular_flags(0, "0015-00003040", "BORRADOR", 0, "2026-10-15 10:00:00", "2026-10-15 18:00:00", hay_diferencia_recepcion=True, impreso=True)
check(f"mismo día: sin SALIDA_DIFERIDA; recibido distinto e impreso: DIFERENCIA_RECEPCION + IMPRESO {D(f)}", "SALIDA_DIFERIDA" not in D(f)["marcas"] and {"DIFERENCIA_RECEPCION", "IMPRESO"} <= set(D(f)["marcas"]))
f = calcular_flags(int(F.IMPRESO | F.DIFERENCIA_RECEPCION | F.VINCULAR_PARCIAL | F.CIRCUITO_ROSA), "0015-00003040", "BORRADOR", 0)
check("los calificadores y los bits viejos (VINCULAR_PARCIAL, CIRCUITO_ROSA) no se apagan al recalcular", f & int(F.IMPRESO) and f & int(F.DIFERENCIA_RECEPCION) and f & int(F.VINCULAR_PARCIAL) and f & int(F.CIRCUITO_ROSA))
f = calcular_flags(int(F.EGRESO | F.EMITIDO | F.RETIRADO), "0015-00003040", "ENTREGADO", NC)
check("las bandas son excluyentes: al recalcular no quedan dos clases ni dos logísticas", bin(f & (int(F.EGRESO) | int(F.EGRESO_AVIOS) | int(F.INTERNO))).count("1") == 1
      and bin(f & (int(F.EN_DEPOSITO) | int(F.RETIRADO) | int(F.RECIBIDO))).count("1") == 1)

# ---- (2) migrate_066 sobre una copia cruda de P
# [S895] Fijada a la copia de P del 28/10 12:52, ANTERIOR al despliegue del paquete (Tomy relanzó a las 13:03): esta prueba corre migraciones sobre la copia de P
# y con una copia más nueva ya vienen aplicadas (SKIP). Mismo criterio que las de la S890 (auditoría de CA, 28/10).
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261028_1252.db"
TMP = os.path.join(RAIZ, "scratch", "test_genoma_s891"); os.makedirs(TMP, exist_ok=True)
T = os.path.join(TMP, "P.db"); shutil.copyfile(ORIG, T)
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
M066 = os.path.join(RAIZ, "scripts", "migrate_066_remitos_genoma_fecha_emision.py")
def q(sql, *a):
    con = sqlite3.connect(T); r = con.execute(sql, a).fetchall(); con.commit(); con.close(); return r
antes = {r[0]: r[1:] for r in q("select id, numero_legal, estado, flags_estado, fecha_creacion, fecha_salida from remitos")}
r = subprocess.run([PY, "-X", "utf8", M066], capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
check(f"migrate_066 corre y se registra [rc {r.returncode}]", r.returncode == 0 and "OK" in r.stdout and q("select 1 from _migraciones_aplicadas where id='066_remitos_genoma_fecha_emision'"))
despues = {r[0]: r[1:] for r in q("select id, numero_legal, estado, flags_estado, fecha_creacion, fecha_salida, fecha_emision from remitos")}
check("no cambia ningún número ni estado ni fecha de creación", all(despues[k][0] == v[0] and despues[k][1] == v[1] and despues[k][3] == v[3] for k, v in antes.items()))
check("los bits viejos quedan (VINCULAR_PARCIAL en los 15 que lo tenían)", sum(1 for v in despues.values() if int(v[2] or 0) & 2048) == sum(1 for v in antes.values() if int(v[2] or 0) & 2048))
num = [v for v in despues.values() if v[0]]
check("todo remito con número tiene fecha_emision = fecha_creacion", all(v[5] == v[3] for v in num))
check("los numerados no anulados que no tenían salida quedan con la salida asumida en la emisión; las salidas que existían no se tocan",
      all((antes[k][4] is None and despues[k][1] != "ANULADO" and despues[k][4] == despues[k][5]) or antes[k][4] == despues[k][4] or despues[k][1] == "ANULADO" for k in antes if despues[k][0]))
def gen(numero): return D(q("select flags_estado from remitos where numero_legal=?", numero)[0][0])
g30 = gen("0015-00003030")
check(f"3030 Coalix (no comercial, mostrador entregado): EGRESO_AVIOS / EMITIDO / RECIBIDO {g30}", (g30["clase"], g30["estado"], g30["logistica"]) == ("EGRESO_AVIOS", "EMITIDO", "RECIBIDO"))
g19 = gen("0015-00003019")
check(f"3019 Rizobacter (impreso el 23/09, despachado el 25/09): EGRESO / RETIRADO + SALIDA_DIFERIDA {g19}", g19["logistica"] == "RETIRADO" and "SALIDA_DIFERIDA" in g19["marcas"])
anul = q("select numero_legal, flags_estado from remitos where estado='ANULADO'")
check(f"los {len(anul)} anulados: ANULADO + FUE_ANULADO", anul and all(D(fl)["estado"] == "ANULADO" and "FUE_ANULADO" in D(fl)["marcas"] for _, fl in anul))
r = subprocess.run([PY, "-X", "utf8", M066], capture_output=True, text=True, encoding="utf-8", env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
check("migrate_066 otra vez: SKIP", r.returncode == 0 and "SKIP" in r.stdout)

# ---- (3) el servidor sobre la copia migrada
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
SALIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(_router.__file__)))), "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida")
previos = set(os.listdir(SALIDA)) if os.path.isdir(SALIDA) else set()
def guid(h): h = h.replace("-", ""); return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"
pend = q("""select pi.pedido_id, pi.id, pi.cantidad - coalesce((select sum(ri.cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id
            where ri.pedido_item_id=pi.id and r.estado<>'ANULADO'), 0) from pedidos_items pi join pedidos p on p.id=pi.pedido_id where p.estado='PENDIENTE' order by pi.pedido_id desc""")
pend = [(p, i, x) for p, i, x in pend if x and x > 0]
(p1, i1, x1) = pend[0]; (p2, i2, x2) = next(t for t in pend if t[0] != p1)
r = cli.post("/remitos/armar", json={"pedido_id": p2, "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": i2, "cantidad": x2}]})
j = r.json() if r.status_code == 200 else {}
check(f"armar sin número: indeterminado (clase por el pedido, sin estado ni logística) y sin fecha de emisión [{r.status_code}] {D(j.get('flags_estado'))}",
      r.status_code == 200 and j.get("numero_legal") is None and D(j.get("flags_estado"))["estado"] is None and j.get("fecha_emision") is None)
rid = j.get("id", "")
rp = cli.get(f"/remitos/{rid}/pdf")
fila = q("select numero_legal, fecha_emision, fecha_salida, flags_estado from remitos where id=?", rid.replace("-", ""))[0]
hoy = datetime.now().strftime("%Y-%m-%d")
check(f"al tomar número (PDF) se fija la emisión hoy y la salida asumida en la emisión [{rp.status_code}] -> {fila[0]}, {fila[1]}, {fila[2]}",
      rp.status_code == 200 and fila[0] and fila[1] and fila[1].startswith(hoy) and fila[2] == fila[1])
g = D(fila[3])
check(f"y el genoma queda EGRESO / EMITIDO / RETIRADO + IMPRESO {g}", (g["estado"], g["logistica"]) == ("EMITIDO", "RETIRADO") and "IMPRESO" in g["marcas"])
r = cli.post("/remitos/armar", json={"pedido_id": p1, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": i1, "cantidad": x1}]})
jm = r.json() if r.status_code == 200 else {}
gm = D(jm.get("flags_estado"))
check(f"mostrador (nace entregado, sin número): todavía sin estado; al imprimir, EMITIDO / RECIBIDO [{r.status_code}] {gm}", r.status_code == 200 and gm["estado"] is None)
cli.get(f"/remitos/{jm.get('id')}/pdf")
gm = D(q("select flags_estado from remitos where id=?", jm.get("id", "").replace("-", ""))[0][0])
check(f"   -> {gm}", (gm["estado"], gm["logistica"]) == ("EMITIDO", "RECIBIDO") and "IMPRESO" in gm["marcas"])
# EN_DEPOSITO y salida diferida: un remito emitido ayer que quedó en el depósito y lo retiran hoy
ayer = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d 10:00:00")
q("update remitos set flags_estado = flags_estado | ?, fecha_emision=?, fecha_salida=NULL, aprobado_para_despacho=1 where id=?", int(F.EN_DEPOSITO), ayer, rid.replace("-", ""))
r = cli.post(f"/remitos/{rid}/despachar", json={})
fila = q("select fecha_salida, flags_estado from remitos where id=?", rid.replace("-", ""))[0]
g = D(fila[1])
check(f"emitido ayer, en depósito, retirado hoy (despachar): RETIRADO + SALIDA_DIFERIDA, salida hoy [{r.status_code}] {g}",
      r.status_code == 200 and fila[0].startswith(hoy) and g["logistica"] == "RETIRADO" and "SALIDA_DIFERIDA" in g["marcas"])
# recibido distinto -> DIFERENCIA_RECEPCION. [S894] PATCH /items/{id}/recibido se retiró: «llegó» lo baja una corrección con causa
ri = q("select id, cantidad_remitida from remitos_items where remito_id=?", rid.replace("-", ""))[0]
r = cli.post(f"/remitos/{rid}/correccion", json={"remito_item_id": ri[0], "cantidad_real": max(ri[1] - 1, 0), "causa": "SE_RECHAZO"})
g = D(q("select flags_estado from remitos where id=?", rid.replace("-", ""))[0][0])
check(f"recibido distinto de lo remitido (corrección «se rechazó»): DIFERENCIA_RECEPCION (irreversible) [{r.status_code}] {g}", r.status_code == 200 and "DIFERENCIA_RECEPCION" in g["marcas"])
# cambio de fecha de emisión: mueve la emisión; la salida registrada aparte (hoy) no se toca
r = cli.patch(f"/remitos/{rid}/fecha", json={"fecha": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"), "motivo": "prueba"})
fila = q("select fecha_emision, fecha_salida from remitos where id=?", rid.replace("-", ""))[0]
check(f"cambiar la fecha del remito mueve la EMISIÓN y no la salida registrada aparte [{r.status_code}] -> {fila}",
      r.status_code == 200 and fila[0].startswith((datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")) and fila[1].startswith(hoy))
# respuesta de la API
j = cli.get(f"/remitos/{rid}").json()
check("la API devuelve fecha_emision y flags_estado", "fecha_emision" in j and "flags_estado" in j and j["flags_estado"])

# ---- limpieza
del cli; eng.dispose()
for n in (set(os.listdir(SALIDA)) - previos) if os.path.isdir(SALIDA) else []:
    os.remove(os.path.join(SALIDA, n))
shutil.rmtree(TMP, ignore_errors=True)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
