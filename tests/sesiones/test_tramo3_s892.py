r"""S892, paquete 2 de remitos, tramo 3a (reglas de Carlos y Nike del 22/10):
(1) «Salió sin papel»: el remito sin número toma el 0015 sin imprimirse (EMITIDO sin IMPRESO, salida asumida en la emisión, nota
    [SISTEMA]); si después lo piden, se imprime con ese número y ese primer papel queda como imagen. La fecha es la de la asignación del
    número (Carlos, 23/10): ahora, aunque se mande otra. Un pedido Rosa SÍ puede salir con un 0015 (si lo despacha un transporte hace
    falta un remito) y queda dicho en una nota que no se factura, con pedidos Rosa reales de P: sin papel y por la impresión de siempre.
(2) «Queda en depósito» (bit 37, caso Rizobacter): se borra la salida asumida; «Retiró el transporte» la registra (nunca antes de la
    emisión) y, si es otro día, queda SALIDA_DIFERIDA. Cambiar la fecha de un remito en depósito no le inventa una salida.
(3) Pantalla (estática). Sobre una COPIA de P con migrate_066 aplicada."""
import sys, os, shutil, sqlite3, glob, subprocess, io
from datetime import datetime, timedelta
from _esquema_p import asegurar_esquema, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.remitos.genoma import describir

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_*.db"))[-1]
TMP = os.path.join(RAIZ, "scratch", "test_tramo3_s892"); os.makedirs(TMP, exist_ok=True)
T = os.path.join(TMP, "P.db"); shutil.copyfile(ORIG, T)
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
r = subprocess.run([PY, "-X", "utf8", os.path.join(RAIZ, "scripts", "migrate_066_remitos_genoma_fecha_emision.py")], capture_output=True, text=True,
                   encoding="utf-8", env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
asegurar_esquema(T)
check(f"setup: copia de P con migrate_066 [rc {r.returncode}]", r.returncode == 0)

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
SALIDA = os.path.join(BASE, "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida"); IMAGENES = os.path.join(BASE, "DOCUMENTOS_GENERADOS_RAR", "Remitos emitidos")
previos = set(os.listdir(SALIDA)) if os.path.isdir(SALIDA) else set()
def q(sql, *a):
    con = sqlite3.connect(T); x = con.execute(sql, a).fetchall(); con.commit(); con.close(); return x
def h(x): return x.replace("-", "")
def fila(rid): return q("select numero_legal, fecha_emision, fecha_salida, flags_estado, estado from remitos where id=?", h(rid))[0]
def gen(rid): return describir(fila(rid)[3])
def notas(rid): return [n for (n,) in q("select texto from remitos_notas where remito_id=? order by id", h(rid))]
def dia(s): return (s or "")[:10]
HOY = datetime.now().strftime("%Y-%m-%d")
NOTA_ROSA = "[SISTEMA] Remito de un pedido Rosa: no se factura."

def pendientes(rosa):
    return q(f"""select p.id, pi.id, pi.cantidad - coalesce((select sum(ri.cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id
                 where ri.pedido_item_id=pi.id and r.estado<>'ANULADO'), 0) as falta
                 from pedidos p join pedidos_items pi on pi.pedido_id=p.id where p.estado='PENDIENTE' and ((p.flags_estado>>12)&1)={1 if rosa else 0}
                 and (p.flags_estado>>11)&1=0 order by p.id desc""")
def armar(pedido, item, cant):
    r = cli.post("/remitos/armar", json={"pedido_id": pedido, "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": item, "cantidad": cant}]})
    return r.json()["id"] if r.status_code == 200 else ""
blancos = [x for x in pendientes(False) if x[2] and x[2] > 0]
rosas = [x for x in pendientes(True) if x[2] and x[2] > 0]
ultimo = max(int(n.split("-")[1]) for (n,) in q("select numero_legal from remitos where numero_legal like '0015-%'"))

# ---- (1) salió sin papel
ra = armar(*blancos[0])
r = cli.post(f"/remitos/{ra}/salida-sin-papel", json={"motivo": "salió con la factura"})
num, fe, fs, fl, est = fila(ra)
g = gen(ra)
check(f"Blanco sin papel [{r.status_code}]: toma el próximo 0015 ({num}), EMITIDO y RETIRADO, SIN la marca IMPRESO, emisión y salida hoy",
      r.status_code == 200 and num == f"0015-{ultimo + 1:08d}" and g["estado"] == "EMITIDO" and g["logistica"] == "RETIRADO"
      and "IMPRESO" not in g["marcas"] and dia(fe) == HOY and dia(fs) == HOY)
