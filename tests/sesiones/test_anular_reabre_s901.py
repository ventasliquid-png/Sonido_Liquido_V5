r"""S901, Card #217 F1 (mapa del flujo documental; Nike, Sello de Oro 06/11/2026, Q3: «REABRE OBLIGATORIAMENTE»): anular el remito que respaldaba la entrega de un pedido CUMPLIDO lo
reabre (PENDIENTE), aunque la orden venga del remito y no del pedido. Antes el pedido quedaba Cumplido con nada entregado y sin rastro.
Reglas: (a) reabre si ya no queda ningún remito emitido y vigente, o (b) el pedido estaba entregado completo (bit 21) y ya no lo está; NO reabre si el remito anulado no tenía ningún renglón
con salida, ni si el pedido no estaba Cumplido, ni a un Cumplido cerrado a propósito con entrega parcial al que todavía le queda un remito vigente. Deja las mismas huellas que cualquier salida de
Cumplido: «Cambio de estado», bit 50 y una línea que dice por qué; y anula los RI que había generado el Cumplido. La pantalla avisa. Sobre una COPIA de la base de P del 05/11 10:21."""
import sys, os, re, json, sqlite3, subprocess, uuid
from _esquema_p import copiar_p, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user, get_current_user_optional
import backend.pedidos.router as _pr
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
APP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(_pr.__file__))))   # raíz del código que se está probando (D, o current/ del clon de B)
def leer(*partes): return open(os.path.join(APP, *partes), encoding="utf-8").read()
B20, B21, B33, B34, B50 = 1 << 20, 1 << 21, 1 << 33, 1 << 34, 1 << 50
FILA = re.compile(r"\[SISTEMA\] Cambio de estado: (\w+) ➔ (\w+) por (.+?) a las (\d\d:\d\d \d\d/\d\d/\d{4})\.")

ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261105_1021.db"
T = os.path.join(RAIZ, "scratch", "test_anular_reabre_tmp.db"); copiar_p(ORIG, T)
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
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.commit(); con.close(); return v
def ped(pid): return q("select estado, flags_estado, nota from pedidos where id=?", pid)[0]
def rem(rid): return q("select estado, numero_legal, flags_estado from remitos where id=?", rid)[0]
def remito_de(pid, numero=None):
    return q("select id from remitos where pedido_id=? and numero_legal " + ("= ?" if numero else "is not null") + " order by fecha_creacion limit 1", *([pid, numero] if numero else [pid]))[0][0]
def anular(rid, motivo="Se emitió por error"): return cli.post(f"/remitos/{rid}/anular", json={"motivo": motivo})
def lineas(pid): return FILA.findall(ped(pid)[2] or "")
def nuevo_remito(pid, numero, items, estado="ENTREGADO", como=None):
    """Agrega un remito vigente numerado al pedido (copiando los datos de otro del mismo pedido): items = [(pedido_item_id, cantidad)]."""
    con = sqlite3.connect(T); con.row_factory = sqlite3.Row
    base = con.execute("select * from remitos where id=?", (como or remito_de(pid),)).fetchone()
    d = dict(base); d.update(id=uuid.uuid4().hex, pedido_id=pid, numero_legal=numero, estado=estado, fecha_creacion="2026-11-05 12:00:00")
    con.execute(f"insert into remitos ({','.join(d)}) values ({','.join('?' * len(d))})", list(d.values()))
    for pi, cant in items:
        con.execute("insert into remitos_items (remito_id, pedido_item_id, cantidad_remitida, cantidad_declarada) values (?,?,?,?)", (d["id"], pi, cant, cant))
    con.commit(); con.close(); return d["id"]

# ---------- (1) el caso simple: un 0015 que respaldaba toda la entrega ----------
P1 = 79
rid = remito_de(P1)
e0, f0, n0 = ped(P1)
check(f"partida: el #{P1} está CUMPLIDO, entregado completo (bit 21), con un solo remito vigente {rem(rid)[1]} y sin el bit 50", f0 & B34 and f0 & B21 and not f0 & B50 and rem(rid)[0] != "ANULADO")
r = anular(rid)
e1, f1, n1 = ped(P1)
j = r.json() if r.status_code == 200 else {}
check(f"anular ese remito [{r.status_code}]: el remito queda ANULADO y la respuesta avisa «pedido_reabierto»", r.status_code == 200 and rem(rid)[0] == "ANULADO" and j.get("pedido_reabierto") is True)
check("el pedido VUELVE A PENDIENTE (estado y bit 33), sale del Cumplido (bit 34) y se apaga la entrega completa (bit 21)", e1 == "PENDIENTE" and f1 & B33 and not f1 & B34 and not f1 & B21)
check("prende el bit 50 (FUE_REABIERTO): la cicatriz de que estuvo cerrado", f1 & B50)
check("la nota recibe la línea «Cambio de estado: CUMPLIDO ➔ PENDIENTE por prueba», en el formato de la #215", lineas(P1)[-1][:3] == ("CUMPLIDO", "PENDIENTE", "prueba") and n1.startswith(n0))
check("y otra línea que dice POR QUÉ: el remito, su motivo y que el pedido vuelve a deber", "[SISTEMA] Reabierto el" in n1 and "se anuló el remito 0015-00003039 (motivo: Se emitió por error)" in n1 and "vuelve a deber" in n1)
r = anular(rid)
check("anular otra vez el mismo remito sigue dando 409 y no repite nada", r.status_code == 409 and "REMITO_YA_ANULADO" in r.text and len(lineas(P1)) == 1)
r = cli.post(f"/remitos/{rid}/deshacer-anulacion", json={"motivo": "Era correcto"})
e2, f2, n2 = ped(P1)
check(f"deshacer la anulación [{r.status_code}] devuelve el remito pero NO re-cierra el pedido solo: sigue PENDIENTE con el bit 50 (cerrarlo es una decisión del operador) y recupera la entrega completa",
      r.status_code == 200 and rem(rid)[0] != "ANULADO" and e2 == "PENDIENTE" and f2 & B50 and f2 & B21 and not f2 & B34)

