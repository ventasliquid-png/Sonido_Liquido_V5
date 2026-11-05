r"""S900, Card #214 (Carlos 05/11, a raíz de la 2603 y el pedido #155: «¿no sería lógico que si la conciliación lee Pedido = Entregado / facturado proponga un «¿Pasamos a Cumplido?»… como me pasó a mí ahora?» y «el remito que se carga
después, como ese que tiene fecha de hoy, debería tener otro cartel; por default fecha rto = fecha FAC, que el operador la cambie»). Al conciliar una factura, dos PROPUESTAS (nada automático): (1) fechar el remito como la factura si es MÁS DE UN DÍA POSTERIOR a ella;
(2) pasar a Cumplido el pedido que quedó completo (remitido y facturado, remitos que no esperan retiro). `GET /ingesta/facturas/{id}/proximos-pasos` es de solo lectura; las acciones usan lo que ya existe (cambio de fecha del remito, S890; cambio de estado del pedido
con sus guardas). Sobre una COPIA de la base de P del 05/11 10:21 (con la 2612 y la 2622 ya conciliadas, el #98 cerrado, la 2603 sin cargar) y, para el caso del #155, la 2603 REAL de ARCA cargada por contra natura. Parte de pantalla: estática + compilación (Node)."""
import sys, os, sqlite3, subprocess, hashlib, json, glob
from datetime import date
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261105_1021.db"
ARCA = r"Q:\Mi unidad\V5_Silo_Claude\FACTURAS_PDF\ARCA"
T = os.path.join(RAIZ, "scratch", "test_proximos_pasos_tmp.db"); copiar_p(ORIG, T)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
def x(sql, *a):
    con = sqlite3.connect(T); con.execute(sql, a); con.commit(); con.close()
def huella(sql, *a): return hashlib.md5(repr(q(sql, *a)).encode("utf-8")).hexdigest()
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp_214"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
def fid(n): return q("select id from facturas where tipo_comprobante='FACTURA_A' and numero_comprobante=?", n)[0][0]
def pp(n):
    r = cli.get(f"/ingesta/facturas/{fid(n)}/proximos-pasos"); assert r.status_code == 200, (n, r.status_code, r.text[:200]); return r.json()

# ---------- el servidor: qué se propone en cada caso ----------
h0 = tuple(huella(f"select * from {t} order by id") for t in ("facturas", "remitos", "pedidos", "pedidos_items", "remitos_items"))
r2612 = pp(2612)
check("la 2612 (factura 06/10) contra el remito 3035 del 03/11: se propone fechar el remito como la factura (28 días después) y NO Cumplido, porque el #153 ya está Cumplido",
      [(r["numero_legal"], r["dias_despues_de_la_factura"]) for r in r2612["remitos_a_fechar"]] == [("0015-00003035", 28)] and r2612["pedidos_a_cumplir"] == [] and r2612["pedidos"][0]["estado"] == "CUMPLIDO")
r2624 = pp(2624)
p147 = r2624["pedidos"][0]
check("la 2624 del #147 (Honeymax, PENDIENTE): remito 3036 del 03/11 contra factura del 28/10 (6 días: se propone fechar) y el pedido está COMPLETO (316 de 316 remitidos y facturados): se propone pasar a Cumplido, avisando que la salida está solo ASUMIDA",
      [r["dias_despues_de_la_factura"] for r in r2624["remitos_a_fechar"]] == [6] and p147["pedido_id"] == 147 and p147["completo"] and p147["proponer_cumplido"] and p147["salida_asumida"]
      and p147["remitida"] == 316 and p147["pedida"] == 316 and p147["remitos"] == ["0015-00003036"])
r2627 = pp(2627)
check("la 2627 del #150 (Cynthia, 04/11): remito del mismo día (0 días) y pedido completo: NO se propone fecha, sí Cumplido",
      r2627["remitos_a_fechar"] == [] and [p["pedido_id"] for p in r2627["pedidos_a_cumplir"]] == [150])
r2621 = pp(2621)
check("la 2621 (factura 26/10) con el remito 3031 del 20/10, ANTERIOR a la factura (-6 días): es el caso normal (remito primero) y no se toca; el #137 ya está Cumplido",
      r2621["remitos"][0]["dias_despues_de_la_factura"] == -6 and r2621["remitos_a_fechar"] == [] and r2621["pedidos_a_cumplir"] == [])
check("el umbral es «más de un día»: la 2625 con el remito a 1 día no propone fecha; la 2619 con el remito a 2 días sí",
      pp(2625)["remitos_a_fechar"] == [] and [r["dias_despues_de_la_factura"] for r in pp(2619)["remitos_a_fechar"]] == [2])
