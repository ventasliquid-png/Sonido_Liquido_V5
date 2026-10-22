r"""S890, Carlos (21/10): «No debemos tener un montón de fechas... la fecha del remito como confección es el día que deja de ser un desnumerado y adquiere
rango de remito». Antes el PDF ponía la fecha del día en que se generaba: cada reimpresión cambiaba la fecha del papel.
(1) Al tomar número, el remito fija su fecha (fecha_salida, sin columnas nuevas; un mostrador ya la trae) y el PDF la imprime; reimprimir no la cambia.
(2) Un remito viejo numerado sin fecha de salida imprime la de creación. (3) «Despachar» no pisa una fecha de salida que ya existe.
(4) La fecha se puede cambiar (pedido de Carlos del 20/10: «por si el papel se perdió o hay que ajustar algo sin perder el remito original»): solo con número,
no anulado, con motivo, nunca a futuro, y queda una nota [SISTEMA]. (5) Pantalla (estática): el listado muestra esa fecha y tiene el lápiz para cambiarla.
Sobre una COPIA de la base de P (la más nueva de BACKUPS_DB/PRODUCCION_P)."""
import sys, os, shutil, sqlite3, glob, io, re
from datetime import datetime, timedelta
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import fitz

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
HOY = datetime.now().strftime("%d/%m/%Y")

ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_*.db"))[-1]
T = os.path.join(RAIZ, "scratch", "test_fecha_remito_tmp.db"); copiar_p(ORIG, T)
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
RESPALDO = os.path.join(RAIZ, "scratch", "test_fecha_respaldo"); os.makedirs(RESPALDO, exist_ok=True)
tocados = set()
def q(sql, *a):
    con = sqlite3.connect(T); r = con.execute(sql, a).fetchall(); con.commit(); con.close(); return r
def rid(numero): return q("select id from remitos where numero_legal=?", numero)[0][0]
def guid(h): h = h.replace("-", ""); return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:]}"
def pdf(remito_id):
    """GET /remitos/{id}/pdf; respalda el archivo que el endpoint pisa. Devuelve (status, texto de la primera copia en una línea)."""
    r = cli.get(f"/remitos/{guid(remito_id)}/pdf")
    num = q("select numero_legal from remitos where id=?", remito_id)[0][0]
    nombre = f"remito_{(num or '').replace('-', '_')}.pdf"
    if r.status_code != 200: return r.status_code, ""
    out = os.path.join(RESPALDO, "_" + nombre); open(out, "wb").write(r.content)
    return 200, " ".join(fitz.open(out)[0].get_text().split())
for numero in ("0015-00003031", "0015-00003027", "0015-00003029"):
    n = f"remito_{numero.replace('-', '_')}.pdf"; tocados.add(n)
    if os.path.exists(os.path.join(SALIDA, n)): shutil.copyfile(os.path.join(SALIDA, n), os.path.join(RESPALDO, n))
def fecha_salida(remito_id): return q("select fecha_salida from remitos where id=?", remito_id)[0][0]

# ---- (1) tomar número fija la fecha; el PDF la imprime; reimprimir no la cambia
r29 = rid("0015-00003029")
q("update remitos set numero_legal=NULL, fecha_salida=NULL where id=?", r29)        # en la copia: vuelve a ser un remito sin número
ultimo = max(int(n.split("-")[-1]) for (n,) in q("select numero_legal from remitos where numero_legal like '0015-%'"))
proximo = f"remito_0015_{ultimo + 1:08d}.pdf"                                         # el archivo que el endpoint va a escribir: se respalda ANTES
tocados.add(proximo)
if os.path.exists(os.path.join(SALIDA, proximo)): shutil.copyfile(os.path.join(SALIDA, proximo), os.path.join(RESPALDO, proximo))
st, txt = pdf(r29)
num29 = q("select numero_legal from remitos where id=?", r29)[0][0]
tocados.add(f"remito_{(num29 or '').replace('-', '_')}.pdf")
fs = fecha_salida(r29)
check(f"al tomar número ({num29}) el remito fija su fecha: fecha_salida = hoy ({fs}) [{st}]", st == 200 and num29 and fs and fs[:10] == datetime.now().strftime("%Y-%m-%d"))
check(f"el PDF imprime esa fecha ({HOY})", HOY in txt)
# [S891] la fecha del papel es la de EMISIÓN (fecha_emision); la de salida es la física
q("update remitos set fecha_emision='2026-10-18 10:00:00', fecha_salida='2026-10-18 10:00:00' where id=?", r29)
st, txt = pdf(r29)
check(f"reimprimir otro día NO cambia la fecha del papel: imprime la del remito (18/10/2026), no la de hoy [{st}]", st == 200 and "18/10/2026" in txt and (HOY == "18/10/2026" or HOY not in txt))
check("reimprimir no lo renumera", q("select numero_legal from remitos where id=?", r29)[0][0] == num29)

r31 = rid("0015-00003031")
st, txt = pdf(r31)
check(f"3031 (mostrador, salió el 20/10): el papel dice 20/10/2026 aunque se reimprima hoy [{st}]", st == 200 and "20/10/2026" in txt)

