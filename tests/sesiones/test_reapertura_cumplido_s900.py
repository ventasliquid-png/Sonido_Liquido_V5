r"""S900, Card #215 (Carlos 05/11: «¿no estamos diseñando una trampa? no queda un registro de que el pedido pasó de cerrado a abierto y cerrado de nuevo»; Nike, Sello de Oro 05/11):
(1) TODA transición de estado de un pedido deja en su nota «[SISTEMA] Cambio de estado: {anterior} ➔ {nuevo} por {usuario} a las {HH:MM DD/MM/AAAA}.»;
(2) salir de CUMPLIDO hacia cualquier estado prende el bit 50 (FUE_REABIERTO), en el instante de reabrir, una vez y para siempre; Anulado → Pendiente NO lo prende;
(3) las cuatro puertas de salida de Cumplido: el cambio de estado (PATCH /pedidos/{id}), la corrección por renglón (que reabre sola), la anulación de «anular y reingestar» y la
    migración por discrepancia; (4) el listado y la ficha muestran la marca. Sobre una COPIA de la base de P del 05/11 10:21 (el #98 ya está Cumplido con el bit 46)."""
import sys, os, re, json, sqlite3, subprocess
from datetime import datetime
from _esquema_p import copiar_p, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user, get_current_user_optional
from backend.pedidos.constants import PedidoFlags as PF
from backend.pedidos.transiciones import registrar_cambio_de_estado, nombre_de_estado, SIN_SESION
import backend.pedidos.router as _pr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
APP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(_pr.__file__))))   # raíz del código que se está probando (D, o current/ del clon de B)
def leer(*partes): return open(os.path.join(APP, *partes), encoding="utf-8").read()
B33, B34, B35, B36, B46, B50 = 1 << 33, 1 << 34, 1 << 35, 1 << 36, 1 << 46, 1 << 50
FILA = re.compile(r"\[SISTEMA\] Cambio de estado: (\w+) ➔ (\w+) por (.+?) a las (\d\d:\d\d \d\d/\d\d/\d{4})\.")

# ---------- (1) el bit y el helper, sin base ----------
check("el bit 50 se llama FUE_REABIERTO, vale 1 << 50 = 1125899906842624 y ningún otro miembro de PedidoFlags comparte ese valor",
      PF.FUE_REABIERTO.value == 1 << 50 == 1125899906842624 and [m.name for m in PF if m.value == 1 << 50] == ["FUE_REABIERTO"])
class P_:
    def __init__(self, flags, nota=""): self.flags_estado, self.nota = flags, nota
ESTADOS = {"PRESUPUESTO": 1 << 32, "PENDIENTE": B33, "CUMPLIDO": B34, "ANULADO": B35}
def pasar(de, a, flags_extra=0, nota="", usuario="ana", ahora=None):
    p = P_(ESTADOS[de] | flags_extra, nota); antes = p.flags_estado
    p.flags_estado = (p.flags_estado & ~sum(ESTADOS.values())) | ESTADOS[a]
    return p, registrar_cambio_de_estado(p, antes, usuario, ahora)
p, linea = pasar("CUMPLIDO", "PENDIENTE", ahora=datetime(2026, 11, 5, 14, 7))
check("Cumplido → Pendiente: la línea sale en el formato de Nike, con usuario y «HH:MM DD/MM/AAAA», va en la nota y prende el bit 50",
      linea == "[SISTEMA] Cambio de estado: CUMPLIDO ➔ PENDIENTE por ana a las 14:07 05/11/2026." and p.nota == "\n" + linea and p.flags_estado & B50)