check("deja nota [SISTEMA] con el número y el motivo", any(n.startswith(f"[SISTEMA] Salió sin papel el ") and num in n and "Motivo: salió con la factura" in n for n in notas(ra)))
check("no genera ningún PDF (ni de salida ni imagen)", (set(os.listdir(SALIDA)) if os.path.isdir(SALIDA) else set()) == previos
      and not (os.path.isdir(IMAGENES) and os.listdir(IMAGENES)))
r = cli.post(f"/remitos/{ra}/salida-sin-papel", json={})
check(f"otra vez: 409 REMITO_CON_NUMERO [{r.status_code}]", r.status_code == 409 and "REMITO_CON_NUMERO" in r.text)
rp = cli.get(f"/remitos/{ra}/pdf")
check(f"si después lo piden, se imprime con el MISMO número y ese primer papel queda como imagen, sin nota de «no había imagen» [{rp.status_code}]",
      rp.status_code == 200 and fila(ra)[0] == num and "IMPRESO" in gen(ra)["marcas"]
      and os.path.exists(os.path.join(IMAGENES, f"remito_{num.replace('-', '_')}.pdf")) and not any("no había imagen" in n for n in notas(ra)))

rb = armar(*blancos[1])
hace3 = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
r = cli.post(f"/remitos/{rb}/salida-sin-papel", json={"fecha": hace3})
check(f"la fecha del remito es la de la asignación del número: aunque se mande «hace 3 días», emisión y salida son hoy [{r.status_code}]",
      r.status_code == 200 and dia(fila(rb)[1]) == HOY and dia(fila(rb)[2]) == HOY)
check("un pedido Blanco no recibe la aclaración de Rosa", not any(n == NOTA_ROSA for n in notas(ra)) and not any(n == NOTA_ROSA for n in notas(rb)))

# Rosa: SÍ puede tener un 0015 (Carlos, 23/10); queda dicho que no se factura
rr = armar(*rosas[0])
r = cli.post(f"/remitos/{rr}/salida-sin-papel", json={})
numero_rosa = fila(rr)[0]
check(f"pedido Rosa real #{rosas[0][0]} sin papel [{r.status_code}]: toma un 0015 ({numero_rosa}), EMITIDO, sin IMPRESO",
      r.status_code == 200 and (numero_rosa or "").startswith("0015-") and gen(rr)["estado"] == "EMITIDO" and "IMPRESO" not in gen(rr)["marcas"])
check("y queda aclarado en el remito que no se factura (una sola nota)", notas(rr).count(NOTA_ROSA) == 1)
check("sus renglones siguen como «no aplica» para la factura (cantidad_facturada NULL): el conciliador no los ofrece",
      q("select count(*) from remitos_items where replace(remito_id,'-','')=? and cantidad_facturada is not null", h(rr))[0][0] == 0)
otro = next(x for x in rosas if x[0] != rosas[0][0])
rr2 = armar(*otro)
rp = cli.get(f"/remitos/{rr2}/pdf")
check(f"pedido Rosa #{otro[0]} por la impresión de siempre [{rp.status_code}]: toma el 0015, queda IMPRESO y la misma aclaración",
      rp.status_code == 200 and (fila(rr2)[0] or "").startswith("0015-") and "IMPRESO" in gen(rr2)["marcas"] and notas(rr2).count(NOTA_ROSA) == 1)
cli.get(f"/remitos/{rr2}/pdf")
check("reimprimirlo no repite la aclaración", notas(rr2).count(NOTA_ROSA) == 1)

# ---- (2) queda en depósito / retiró el transporte
# [S894, CA H16 (a)] «Salió sin papel» confirma la salida (bit 47): ese remito ya no puede quedar en depósito. El caso Rizobacter es el
# remito IMPRESO que espera al transporte (salida asumida, sin el 47): el resto de esta parte usa uno impreso.
r = cli.post(f"/remitos/{rb}/en-deposito")
check(f"«salió sin papel» (salida confirmada) y después «queda en depósito»: 409 SALIDA_CONFIRMADA [{r.status_code}]", r.status_code == 409 and "SALIDA_CONFIRMADA" in r.text)
rb = armar(*blancos[3]); cli.get(f"/remitos/{rb}/pdf")
r = cli.post(f"/remitos/{rb}/en-deposito")
num_b, fe_b, fs_b, _, _ = fila(rb)
check(f"queda en depósito [{r.status_code}]: logística EN_DEPOSITO, se borra la salida asumida, nota [SISTEMA]",
      r.status_code == 200 and gen(rb)["logistica"] == "EN_DEPOSITO" and fs_b is None
      and any(n.startswith("[SISTEMA] Queda en depósito") and "se borró la salida asumida" in n for n in notas(rb)))
