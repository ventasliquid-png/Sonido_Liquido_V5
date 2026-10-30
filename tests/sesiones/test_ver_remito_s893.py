r"""S893, Carlos 26/10: «Imprimir HTML es una forma de ver el remito en pantalla tal como saldrá el físico: mantenerlo es una forma visual de leer el remito sin tener que imprimirlo».
El HTML (RemitoTemplate.vue) era un dibujo aparte que no seguía las reglas del papel (un retiro por mostrador salía con «Roseti 1482» bajo el cliente) y su impresión no tomaba número ni quedaba
registrada. Se lo reemplaza por «Ver el remito»: GET /remitos/{id}/pdf?ver=1 muestra el documento VERDADERO sin imprimir: NO toma número, NO marca IMPRESO (bit 44), NO guarda imagen y NO deja la nota
de reimpresión. Un remito impreso muestra su imagen guardada; uno sin papel (con o sin número) se dibuja con la marca «VISTA PREVIA - SIN VALIDEZ» (y su número, si ya lo tiene). Una corrección no se ve
(no tiene papel). Sobre una COPIA de P con migrate_066, 068 y 069."""
import sys, os, shutil, sqlite3, glob, subprocess
from _esquema_p import asegurar_esquema, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
import fitz

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_*.db"))[-1]
TMP = os.path.join(RAIZ, "scratch", "test_ver_remito_s893"); os.makedirs(TMP, exist_ok=True)
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
CARPETA = os.path.join(BASE, "DOCUMENTOS_GENERADOS_RAR", "Remitos emitidos")
def hx(x): return str(x).replace("-", "")
def estado(rid): return q("select numero_legal, estado, flags_estado from remitos where id=?", hx(rid))[0]
def notas(rid): return q("select count(*) from remitos_notas where remito_id=?", hx(rid))[0][0]
def imagenes(): return sorted(os.listdir(CARPETA)) if os.path.isdir(CARPETA) else []
def texto(resp):
    d = fitz.open(stream=resp.content, filetype="pdf"); t = " ".join(p.get_text() for p in d); d.close(); return t
IMPRESO = 1 << 44

# ---- A) un remito SIN número: ver = la vista previa de siempre
ped = cli.get("/remitos/pedidos-por-remitar").json()["pedidos"][0]
pi = q("select id, cantidad from pedidos_items where pedido_id=? order by id limit 1", ped["pedido_id"])[0]
rA = cli.post("/remitos/armar", json={"pedido_id": ped["pedido_id"], "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": pi[0], "cantidad": 1}]}).json()["id"]
antesA = (estado(rA), notas(rA), imagenes())
r = cli.get(f"/remitos/{rA}/pdf", params={"ver": 1})
check(f"ver un remito sin número [{r.status_code}]: es un PDF con la marca «VISTA PREVIA - SIN VALIDEZ»", r.status_code == 200 and r.content[:4] == b"%PDF" and "VISTA PREVIA" in texto(r))
check("y no pasó nada: sigue sin número, sin IMPRESO, sin notas nuevas y sin imágenes guardadas", (estado(rA), notas(rA), imagenes()) == antesA and estado(rA)[0] is None and not estado(rA)[2] & IMPRESO)

# ---- B) un remito CON número pero sin papel (salió sin papel): ver = vista con su número, sin marcarlo impreso
r = cli.post(f"/remitos/{rA}/salida-sin-papel", json={})
num = estado(rA)[0]
check(f"«salió sin papel» le da número sin imprimirlo [{r.status_code}]: {num}, sin IMPRESO", r.status_code == 200 and num and not estado(rA)[2] & IMPRESO)
antesB = (estado(rA), notas(rA), imagenes())
r = cli.get(f"/remitos/{rA}/pdf", params={"ver": 1})
t = texto(r)
check(f"ver un remito con número sin papel [{r.status_code}]: muestra la marca «VISTA PREVIA» y SU NÚMERO ({num})", r.status_code == 200 and "VISTA PREVIA" in t and num.split("-")[1].lstrip("0") in t.replace(" ", "").replace("-", ""))
check("y NO lo marcó impreso, no guardó imagen ni dejó nota", (estado(rA), notas(rA), imagenes()) == antesB and not estado(rA)[2] & IMPRESO)