x("update remitos set flags_estado = flags_estado | ? where numero_legal='0015-00003036'", 1 << 37)
r_dep = pp(2624)["pedidos"][0]
x("update remitos set flags_estado = flags_estado & ~? where numero_legal='0015-00003036'", 1 << 37)
check("un remito EN DEPÓSITO (esperando retiro) impide la propuesta: el pedido no se considera completo", r_dep["en_deposito"] and not r_dep["completo"] and not r_dep["proponer_cumplido"])
ri = q("select ri.id, ri.cantidad_remitida from remitos_items ri join remitos r on r.id=ri.remito_id where r.numero_legal='0015-00003042' limit 1")[0]
x("update remitos_items set cantidad_remitida = cantidad_remitida - 4 where id=?", ri[0])
r_inc = pp(2627)["pedidos"][0]
x("update remitos_items set cantidad_remitida = ? where id=?", ri[1], ri[0])
check("un pedido con algo SIN remitir (80 de 84) no se propone para Cumplido (para eso está el cierre con discrepancia de siempre)", not r_inc["completo"] and not r_inc["proponer_cumplido"] and r_inc["remitida"] == 80)
check("el endpoint es de solo lectura: facturas, remitos, pedidos y renglones idénticos tras todas las consultas",
      tuple(huella(f"select * from {t} order by id") for t in ("facturas", "remitos", "pedidos", "pedidos_items", "remitos_items")) == h0)
check("una factura inexistente es 404", cli.get("/ingesta/facturas/00000000000000000000000000000000/proximos-pasos").status_code == 404)

# ---------- el caso del #155: la 2603 real por contra natura ----------
f2603 = glob.glob(os.path.join(ARCA, "30715603973_001_00001_00002603*.pdf"))
rr = cli.post("/ingesta/raw", files={"file": (os.path.basename(f2603[0]), open(f2603[0], "rb").read(), "application/pdf")}) if f2603 else None
rid = rr.json()["id"] if rr is not None and rr.status_code == 200 else None
ev = cli.post(f"/ingesta/raw/{rid}/contra-natura/evaluar", json={}).json() if rid else {}
transporte = q("select id from empresas_transporte limit 1")[0][0]
producto = q("select id from productos where nombre like 'Surgizime E2 bid%5 litros%' limit 1")[0][0]
body = {"cliente_id": ev.get("cliente_id"), "domicilio_entrega_id": ev.get("domicilio_entrega_id"), "transporte_id": transporte,
        "productos": [{"item_pdf": r["item_pdf"], "producto_id": producto} for r in ev.get("renglones", [])]}
ev2 = cli.post(f"/ingesta/raw/{rid}/contra-natura/evaluar", json=body).json() if rid else {}
conf = cli.post(f"/ingesta/raw/{rid}/contra-natura/confirmar", json=body) if rid else None
res = conf.json() if conf is not None and conf.status_code == 200 else {}
check("partida del #155: la 2603 real (Doc Baires, 16/09, sin pedido) se carga por contra natura: el resultado trae la factura, el pedido retroactivo y el remito",
      ev2.get("veredicto") == "RETROACTIVO" and conf is not None and conf.status_code == 200 and res.get("factura_id") and res.get("pedido_id") and res.get("remito_id"))
r155 = cli.get(f"/ingesta/facturas/{res['factura_id']}/proximos-pasos").json() if res.get("factura_id") else {"remitos_a_fechar": [], "pedidos_a_cumplir": [], "remitos": [], "pedidos": []}
check("el PR que arma contra natura NACE SIN NÚMERO NI FECHA (la toma al emitirse): no hay fecha que proponer al conciliar; el pedido retroactivo queda completo (6 de 6, remitido y facturado) con salida asumida: se propone Cumplido, nombrando al «PR sin número»",
      q("select numero_legal from remitos where id=?", res["remito_id"].replace("-", ""))[0][0] is None and r155["remitos"] == [] and r155["remitos_a_fechar"] == []
      and [p["pedido_id"] for p in r155["pedidos_a_cumplir"]] == [res.get("pedido_id")] and r155["pedidos_a_cumplir"][0]["pedida"] == 6 and r155["pedidos_a_cumplir"][0]["salida_asumida"]
      and r155["pedidos_a_cumplir"][0]["remitos"] == ["PR sin número"])
r_c = cli.patch(f"/pedidos/{res['pedido_id']}", json={"estado": "CUMPLIDO"})
r155c = cli.get(f"/ingesta/facturas/{res['factura_id']}/proximos-pasos").json() if res.get("factura_id") else {}
check("«Sí, pasar a Cumplido» (caso #155) usa el cambio de estado de siempre: 200, sin cartel de discrepancia porque el pedido está completo; la propuesta desaparece y con el pedido ya Cumplido no se vuelve a ofrecer",
      r_c.status_code == 200 and q("select estado from pedidos where id=?", res["pedido_id"])[0][0] == "CUMPLIDO" and r155c["pedidos_a_cumplir"] == [])