r = cli.post(f"/remitos/{rb}/en-deposito")
check(f"otra vez: 409 YA_EN_DEPOSITO [{r.status_code}]", r.status_code == 409 and "YA_EN_DEPOSITO" in r.text)
r = cli.patch(f"/remitos/{rb}/fecha", json={"fecha": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"), "motivo": "ajuste"})
check(f"cambiar la fecha de un remito en depósito no le inventa una salida (sigue EN_DEPOSITO) [{r.status_code}]",
      r.status_code == 200 and fila(rb)[2] is None and gen(rb)["logistica"] == "EN_DEPOSITO")
r = cli.post(f"/remitos/{rb}/retiro", json={"fecha": hace3})
check(f"retiro antes de la emisión: 422 SALIDA_ANTES_DE_EMISION [{r.status_code}]", r.status_code == 422 and "SALIDA_ANTES_DE_EMISION" in r.text)
r = cli.post(f"/remitos/{rb}/retiro", json={})
g = gen(rb)
check(f"retiró el transporte hoy [{r.status_code}]: RETIRADO, salida hoy, SALIDA_DIFERIDA (emitido hace 2 días), nota",
      r.status_code == 200 and g["logistica"] == "RETIRADO" and dia(fila(rb)[2]) == HOY and "SALIDA_DIFERIDA" in g["marcas"]
      and any(n.startswith("[SISTEMA] Retiró el transporte el ") for n in notas(rb)))
check("se lo llevó el transporte: pasa a EN CAMINO (lo dice la nota)", fila(rb)[4] == "EN_CAMINO" and any("Pasa a EN CAMINO" in n for n in notas(rb)))
r = cli.post(f"/remitos/{rb}/en-deposito")
check(f"ya retirado, no se puede volver a marcar en depósito: 409 REMITO_EN_CAMINO (el banco lo mostró: la fila volvía a ofrecerlo) [{r.status_code}]",
      r.status_code == 409 and "REMITO_EN_CAMINO" in r.text)
r = cli.post(f"/remitos/{rb}/retiro", json={})
check(f"retiro de un remito que no está en depósito: 409 [{r.status_code}]", r.status_code == 409 and "REMITO_NO_EN_DEPOSITO" in r.text)
rc = armar(*blancos[2])
r = cli.post(f"/remitos/{rc}/en-deposito")
check(f"en depósito sin número: 409 REMITO_SIN_NUMERO [{r.status_code}]", r.status_code == 409 and "REMITO_SIN_NUMERO" in r.text)
r30 = q("select id from remitos where numero_legal='0015-00003030'")[0][0]
r = cli.post(f"/remitos/{r30[:8]}-{r30[8:12]}-{r30[12:16]}-{r30[16:20]}-{r30[20:]}/en-deposito")
check(f"un remito ya recibido (3030, ENTREGADO) no queda en depósito: 409 [{r.status_code}]", r.status_code == 409 and "REMITO_ENTREGADO" in r.text)

# ---- (3) pantalla (estática)
lista = io.open(os.path.join(RAIZ, "frontend", "src", "views", "Logistica", "RemitoListView.vue"), encoding="utf-8").read()
check("listado: «Salió sin papel» solo sin número, «Queda en depósito» con número en BORRADOR, «Retiró el transporte» con el bit 37, marca «en depósito»",
      'data-accion="sin-papel"' in lista and 'data-accion="en-deposito"' in lista and 'data-accion="retiro"' in lista and 'data-marca="en-deposito"' in lista
      and "tieneBit(remito.flags_estado, 37)" in lista and "/remitos/${remito.id}/en-deposito" in lista and "'salida-sin-papel' : 'retiro'" in lista)
check("«Salió sin papel» no pide fecha (es la de la asignación del número); solo «Retiró el transporte» la pide",
      """<template v-if="accionFecha.modo === 'retiro'">""" in lista and "{ fecha: accionFecha.fecha } : { motivo:" in lista)
check("la ventana de fecha arranca hoy y no deja elegir días futuros", 'data-modal="accion-fecha"' in lista and ':max="hoyISO()"' in lista and "fecha: hoyISO()" in lista)

# ---- limpieza
del cli; eng.dispose()
for n in (set(os.listdir(SALIDA)) - previos) if os.path.isdir(SALIDA) else []:
    os.remove(os.path.join(SALIDA, n))
_aparte.__exit__(None, None, None)
shutil.rmtree(TMP, ignore_errors=True)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