# ---- C) impreso de verdad: ver = la imagen guardada, sin la nota de reimpresión
r = cli.get(f"/remitos/{rA}/pdf")
check(f"imprimir de verdad [{r.status_code}]: queda IMPRESO y la imagen guardada ({imagenes()})", r.status_code == 200 and estado(rA)[2] & IMPRESO and len(imagenes()) == 1)
img = os.path.join(CARPETA, imagenes()[0]); bytes_img = open(img, "rb").read()
n0 = notas(rA)
r = cli.get(f"/remitos/{rA}/pdf", params={"ver": 1})
check(f"ver un remito impreso [{r.status_code}]: entrega EXACTAMENTE la imagen guardada, sin la marca de vista previa", r.status_code == 200 and r.content == bytes_img and "VISTA PREVIA" not in texto(r))
check("y no dejó ninguna nota de reimpresión", notas(rA) == n0)
r = cli.get(f"/remitos/{rA}/pdf")
check("(control) reimprimir de verdad SÍ deja su nota [SISTEMA] «Reimpresión»", r.status_code == 200 and notas(rA) == n0 + 1 and "Reimpresión" in q("select texto from remitos_notas where remito_id=? order by id desc limit 1", hx(rA))[0][0])
check("ver sigue sin dejar nota después de reimprimir", cli.get(f"/remitos/{rA}/pdf", params={"ver": 1}).status_code == 200 and notas(rA) == n0 + 1)

# ---- D) una corrección no se ve (no tiene papel), un remito inexistente da 404 y uno anulado se puede ver
it = q("select id from remitos_items where remito_id=?", hx(rA))[0][0]
rc = cli.post(f"/remitos/{rA}/correccion", json={"remito_item_id": it, "cantidad_real": 0, "causa": "NO_SALIO"})
corr = q("select remito_id from remitos_items where corrige_item_id=?", it)
r = cli.get(f"/remitos/{corr[0][0]}/pdf", params={"ver": 1}) if corr else None
check(f"ver una corrección: 409 CORRECCION_NO_SE_IMPRIME (corrección {rc.status_code})", r is not None and r.status_code == 409 and "CORRECCION_NO_SE_IMPRIME" in r.text)
check("un remito que no existe: 404", cli.get("/remitos/00000000000000000000000000000000/pdf", params={"ver": 1}).status_code == 404)
anul = q("select id, flags_estado from remitos where estado='ANULADO' and numero_legal is not null limit 1")[0]
r = cli.get(f"/remitos/{anul[0]}/pdf", params={"ver": 1})
check(f"un remito anulado también se puede ver [{r.status_code}] y no cambia", r.status_code == 200 and q("select estado, flags_estado from remitos where id=?", anul[0])[0] == ("ANULADO", anul[1]))

# ---- E) código: el HTML se retiró
def leer(p): return open(p, encoding="utf-8").read().replace("\r\n", "\n")
spl, fic = leer("frontend/src/views/Logistica/LogisticaSplitter.vue"), leer("frontend/src/views/Logistica/RemitoFicha.vue")
check("el dibujo HTML (RemitoTemplate.vue) ya no existe ni se usa, y «Ver el remito» pide /pdf?ver=1 en «Entregas y remitos» y en la ficha",
      not os.path.exists("frontend/src/views/Logistica/components/RemitoTemplate.vue") and "RemitoTemplate" not in spl and "printRemitoData" not in spl
      and "?ver=1" in spl and 'data-accion="ver-remito"' in spl and "?ver=1" in fic and 'data-accion="ver-remito"' in fic)

_aparte.__exit__(None, None, None)
ok = sum(1 for _, c in checks if c)
print(f"\nRESULTADO: {ok}/{len(checks)} checks OK")
if ok != len(checks):
    print("FALLO:", *[d for d, c in checks if not c], sep="\n  ")
    sys.exit(1)
