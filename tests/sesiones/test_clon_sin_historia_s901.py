r"""S901, hallazgo H26 de CA (auditoría de la S900; pedido de Carlos 06/11: «comiteá y portá H26 y el cartel»).
`clone_pedido` copiaba la nota ENTERA del original con sus líneas [SISTEMA] y su OC: el #157 (clon del #151) decía «Flete a cargo NUESTRO (bit 48)» sin tener el bit 48 y contaba tres conversiones de circuito
ajenas; con la #215 (S900) cada clon habría heredado además «Cambio de estado: CUMPLIDO ➔ …» sin el bit 50. Ahora el clon lleva «Clonado de Pedido #N.» más lo que escribió una persona, sin las líneas [SISTEMA]
y sin la OC del original. Sobre una COPIA de la base de P del 05/11 10:21."""
import sys, os, sqlite3
from _esquema_p import copiar_p, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user, get_current_user_optional
from backend.pedidos.notas import nota_para_clon
import backend.pedidos.router as _pr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
APP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(_pr.__file__))))   # raíz del código que se está probando (D, o current/ del clon de B)
def leer(*partes): return open(os.path.join(APP, *partes), encoding="utf-8").read()
B34, B46, B48, B50 = 1 << 34, 1 << 46, 1 << 48, 1 << 50

# ---------- la nota del clon, sin base ----------
S_ = "\n[SISTEMA] Flete a cargo NUESTRO (bit 48). 2026-11-03 13:03 admin\n[SISTEMA] Cambio de estado: CUMPLIDO ➔ PENDIENTE por ana a las 14:07 05/11/2026."
check("sin nota o con la nota vacía: solo «Clonado de Pedido #5.»", nota_para_clon(None, 5) == "Clonado de Pedido #5." and nota_para_clon("", 5) == "Clonado de Pedido #5.")
check("una nota que son solo líneas [SISTEMA] (flete, cambios de estado, conversiones de circuito) no se hereda", nota_para_clon(S_, 5) == "Clonado de Pedido #5.")
check("el «Clonado de Pedido #N.» del original no se acumula en cadena (un clon de un clon dice solo de dónde viene)", nota_para_clon("Clonado de Pedido #111. " + S_, 151) == "Clonado de Pedido #151.")
check("lo que escribió una persona se conserva y las líneas [SISTEMA] no", nota_para_clon("Entregar por el portón verde" + S_, 5) == "Clonado de Pedido #5. Entregar por el portón verde")
check("una línea [SISTEMA] pegada al final de un texto corta desde ahí; varias líneas humanas se conservan", nota_para_clon("aviso del cliente [SISTEMA] Migrado a pedido #9.\nsegunda línea", 5) == "Clonado de Pedido #5. aviso del cliente\nsegunda línea")
check("las notas que escribió el sistema al nacer de una factura («Ingesta Automática Factura: …», «Ingesta en Cuarentena Factura: …», «Ingesta en Cuarentena») hablan de ESA factura y tampoco se heredan; una línea humana que nombra la Ingesta sí",
      nota_para_clon("Ingesta Automática Factura: 00001-00002514", 1) == "Clonado de Pedido #1." and nota_para_clon("Ingesta en Cuarentena Factura: 00001-00002941", 1) == "Clonado de Pedido #1."
      and nota_para_clon("Ingesta en Cuarentena", 1) == "Clonado de Pedido #1." and nota_para_clon("Pedir a Ingesta que revise la OC", 1) == "Clonado de Pedido #1. Pedir a Ingesta que revise la OC")

