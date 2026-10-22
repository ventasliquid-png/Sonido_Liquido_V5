r"""S890, regla de Carlos (20/10): el remito impreso muestra la dirección del CLIENTE, aunque retire él o mande a alguien a buscar:
1° la de entrega, 2° la fiscal, y la oficina (Roseti 1482) SOLO si el cliente no tiene ninguna (consumidor final, casi seguro Rosa).
Casos reales: el 0015-00003030 (Coalix, mostrador) y el 0015-00003031 (Petroplastic, mostrador) salieron con «Roseti 1482» debajo del nombre del cliente,
porque el PDF imprimía el domicilio de entrega del remito y en mostrador ese domicilio es la oficina. Petroplastic tiene en un mismo domicilio la dirección
fiscal (Pellegrini 989) y la de entrega (Ruta 234 Km 16, Junín de los Andes): se imprime la de entrega.
Sobre una COPIA de la base de P (la más nueva de BACKUPS_DB/PRODUCCION_P). El domicilio GUARDADO en el remito no cambia."""
import sys, os, shutil, sqlite3, glob
from uuid import UUID
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from backend.remitos.service import RemitosService
from backend.remitos import models as rmodels
from backend.clientes.models import Domicilio
from backend.clientes.constants import DOMICILIO_ROSETI_ID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import fitz

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
OFICINA = UUID(DOMICILIO_ROSETI_ID).hex

ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_*.db"))[-1]
T = os.path.join(RAIZ, "scratch", "test_direccion_remito_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)

# el endpoint escribe el PDF en DOCUMENTOS_GENERADOS_RAR/Remitos de salida del repo: se respalda lo que hubiera con el mismo nombre y se restaura al final
import backend.remitos.router as _router   # la carpeta sale del código que corre (D o, con correr_en_B, el clon de B)
SALIDA = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(_router.__file__)))), "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida")
RESPALDO = os.path.join(RAIZ, "scratch", "test_direccion_respaldo"); os.makedirs(RESPALDO, exist_ok=True)
tocados = set()

def pdf_texto(numero):
    """GET /remitos/{id}/pdf del remito con ese número; devuelve (status, texto de la primera copia en una sola línea)."""
    con = sqlite3.connect(T); rid = con.execute("select id from remitos where numero_legal=?", (numero,)).fetchone()[0]; con.close()
    nombre = f"remito_{numero.replace('-', '_')}.pdf"
    if nombre not in tocados:
        tocados.add(nombre)
        if os.path.exists(os.path.join(SALIDA, nombre)): shutil.copyfile(os.path.join(SALIDA, nombre), os.path.join(RESPALDO, nombre))
    # [S891] cada caso dibuja un papel nuevo: sin la marca IMPRESO (bit 44) el servidor no entrega la imagen guardada del primer papel
    con = sqlite3.connect(T); con.execute("update remitos set flags_estado = coalesce(flags_estado, 0) & ~? where id=?", (1 << 44, rid)); con.commit(); con.close()
    r = cli.get(f"/remitos/{rid}/pdf")
    if r.status_code != 200: return r.status_code, ""
    out = os.path.join(RESPALDO, "_" + nombre); open(out, "wb").write(r.content)
    return 200, " ".join(fitz.open(out)[0].get_text().split())

def dom_guardado(numero):
    con = sqlite3.connect(T); d = con.execute("select domicilio_entrega_id from remitos where numero_legal=?", (numero,)).fetchone()[0]; con.close()
    return UUID(d).hex if d else None

# ---- Petroplastic 0015-00003031 (mostrador; el pedido tiene fiscal Pellegrini y entrega Ruta 234 en el mismo domicilio)
st, txt = pdf_texto("0015-00003031")
check(f"3031 Petroplastic [{st}]: imprime la dirección de ENTREGA del cliente (Ruta 234 Km 16, Junín de los Andes)", st == 200 and "RUTA 234 KM. 16" in txt and "JUNIN DE LOS ANDES" in txt)
check("3031: ya no dice Roseti 1482 debajo del cliente", "ROSETI 1482, CABA" not in txt)
check("3031: tampoco la fiscal (Pellegrini), porque hay de entrega", "PELLEGRINI" not in txt)
check("3031: el domicilio GUARDADO sigue siendo la oficina (es donde figura que se entregó; solo cambia el papel)", dom_guardado("0015-00003031") == OFICINA)
check("3031: conserva su número (no se renumera)", "0015-00003031" in txt)