# ---------- (2) un Rosa: el remito es el RI que generó el Cumplido ----------
P2 = 141
rid = remito_de(P2)
check(f"partida: el #{P2} es un Rosa CUMPLIDO con un solo RI ({rem(rid)[1]})", ped(P2)[1] & B34 and rem(rid)[1].startswith("RI"))
r = anular(rid, "El cliente no lo retiró")
e, f, n = ped(P2)
check(f"anular el RI [{r.status_code}]: el pedido Rosa vuelve a PENDIENTE con el bit 50 y sus dos líneas; el RI ya anulado no se menciona dos veces",
      r.status_code == 200 and e == "PENDIENTE" and f & B33 and not f & B34 and f & B50 and lineas(P2)[-1][:2] == ("CUMPLIDO", "PENDIENTE") and "También se anul" not in n and rem(rid)[0] == "ANULADO")

# ---------- (3) un Cumplido al que le queda un RI generado por el Cumplido: el pedido se reabre y ese RI también se anula ----------
P3 = 148
ri = remito_de(P3)
q("delete from remitos_items where id = 121")                                                    # el RI cubría los renglones 294 (4) y 295 (8): ahora solo el primero
b = nuevo_remito(P3, "0015-99999001", [(295, 8.0)], como=remito_de(79))                         # y un 0015 a mano cubre el segundo
check(f"partida: el #{P3} (Cumplido, entregado completo) tiene dos remitos vigentes: el RI del Cumplido y un 0015 a mano", ped(P3)[1] & B34 and rem(ri)[0] != "ANULADO" and rem(b)[0] != "ANULADO")
r = anular(b, "Se devolvió todo")
e, f, n = ped(P3)
check(f"anular el 0015 [{r.status_code}]: aunque todavía queda un remito vigente (el RI), el pedido deja de estar entregado completo → se REABRE", r.status_code == 200 and e == "PENDIENTE" and f & B50 and not f & B34 and not f & B21)
check("y como al salir de Cumplido a mano, el RI que había generado el Cumplido también se anula, y la nota lo dice", rem(ri)[0] == "ANULADO" and "También se anuló el RI RI01-00000001" in n)

# ---------- (4) lo que NO debe reabrir ----------
# (4a) un Cumplido cerrado a propósito con entrega parcial, al que le queda un remito vigente
P4 = 94
q("update pedidos_items set cantidad = 10 where pedido_id = ?", P4)
r1 = remito_de(P4)
q("update remitos_items set cantidad_remitida = 3, cantidad_declarada = 3 where remito_id = ?", r1)
item4 = q("select pedido_item_id from remitos_items where remito_id = ?", r1)[0][0]
r2 = nuevo_remito(P4, "0015-99999002", [(item4, 3.0)], como=r1)
q("update pedidos set flags_estado = (flags_estado & ~?) | ? where id = ?", B21, B20, P4)
check(f"partida: el #{P4} es un Cumplido con entrega PARCIAL (6 de 10, bit 20, sin el 21) y dos remitos vigentes", ped(P4)[1] & B34 and ped(P4)[1] & B20 and not ped(P4)[1] & B21)
n_antes = ped(P4)[2]
r = anular(r2)
e, f, n = ped(P4)
check(f"anular uno de los dos [{r.status_code}]: el pedido NO se reabre (nunca estuvo entregado completo y todavía queda un remito vigente): sigue CUMPLIDO, sin bit 50 y sin líneas nuevas en la nota",
      r.status_code == 200 and r.json().get("pedido_reabierto") is False and f & B34 and not f & B50 and n == n_antes)