p, linea = pasar("CUMPLIDO", "PRESUPUESTO"); check("Cumplido → Presupuesto prende el bit 50", p.flags_estado & B50 and "CUMPLIDO ➔ PRESUPUESTO" in linea)
p, linea = pasar("CUMPLIDO", "ANULADO"); check("Cumplido → Anulado prende el bit 50", p.flags_estado & B50 and "CUMPLIDO ➔ ANULADO" in linea)
p, linea = pasar("ANULADO", "PENDIENTE"); check("Anulado → Pendiente NO prende el bit 50 (dictamen de Nike), pero sí deja su línea", not p.flags_estado & B50 and "ANULADO ➔ PENDIENTE" in linea)
p, linea = pasar("PENDIENTE", "CUMPLIDO"); check("Pendiente → Cumplido (un cierre normal) deja la línea y no prende el bit 50", not p.flags_estado & B50 and "PENDIENTE ➔ CUMPLIDO" in linea)
p, linea = pasar("PRESUPUESTO", "PENDIENTE"); check("Presupuesto → Pendiente: línea, sin bit 50", not p.flags_estado & B50 and "PRESUPUESTO ➔ PENDIENTE" in linea)
p, linea = pasar("PENDIENTE", "PENDIENTE")
check("si el estado no cambió no hace nada: devuelve None, no toca la nota ni los flags", linea is None and p.nota == "" and p.flags_estado == B33)
p, linea = pasar("CUMPLIDO", "PENDIENTE", usuario=None); check("sin sesión lo dice: «por (sin sesión)»", f"por {SIN_SESION} a las" in linea and SIN_SESION == "(sin sesión)")
p, _ = pasar("CUMPLIDO", "PENDIENTE", flags_extra=B46 | (1 << 12), nota="nota previa")
check("el resto de los flags queda intacto (el bit 46 y el Rosa) y la nota previa se conserva", p.flags_estado & B46 and p.flags_estado & (1 << 12) and p.nota.startswith("nota previa\n[SISTEMA]"))
p, _ = pasar("CUMPLIDO", "PENDIENTE"); antes = p.flags_estado; p.flags_estado = (p.flags_estado & ~sum(ESTADOS.values())) | B34; registrar_cambio_de_estado(p, antes, "ana")
check("al re-cerrar el bit 50 sigue prendido (una vez y para siempre) y el re-cierre deja su propia línea", p.flags_estado & B50 and p.nota.count("Cambio de estado") == 2 and "PENDIENTE ➔ CUMPLIDO" in p.nota)