# ---------- el clon por la API, sobre la copia de P ----------
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261105_1021.db"
T = os.path.join(RAIZ, "scratch", "test_clon_sin_historia_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "prueba"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U(); app.dependency_overrides[get_current_user_optional] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
_aparte = imagenes_aparte(APP); _aparte.__enter__()
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
def ped(pid): return q("select estado, flags_estado, nota, oc, total from pedidos where id=?", pid)[0]
def clonar(pid):
    r = cli.post(f"/pedidos/{pid}/clone")
    return r, (r.json().get("id") if r.status_code == 200 else None)

n151 = ped(151)[2] or ""
check("partida: el #151 (Centro Pet) tiene líneas [SISTEMA] y el «Clonado de Pedido #111.» heredado", "[SISTEMA]" in n151 and "Clonado de Pedido #111." in n151)
r, c1 = clonar(151)
e, f, n, oc, tot = ped(c1)
check(f"clonar el #151 [{r.status_code}] da un pedido NUEVO con la nota «Clonado de Pedido #151.» y NADA de las líneas [SISTEMA] del original (ni el flete, ni las conversiones de circuito)",
      r.status_code == 200 and n.strip() == "Clonado de Pedido #151." and "[SISTEMA]" not in n and "Flete" not in n and "Circuito" not in n)
check("el clon no hereda la OC (la del original sigue en el original), nace Presupuesto y sin los bits de la historia del otro (46, 48, 50, Cumplido) y conserva renglones y total",
      oc in (None, "") and e == "PRESUPUESTO" and not f & (B46 | B48 | B50 | B34)
      and q("select count(*), sum(cantidad) from pedidos_items where pedido_id=?", c1) == q("select count(*), sum(cantidad) from pedidos_items where pedido_id=151") and abs(tot - ped(151)[4]) < 0.01)
check("el original queda como estaba (nota entera con sus líneas [SISTEMA])", ped(151)[2] == n151)
r2, c2 = clonar(c1)
check(f"clonar el clon [{r2.status_code}]: «Clonado de Pedido #{c1}.» y no se acumula la cadena", r2.status_code == 200 and ped(c2)[2].strip() == f"Clonado de Pedido #{c1}.")
con_oc = q("select id, oc from pedidos where coalesce(oc,'') != '' and id in (select pedido_id from pedidos_items) order by id desc limit 1")[0]
r3, c3 = clonar(con_oc[0])
check(f"un pedido con OC («{con_oc[1]}», #{con_oc[0]}) se clona sin su OC y el original la conserva [{r3.status_code}]", r3.status_code == 200 and ped(c3)[3] in (None, "") and ped(con_oc[0])[3] == con_oc[1])
# el cruce con la #215: un Cumplido limpio que se reabrió tiene la línea «Cambio de estado» y el bit 50; su clon no hereda ni la una ni el otro
L1 = q("select id from pedidos where (flags_estado & ?) != 0 and (flags_estado & ?) = 0 and (flags_estado & ?) = 0 and (flags_estado & 4096) = 0 and id not in (98, 136) order by id limit 1", B34, B46, B50)[0][0]
rr = cli.patch(f"/pedidos/{L1}", json={"estado": "Pendiente"})
check(f"partida (cruce con la #215): el Cumplido #{L1} reabierto tiene el bit 50 y la línea «Cambio de estado: CUMPLIDO ➔ PENDIENTE» [{rr.status_code}]", rr.status_code == 200 and ped(L1)[1] & B50 and "Cambio de estado: CUMPLIDO ➔ PENDIENTE" in ped(L1)[2])
r4, c4 = clonar(L1)
check(f"su clon (#{c4}) no hereda la línea «Cambio de estado» ni el bit 50 [{r4.status_code}] nota del clon: {ped(c4)[2]!r}",
      r4.status_code == 200 and "Cambio de estado" not in ped(c4)[2] and not ped(c4)[1] & B50 and ped(c4)[2].strip() == f"Clonado de Pedido #{L1}." and "Ingesta" not in ped(c4)[2])
pr = leer("backend", "pedidos", "router.py")
check("el servidor usa el helper y no copia la OC", "nota=nota_para_clon(original.nota, original.id)," in pr and "oc=None," in pr and 'nota=f"Clonado de Pedido #{original.id}. {original.nota or \'\'}"' not in pr)

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
try: _aparte.__exit__(None, None, None)
except Exception: pass
del cli; eng.dispose()
try: os.remove(T)
except OSError: pass
sys.exit(1 if falla else 0)