# ---- (2) remito viejo numerado sin fecha de salida: imprime la de creación
r27 = rid("0015-00003027")
fc27 = q("select fecha_creacion, fecha_salida from remitos where id=?", r27)[0]
st, txt = pdf(r27)
esperada = datetime.strptime(fc27[0][:10], "%Y-%m-%d").strftime("%d/%m/%Y")
check(f"0015-00003027 (borrador viejo con número, sin fecha de salida): imprime la de creación ({esperada}) [{st}]", fc27[1] is None and st == 200 and esperada in txt)
check("y reimprimir un remito que ya tiene número NO le fija fecha de salida (solo se fija al tomar número)", fecha_salida(r27) is None)

# ---- (3) despachar no pisa la fecha de salida
q("update remitos set aprobado_para_despacho=1, estado='BORRADOR' where id=?", r29)
r = cli.post(f"/remitos/{guid(r29)}/despachar", json={})
check(f"despachar un remito con fecha (18/10) lo pasa a EN_CAMINO sin pisar la fecha [{r.status_code}] -> {fecha_salida(r29)}", r.status_code == 200 and r.json()["estado"] == "EN_CAMINO" and fecha_salida(r29).startswith("2026-10-18"))

# ---- (4) cambiar la fecha
def cambiar(remito_id, fecha, motivo="El papel se perdió y se rehízo"):
    return cli.patch(f"/remitos/{guid(remito_id)}/fecha", json={"fecha": fecha, "motivo": motivo})
notas_antes = q("select count(*) from remitos_notas where remito_id=?", r31)[0][0]
r = cambiar(r31, "2026-10-19")
fs = fecha_salida(r31)
check(f"cambiar la fecha del 3031 al 19/10 [{r.status_code}] -> fecha_salida {fs} (conserva la hora)", r.status_code == 200 and fs.startswith("2026-10-19 14:28"))
nota = q("select texto, autor_id from remitos_notas where remito_id=? order by id desc limit 1", r31)[0]
check(f"queda una nota [SISTEMA] con la fecha anterior, la nueva, el motivo y el autor: {nota[0]!r}", q("select count(*) from remitos_notas where remito_id=?", r31)[0][0] == notas_antes + 1
      and nota[0].startswith("[SISTEMA] Fecha del remito cambiada del 20/10/2026 al 19/10/2026. Motivo: El papel se perdió") and nota[1] == 1)
st, txt = pdf(r31)
check(f"el PDF imprime la fecha nueva (19/10/2026) [{st}]", st == 200 and "19/10/2026" in txt)
check("el número y el estado no cambian", q("select numero_legal, estado from remitos where id=?", r31)[0] == ("0015-00003031", "ENTREGADO"))
r = cambiar(r31, "2026-10-19", motivo="   ")
check(f"sin motivo: 422 MOTIVO_OBLIGATORIO [{r.status_code}]", r.status_code == 422 and "MOTIVO_OBLIGATORIO" in r.text)
r = cambiar(r31, (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
check(f"a futuro: 422 FECHA_FUTURA [{r.status_code}]", r.status_code == 422 and "FECHA_FUTURA" in r.text)
r = cambiar(r31, "19/10/2026")
check(f"formato equivocado: 422 FECHA_INVALIDA [{r.status_code}]", r.status_code == 422 and "FECHA_INVALIDA" in r.text)
q("update remitos set numero_legal=NULL where id=?", r27)
r = cambiar(r27, "2026-10-15")
check(f"remito sin número: 409 REMITO_SIN_NUMERO (su fecha es la del día en que tome número) [{r.status_code}]", r.status_code == 409 and "REMITO_SIN_NUMERO" in r.text)
q("update remitos set numero_legal='0015-00003027', estado='ANULADO' where id=?", r27)
r = cambiar(r27, "2026-10-15")
check(f"remito anulado: 409 REMITO_ANULADO [{r.status_code}]", r.status_code == 409 and "REMITO_ANULADO" in r.text)
r = cli.patch("/remitos/00000000-0000-0000-0000-000000000000/fecha", json={"fecha": "2026-10-15", "motivo": "x"})
check(f"remito inexistente: 404 [{r.status_code}]", r.status_code == 404)

# ---- (5) pantalla (estática)
v = io.open(os.path.join(RAIZ, "frontend", "src", "views", "Logistica", "RemitoListView.vue"), encoding="utf-8").read()
check("listado: la columna Fecha muestra la fecha del remito (con número, la de emisión; sin número, la de armado) y ordena por ella",
      "remito.numero_legal ? (remito.fecha_emision || remito.fecha_salida || remito.fecha_creacion) : remito.fecha_creacion" in v
      and "formatDate(fechaRemito(remito))" in v and "new Date(fechaRemito(a))" in v)
check("listado: lápiz «Cambiar la fecha» solo en remitos numerados no anulados, ventana con fecha (sin futuro) y motivo obligatorio, PATCH /remitos/{id}/fecha",
      "v-if=\"remito.numero_legal && remito.estado !== 'ANULADO'\" @click.stop=\"abrirCambioFecha(remito)\"" in v and ':max="hoyISO()"' in v
      and "!cambioFecha.motivo.trim()" in v and "api.patch(`/remitos/${cambioFecha.remito.id}/fecha`" in v)

# ---- limpieza
del cli; eng.dispose()
for nombre in tocados:
    gen = os.path.join(SALIDA, nombre)
    if os.path.exists(os.path.join(RESPALDO, nombre)): shutil.copyfile(os.path.join(RESPALDO, nombre), gen)
    elif os.path.exists(gen): os.remove(gen)
shutil.rmtree(RESPALDO, ignore_errors=True)
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