# ---------- la fecha, sobre un remito NUMERADO cargado después (el 3036 del #147: factura del 28/10, remito del 03/11) ----------
rem = pp(2624)["remitos_a_fechar"][0]
r_f = cli.patch(f"/remitos/{rem['remito_id']}/fecha", json={"fecha": "2026-10-28", "motivo": "Igualada a la fecha de la factura 0001-00002624 al conciliar"})
r24 = pp(2624)
nota = q("select texto from remitos_notas where remito_id=? order by id desc limit 1", rem["remito_id"].replace("-", "")) if r_f.status_code == 200 else []
check("«Sí, poner 28/10» usa el cambio de fecha que ya existe: 200, el remito queda del 28/10, deja la nota [SISTEMA] con la fecha anterior, la nueva y el motivo, y la propuesta de fecha desaparece (la de Cumplido sigue: el #147 está completo)",
      r_f.status_code == 200 and r24["remitos"][0]["fecha"] == "2026-10-28" and r24["remitos_a_fechar"] == [] and len(r24["pedidos_a_cumplir"]) == 1
      and nota and "Fecha del remito cambiada" in nota[0][0] and "03/11/2026" in nota[0][0] and "28/10/2026" in nota[0][0] and "Igualada a la fecha de la factura" in nota[0][0])
r_fut = cli.patch(f"/remitos/{rem['remito_id']}/fecha", json={"fecha": "2999-01-01", "motivo": "prueba"})
check("una fecha a futuro la rechaza el servidor (422 FECHA_FUTURA): el cartel no deja elegirla (max = hoy) y el servidor la ampara", r_fut.status_code == 422 and "FECHA_FUTURA" in r_fut.text)

# ---------- pantalla ----------
SRC = os.path.join(RAIZ, "frontend", "src", "views", "Pedidos")
con = open(os.path.join(SRC, "ConciliarFacturaView.vue"), encoding="utf-8").read().replace("\r\n", "\n")
check("el resultado de conciliar tiene el bloque «Para dejarlo prolijo» con las dos propuestas (cartel de fecha y cartel de Cumplido), solo si hay algo que proponer o ya se hizo algo",
      'data-test="proximos-pasos"' in con and 'data-test="cartel-fecha"' in con and 'data-test="cartel-cumplido"' in con and 'v-if="remitosAFechar.length || pedidosACumplir.length || hechos.length"' in con and "Para dejarlo prolijo" in con)
check("cartel de fecha: «Sí, poner <fecha de la factura>» (por defecto), «otra fecha» (no más allá de hoy) y «Dejar <fecha del remito>»; usa PATCH /remitos/{id}/fecha con motivo automático",
      'data-test="fechar-como-factura"' in con and 'data-test="otra-fecha"' in con and ':max="hoyIso"' in con and 'data-test="dejar-fecha"' in con
      and "api.patch(`/remitos/${r.remito_id}/fecha`, { fecha, motivo })" in con and "'Igualada a la fecha de la factura ' + proximos.factura.numero + ' al conciliar'" in con)
check("cartel de Cumplido: «Sí, pasar a Cumplido» por el cambio de estado de siempre (usePedidoEstado, con sus guardas) y «Ahora no»; si la salida está solo asumida lo dice y el botón destacado pasa a ser «Ahora no»",
      'data-test="pasar-a-cumplido"' in con and "await cambiarEstado(p.pedido_id, 'CUMPLIDO')" in con and 'data-test="ahora-no"' in con and 'data-test="salida-asumida"' in con
      and ":class=\"p.salida_asumida ? 'bg-slate-700" in con and ":class=\"p.salida_asumida ? 'bg-emerald-500" in con)
check("las propuestas se piden al servidor solo cuando hay factura registrada (no para notas de crédito o débito) y si falla la consulta el cartel verde queda como siempre; nada se cambia sin contestar",
      "watch(resultado, (r) => { if (r && !r.facturas_ajustadas && r.factura_id) cargarProximosPasos(r.factura_id) })" in con and "proximos.value = null   // sin las propuestas el cartel verde queda como siempre" in con
      and "/proximos-pasos`)).data" in con)
js = ("const fs = require('fs'); const { createRequire } = require('module'); const req = createRequire('C:/dev/Sonido_Liquido_V5/frontend/package.json');"
      "const { parse, compileTemplate, compileScript } = req('@vue/compiler-sfc'); const out = {};"
      "for (const f of ['Pedidos/ConciliarFacturaView']) { const src = fs.readFileSync('C:/dev/Sonido_Liquido_V5/frontend/src/views/' + f + '.vue', 'utf8');"
      "const { descriptor, errors } = parse(src, { filename: f }); let n = errors.length; if (!n) { n += compileTemplate({ source: descriptor.template.content, filename: f, id: 'x' }).errors.length; compileScript(descriptor, { id: 'x' }); } out[f] = n }"
      "console.log(JSON.stringify(out))")
try:
    rc = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", timeout=120)
    res_js = json.loads(rc.stdout.strip())
except (OSError, ValueError, subprocess.SubprocessError):
    res_js = {}
check("la pantalla de conciliar compila (parseo, plantilla y script) sin errores", res_js == {"Pedidos/ConciliarFacturaView": 0})

for n in os.listdir(os.path.join(RAIZ, "scratch")):
    if n.startswith("test_proximos_pasos_tmp"):
        try: os.remove(os.path.join(RAIZ, "scratch", n))
        except OSError: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