r = anular(r1)
e, f, n = ped(P4)
check(f"pero al anular el ÚLTIMO remito vigente [{r.status_code}] sí se reabre: queda PENDIENTE con el bit 50", r.status_code == 200 and e == "PENDIENTE" and f & B50 and not f & B34)

# (4b) un remito sin ningún renglón con salida (papel viejo vacío) no respaldaba la entrega
P5 = 1
rid = remito_de(P5)
check(f"partida: el #{P5} es un Cumplido viejo cuyo remito {rem(rid)[1]} no tiene renglones", ped(P5)[1] & B34 and q("select count(*) from remitos_items where remito_id=?", rid)[0][0] == 0)
r = anular(rid)
check(f"anular ese remito vacío [{r.status_code}]: no reabre nada (no respaldaba entrega alguna)", r.status_code == 200 and ped(P5)[1] & B34 and not ped(P5)[1] & B50 and r.json().get("pedido_reabierto") is False)

# (4c) un pedido que no está Cumplido
P6 = 151
check(f"partida: el #{P6} está PENDIENTE con un remito vigente", ped(P6)[1] & B33 and not ped(P6)[1] & B34)
n_antes = ped(P6)[2]
r = anular(remito_de(P6))
e, f, n = ped(P6)
check(f"anular su remito [{r.status_code}]: sigue PENDIENTE, sin bit 50 y sin ninguna línea de reapertura (la nota no cambia)", r.status_code == 200 and f & B33 and not f & B50 and n == n_antes and r.json().get("pedido_reabierto") is False)

# (4d) un remito facturado sigue sin poder anularse, y el pedido no se toca
P7 = q("select r.pedido_id, r.id from remitos r join pedidos p on p.id = r.pedido_id join facturas_remitos fr on fr.remito_id = r.id "
       "where r.numero_legal is not null and r.estado != 'ANULADO' and (p.flags_estado & ?) != 0 order by p.id desc limit 1", B34)[0]
f_antes = ped(P7[0])[1]
r = anular(P7[1])
check(f"un remito amparado por una factura sigue dando 409 [{r.status_code}] (primero va la nota de crédito) y el pedido #{P7[0]} queda como estaba", r.status_code == 409 and "REMITO_FACTURADO" in r.text and ped(P7[0])[1] == f_antes)

# ---------- (5) la pantalla y el código ----------
svc, rtr, sch = leer("backend", "remitos", "service.py"), leer("backend", "remitos", "router.py"), leer("backend", "remitos", "schemas.py")
vue = leer("frontend", "src", "views", "Logistica", "RemitoListView.vue")
check("el servicio tiene `reabrir_si_dejo_de_estar_cumplido` y reutiliza `registrar_cambio_de_estado` y `anular_ri_de_cumplido` (no repite su lógica)",
      "def reabrir_si_dejo_de_estar_cumplido(" in svc and svc.count("registrar_cambio_de_estado(pedido, flags_previos") >= 2 and "RemitosService.anular_ri_de_cumplido(db, pedido," in svc)
check("el router de «anular» la llama después de recalcular los bits 20/21 y devuelve `pedido_reabierto`; el esquema lo declara con False por defecto",
      "reabrir_si_dejo_de_estar_cumplido(db, remito.pedido, remito, motivo, estaba_completo, current_user)" in rtr and "remito.pedido_reabierto = reabierto" in rtr
      and "pedido_reabierto: bool = False" in sch)
check("la lista de remitos avisa al operador («estaba Cumplido y volvió a Pendiente») y el cartel de «Anular» lo explica",
      "respuesta?.data?.pedido_reabierto" in vue and "estaba Cumplido y volvió a Pendiente" in vue and "el pedido vuelve a Pendiente (queda anotado)" in vue)
js = ("const fs = require('fs'); const { createRequire } = require('module'); const req = createRequire('C:/dev/Sonido_Liquido_V5/frontend/package.json');"
      "const { parse, compileTemplate, compileScript } = req('@vue/compiler-sfc'); const out = {}; const base = " + json.dumps(APP.replace("\\", "/")) + " + '/frontend/src/views/';"
      "for (const f of ['Logistica/RemitoListView']) { const src = fs.readFileSync(base + f + '.vue', 'utf8');"
      "const { descriptor, errors } = parse(src, { filename: f }); let n = errors.length; if (!n) { n += compileTemplate({ source: descriptor.template.content, filename: f, id: 'x' }).errors.length; compileScript(descriptor, { id: 'x' }); } out[f] = n }"
      "console.log(JSON.stringify(out))")
try:
    res_js = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", timeout=180).stdout.strip())
except (OSError, ValueError, subprocess.SubprocessError):
    res_js = {}
check("la lista de remitos compila sin errores", res_js == {"Logistica/RemitoListView": 0})

_aparte.__exit__(None, None, None)
ok = sum(1 for _, c in checks if c)
print(f"\n{ok}/{len(checks)} checks OK")
sys.exit(0 if ok == len(checks) else 1)