# ---------- (2) sobre la copia de P: el cambio de estado de siempre ----------
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261105_1021.db"
T = os.path.join(RAIZ, "scratch", "test_reapertura_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "prueba"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
app.dependency_overrides[get_current_user_optional] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
_aparte = imagenes_aparte(APP); _aparte.__enter__()
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
def ped(pid): return q("select estado, flags_estado, nota, oc from pedidos where id=?", pid)[0]
def estado(pid, e, **extra):
    r = cli.patch(f"/pedidos/{pid}", json={"estado": e, **extra})
    if r.status_code == 409 and "CIERRE_CON_DISCREPANCIA" in r.text:
        r = cli.patch(f"/pedidos/{pid}", json={"estado": e, "cierre_confirmado": True, **extra})
    return r
def lineas(pid): return FILA.findall(ped(pid)[2] or "")

limpio = q("select id from pedidos where (flags_estado & ?) != 0 and (flags_estado & ?) = 0 and (flags_estado & ?) = 0 and (flags_estado & 4096) = 0 and id not in (98, 136) order by id limit 2", B34, B46, B50)
L1, L2 = limpio[0][0], limpio[1][0]
n0 = ped(L1)[2] or ""
check(f"partida: el #{L1} y el #{L2} están Cumplidos, sin la marca de ajuste (bit 46) y sin el bit 50", ped(L1)[1] & B34 and not ped(L1)[1] & (B46 | B50) and ped(L2)[1] & B34)
r = estado(L1, "Pendiente")
e, f, n1, _ = ped(L1)
check(f"reabrir el Cumplido LIMPIO #{L1} [{r.status_code}]: queda PENDIENTE, el bit 50 se prende y la nota recibe la línea con el usuario (antes no dejaba NADA)",
      r.status_code == 200 and f & B33 and not f & B34 and f & B50 and lineas(L1)[-1][:3] == ("CUMPLIDO", "PENDIENTE", "prueba") and n1.startswith(n0))
check("y como no tenía la marca de ajuste NO aparece la otra línea («salió de Cumplido… con ajuste»): la nueva es la que lo registra", "salió de Cumplido" not in n1 and not f & B46)
hh, mm, dd, mo, yy = re.match(r"(\d\d):(\d\d) (\d\d)/(\d\d)/(\d{4})", lineas(L1)[-1][3]).groups()
check("la hora de la línea es la de ahora (mismo día y a lo sumo unos minutos de diferencia)", abs((datetime.now() - datetime(int(yy), int(mo), int(dd), int(hh), int(mm))).total_seconds()) < 600)
r = estado(L1, "Pendiente")
check("guardar otra vez en Pendiente no repite la línea", r.status_code == 200 and len(lineas(L1)) == 1)
r = estado(L1, "Cumplido")
e, f, n2, _ = ped(L1)
check(f"re-cerrarlo [{r.status_code}]: vuelve a CUMPLIDO, el bit 50 SIGUE (cicatriz) y el re-cierre deja su propia línea: {[x[:2] for x in lineas(L1)]}",
      r.status_code == 200 and f & B34 and f & B50 and [x[:2] for x in lineas(L1)] == [("CUMPLIDO", "PENDIENTE"), ("PENDIENTE", "CUMPLIDO")])
r = estado(L1, "Pendiente")
check("reabrirlo una segunda vez deja otra línea: cada reapertura queda registrada", r.status_code == 200 and [x[:2] for x in lineas(L1)].count(("CUMPLIDO", "PENDIENTE")) == 2)

# la nota se puede borrar desde la ficha (PATCH oc-y-nota la reemplaza entera): el bit no
r = cli.patch(f"/pedidos/{L1}/oc-y-nota", json={"nota": ""})
e, f, n3, _ = ped(L1)
check(f"si el operador borra la nota entera desde la ficha [{r.status_code}], las líneas [SISTEMA] se van pero el bit 50 queda: la cicatriz no se borra desde esa pantalla",
      r.status_code == 200 and not (n3 or "").strip() and f & B50)
j = cli.get(f"/pedidos/{L1}").json()
check("la API de la ficha entrega flags_estado con el bit 50", int(j.get("flags_estado") or 0) & B50)

# Cumplido → Anulado, y Anulado → Pendiente no apaga ni vuelve a prender nada
r = estado(L2, "Anulado")
e, f, _, _ = ped(L2)
check(f"Cumplido → Anulado (#{L2}) [{r.status_code}]: ANULADO, bit 50 prendido y línea «CUMPLIDO ➔ ANULADO»", r.status_code == 200 and f & B35 and f & B50 and lineas(L2)[-1][:2] == ("CUMPLIDO", "ANULADO"))
r = estado(L2, "Pendiente")
check("y volver de Anulado a Pendiente deja su línea, no toca la cicatriz (sigue prendida) y no duplica nada", r.status_code == 200 and ped(L2)[1] & B50 and lineas(L2)[-1][:2] == ("ANULADO", "PENDIENTE") and len(lineas(L2)) == 2)

# un pedido que nunca estuvo Cumplido: Pendiente → Anulado → Pendiente → Cumplido, sin bit 50
nuevo = q("select id from pedidos where (flags_estado & ?) != 0 and (flags_estado & ?) = 0 and (flags_estado & 4096) = 0 order by id desc limit 1", B33, B50)[0][0]
for e_ in ("Anulado", "Pendiente", "Cumplido"):
    r = estado(nuevo, e_)
check("un pedido que nunca estuvo Cumplido (Pendiente → Anulado → Pendiente → Cumplido): tres líneas y el bit 50 apagado",
      r.status_code == 200 and [x[:2] for x in lineas(nuevo)] == [("PENDIENTE", "ANULADO"), ("ANULADO", "PENDIENTE"), ("PENDIENTE", "CUMPLIDO")] and not ped(nuevo)[1] & B50)

# el #98: cerrado con ajuste (bit 46); reabrirlo deja las dos líneas, en orden, y los dos bits
e98, f98, n98, _ = ped(98)
check("partida: el #98 está Cumplido con el bit 46 y sin el 50", e98 == "CUMPLIDO" and f98 & B46 and not f98 & B50)
r = estado(98, "Pendiente")
e, f, n, _ = ped(98)
i_nueva, i_vieja = n.find("Cambio de estado: CUMPLIDO ➔ PENDIENTE"), n.find("El pedido salió de Cumplido (Pendiente)")
check(f"reabrir el #98 [{r.status_code}]: la línea nueva y la del bit 46 conviven (la nueva primero), el 46 sigue y el 50 se prende", r.status_code == 200 and 0 < i_nueva < i_vieja and f & B46 and f & B50 and n.startswith(n98))

# ---------- (3) las otras puertas ----------
r136 = q("select id from remitos where numero_legal=?", "0015-00003030")
if r136:
    R30 = r136[0][0]; I30, PI30 = q("select id, pedido_item_id from remitos_items where remito_id=? order by id limit 1", R30)[0]
    e0, f0, n0_, _ = ped(136)
    cant = q("select cantidad_remitida from remitos_items where id=?", I30)[0][0]
    check("partida: el #136 (remito 0015-3030) está Cumplido y sin el bit 50", e0 == "CUMPLIDO" and f0 & B34 and not f0 & B50 and cant and cant > 1)
    r = cli.post(f"/remitos/{R30}/correccion", json={"remito_item_id": I30, "cantidad_real": cant - 1, "causa": "NO_SALIO", "nota": "prueba S900"})
    e, f, n, _ = ped(136)
    usuario1 = (q("select username from usuarios where id=1") or [("?",)])[0][0]
    check(f"la corrección por renglón reabre sola el Cumplido [{r.status_code}]: queda PENDIENTE, el bit 50 se prende, la línea nueva lleva al autor ({usuario1}) y la nota «Reabierto el…» de siempre se conserva",
          r.status_code == 200 and r.json().get("pedido_reabierto") is True and f & B33 and f & B50 and lineas(136) and lineas(136)[-1][:3] == ("CUMPLIDO", "PENDIENTE", usuario1) and "[SISTEMA] Reabierto el " in n)
else:
    check("(la copia no tiene el remito 0015-3030: se omite la puerta de la corrección)", True)
ing = leer("backend", "ingesta", "router.py"); pr = leer("backend", "pedidos", "router.py"); rs = leer("backend", "remitos", "service.py")
check("la anulación de «anular y reingestar» registra la transición con el sistema como autor (y el bit 50 si el pedido estaba Cumplido)",
      "from backend.pedidos.transiciones import registrar_cambio_de_estado" in ing and 'registrar_cambio_de_estado(pedido_asoc, flags_previos, "el sistema (anular y reingestar)")' in ing)
check("la migración por discrepancia (pedido viejo → Anulado) registra la transición con el sistema como autor",
      'registrar_cambio_de_estado(pedido_viejo, flags_previos, "el sistema (migración por discrepancia en Ingesta)")' in pr)
check("el cambio de estado de siempre registra con el usuario de la sesión, antes de la nota del cierre con discrepancia",
      'registrar_cambio_de_estado(pedido, current_state_bit, getattr(current_user, "username", None))' in pr
      and pr.index("registrar_cambio_de_estado(pedido, current_state_bit") < pr.index("nota_forense = f\"\\n[SISTEMA] Cierre confirmado con discrepancia"))
check("la corrección por renglón registra con el autor de la sesión", "registrar_cambio_de_estado(pedido, flags_previos, getattr(autor, \"username\", None))" in rs)

# ---------- (4) la marca en pantalla ----------
lis, can = leer("frontend", "src", "views", "Pedidos", "PedidoList.vue"), leer("frontend", "src", "views", "Ventas", "PedidoCanvas.vue")
check("el listado muestra «reabierto» con el bit 50 (BigInt: el & de JS no llega a ese bit)",
      "const fueReabierto = (pedido) =>" in lis and "(1n << 50n)" in lis and 'v-if="fueReabierto(pedido)" data-test="reabierto"' in lis)
check("la ficha del pedido muestra la misma marca junto al estado", "const fueReabierto = computed(" in can and "(1n << 50n)" in can and 'v-if="fueReabierto" data-test="reabierto"' in can)
rc = subprocess.run(["node", "-e", "const f = [1125899906842624 + 8589934592, 70385925095489, 1125899906842624 + 70385925095489];"
                     "console.log(JSON.stringify(f.map(x => (BigInt(Math.trunc(Number(x) || 0)) & (1n << 50n)) !== 0n)))"], capture_output=True, text=True, timeout=30)
check("la cuenta de pantalla anda con los números reales: prende con el bit 50 y no con el #98 sin él (70385925095489)", rc.stdout.strip() == "[true,false,true]")
js = ("const fs = require('fs'); const { createRequire } = require('module'); const req = createRequire('C:/dev/Sonido_Liquido_V5/frontend/package.json');"
      "const { parse, compileTemplate, compileScript } = req('@vue/compiler-sfc'); const out = {}; const base = " + json.dumps(APP.replace("\\", "/")) + " + '/frontend/src/views/';"
      "for (const f of ['Pedidos/PedidoList', 'Ventas/PedidoCanvas']) { const src = fs.readFileSync(base + f + '.vue', 'utf8');"
      "const { descriptor, errors } = parse(src, { filename: f }); let n = errors.length; if (!n) { n += compileTemplate({ source: descriptor.template.content, filename: f, id: 'x' }).errors.length; compileScript(descriptor, { id: 'x' }); } out[f] = n }"
      "console.log(JSON.stringify(out))")
try:
    res_js = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", timeout=180).stdout.strip())
except (OSError, ValueError, subprocess.SubprocessError):
    res_js = {}
check("el listado y la ficha compilan (parseo, plantilla y script) sin errores", res_js == {"Pedidos/PedidoList": 0, "Ventas/PedidoCanvas": 0})

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
try: _aparte.__exit__(None, None, None)
except Exception: pass
try: os.remove(T)
except OSError: pass
sys.exit(1 if falla else 0)