# ---- Coalix 0015-00003030 (mostrador, oficina guardada)
st, txt = pdf_texto("0015-00003030")
db = S()
r30 = db.query(rmodels.Remito).filter(rmodels.Remito.numero_legal == "0015-00003030").first()
activos = [d for d in r30.pedido.cliente.domicilios if d.activo and UUID(str(d.id)).hex != OFICINA]
esperado = RemitosService._texto_domicilio(sorted([d for d in activos if d.es_entrega], key=lambda d: not d.es_predeterminado)[0] if any(d.es_entrega for d in activos)
                                           else [d for d in activos if d.es_fiscal][0]) if activos else None
db.close()
check(f"3030 Coalix [{st}]: el cliente tiene domicilio propio ({esperado!r}) y el papel lo imprime", st == 200 and esperado and esperado.upper().split(",")[0].strip() in txt)
check("3030: ya no dice Roseti 1482 debajo del cliente", "ROSETI 1482, CABA" not in txt)

# ---- un domicilio con dirección de entrega DISTINTA a la fiscal (si hay alguno con remito, además de Petroplastic)
con = sqlite3.connect(T)
filas = con.execute("""select r.numero_legal, d.calle, d.calle_entrega from remitos r join domicilios d on d.id=r.domicilio_entrega_id
                       where r.numero_legal is not null and trim(coalesce(d.calle_entrega,''))<>'' and upper(trim(d.calle_entrega))<>upper(trim(coalesce(d.calle,'')))
                       and r.numero_legal<>'0015-00003031' order by r.numero_legal desc limit 1""").fetchall()
con.close()
if filas:
    num, calle, calle_ent = filas[0]
    st, txt = pdf_texto(num)
    check(f"{num}: domicilio con entrega distinta ({calle.strip()[:25]} -> {calle_ent.strip()}): imprime la de entrega [{st}]", st == 200 and calle_ent.strip().upper() in txt)
else:
    check("(no hay otro remito con dirección de entrega distinta en esta copia: caso cubierto por el 3031)", True)

# ---- unidad: cuándo se usa el juego de entrega
D = lambda **k: Domicilio(**{**dict(calle=None, numero=None, piso=None, depto=None, localidad=None, provincia_id=None, cp=None, calle_entrega=None, numero_entrega=None,
                                   piso_entrega=None, depto_entrega=None, localidad_entrega=None, provincia_entrega_id=None, cp_entrega=None), **k})
t = RemitosService._texto_domicilio(D(calle="Paraguay", numero="1522", localidad="CABA", calle_entrega="Vieytes", numero_entrega="1549", localidad_entrega="CABA"))
check(f"entrega distinta de la calle fiscal: se usa la de entrega ({t})", t.startswith("Vieytes 1549") and "Paraguay" not in t)
t = RemitosService._texto_domicilio(D(calle="Av Cordoba", numero="2428", localidad="CABA", calle_entrega="AV CORDOBA ", numero_entrega="2428", localidad_entrega=""))
check(f"entrega que repite la calle y le falta la localidad (4 casos en P): se usa el domicilio completo, sin perder la localidad ({t})", t == "Av Cordoba 2428, CABA")
t = RemitosService._texto_domicilio(D(calle="Zuviria", numero="5747", calle_entrega="Calle Zuviria", numero_entrega="5747"))
check(f"«Calle Zuviria» contra «Zuviria» cuenta como distinta y sale la de entrega, que es la misma dirección ({t})", t == "Calle Zuviria 5747")

# ---- cliente SIN ninguna dirección (consumidor final / Rosa): recién ahí la oficina
con = sqlite3.connect(T)
pid, cid = con.execute("select p.id, p.cliente_id from remitos r join pedidos p on p.id=r.pedido_id where r.numero_legal='0015-00003031'").fetchone()
con.execute("delete from domicilios_clientes where cliente_id=?", (cid,))
con.execute("update pedidos set domicilio_entrega_id=NULL where id=?", (pid,))
con.commit(); con.close()
st, txt = pdf_texto("0015-00003031")
check(f"sin ningún domicilio del cliente (ni el del pedido): recién ahí imprime la oficina, Roseti 1482 [{st}]", st == 200 and "ROSETI 1482" in txt)
con = sqlite3.connect(T)
con.execute("insert into domicilios_clientes (cliente_id, domicilio_id, es_predeterminado, flags) values (?, ?, 1, 0)", (cid, OFICINA))
con.commit(); con.close()
st, txt = pdf_texto("0015-00003031")
check(f"cliente Rosa vinculado solo a la oficina (_ensure_domicilio_rosa): imprime Roseti 1482 [{st}]", st == 200 and "ROSETI 1482" in txt)

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
