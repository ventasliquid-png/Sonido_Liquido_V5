r"""S895, Carlos 29/10 (caso Castro #145: vendido, cobrado y entregado sin factura ni remito). El cartel de cierre con discrepancia de un Blanco ofrece «Salió sin papel» por lo que
falta remitir: POST /remitos/pedido/{id}/salida-sin-papel arma UN remito por lo pendiente (pedido menos lo ya remitido) y le da la salida sin papel (número 0015, nota [SISTEMA],
salida confirmada) en un paso; después el Cumplido pasa sin cartel. Sin transportista en el pedido sale como retiro en planta; con transportista, por el del pedido. Sobre una COPIA
de la base de P del 28/10 16:51 (#145 de Castro y #148 de Jofre: Blanco, Pendiente, sin remitos)."""
import sys, os, sqlite3
from _esquema_p import copiar_p, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user, get_current_user_optional
from backend.remitos.constants import RemitoFlags
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
_aparte = imagenes_aparte(r"C:\dev\Sonido_Liquido_V5"); _aparte.__enter__()
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261028_1651.db"
T = os.path.join(RAIZ, "scratch", "test_salida_sin_papel_pedido_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tomy_prueba"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
app.dependency_overrides[get_current_user_optional] = lambda: U()
c = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
def x(sql, *a):
    con = sqlite3.connect(T); con.execute(sql, a); con.commit(); con.close()
B20, B21, B46 = 1 << 20, 1 << 21, 1 << 46
def bits(pid): return int(q("select flags_estado from pedidos where id=?", pid)[0][0])
def remitos(pid): return q("select id, numero_legal, estado, flags_estado, metodo_entrega, transporte_id, fecha_emision from remitos where pedido_id=? and estado!='ANULADO' order by numero_legal", pid)
def renglones(pid): return q("select id, cantidad from pedidos_items where pedido_id=? order by id", pid)

check("partida: #145 (Castro) y #148 (Jofre) son Blanco, PENDIENTE, sin remitos y sin transportista",
      all(q("select estado, (flags_estado>>12)&1, transporte_id from pedidos where id=?", p)[0] == ("PENDIENTE", 0, None) for p in (145, 148)) and not remitos(145) and not remitos(148))
ult = q("select max(numero_legal) from remitos where numero_legal like '0015-%'")[0][0]
proximo = f"0015-{int(ult.split('-')[1]) + 1:08d}"

# ---------- el cartel de siempre ----------
r = c.patch("/pedidos/145", json={"estado": "CUMPLIDO"})
check(f"el Cumplido de #145 sin remitos sigue dando el cartel (409 CIERRE_CON_DISCREPANCIA) [{r.status_code}]", r.status_code == 409 and "CIERRE_CON_DISCREPANCIA" in r.text)

# ---------- el botón, por todo ----------
r = c.post("/remitos/pedido/145/salida-sin-papel", json={})
check(f"POST salida-sin-papel del #145 da 200 [{r.status_code}] {r.text[:150] if r.status_code != 200 else ''}", r.status_code == 200)
fila = remitos(145)
check(f"se creó UN remito, con el próximo 0015 ({proximo}) {[(a[1], a[2], a[4]) for a in fila]}", len(fila) == 1 and fila[0][1] == proximo)
f = int(fila[0][3]) if fila else 0
check("sin transportista en el pedido: retiro en planta (MOSTRADOR), ENTREGADO; salida confirmada (bit 47), emitido, SIN la marca de impreso (bit 44) y con fecha de emisión",
      fila and fila[0][4] == "MOSTRADOR" and fila[0][2] == "ENTREGADO" and f & int(RemitoFlags.SALIDA_CONFIRMADA) and f & int(RemitoFlags.EMITIDO) and not f & int(RemitoFlags.IMPRESO) and fila[0][6])
its = q("select pi.cantidad, ri.cantidad_remitida from remitos_items ri join pedidos_items pi on pi.id=ri.pedido_item_id where ri.remito_id=?", fila[0][0])
check(f"lleva TODO lo pedido, renglón por renglón {its}", len(its) == len(renglones(145)) and all(a == b for a, b in its))
notas = [n[0] for n in q("select texto from remitos_notas where remito_id=?", fila[0][0])]
check(f"rastro: nota [SISTEMA] de «Salió sin papel» con el número, y la de que salió desde el cierre del pedido #145 {[n[:70] for n in notas]}",
      any(n.startswith("[SISTEMA] Salió sin papel") and proximo in n and "Salida registrada desde el cierre del pedido #145" in n for n in notas))
check("el pedido quedó con la entrega completa (bit 21), sin entrega parcial (bit 20), todavía PENDIENTE", bits(145) & B21 and not bits(145) & B20 and q("select estado from pedidos where id=145")[0][0] == "PENDIENTE")
r = c.patch("/pedidos/145", json={"estado": "CUMPLIDO"})
check(f"ahora el Cumplido pasa sin cartel y sin cierre_confirmado [{r.status_code}], sin la marca de cierre con ajuste (bit 46)",
      r.status_code == 200 and q("select estado from pedidos where id=145")[0][0] == "CUMPLIDO" and not bits(145) & B46)
r = c.post("/remitos/pedido/145/salida-sin-papel", json={})
check(f"repetir el botón no duplica nada: 409 NADA_PENDIENTE [{r.status_code}], sigue UN remito", r.status_code == 409 and "NADA_PENDIENTE" in r.text and len(remitos(145)) == 1)

# ---------- parcial: solo lo que falta ----------
ren = renglones(148)
r1 = c.post("/remitos/armar", json={"pedido_id": 148, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": ren[0][0], "cantidad": 1}]})
check(f"partida parcial: se arma a mano 1 unidad del primer renglón de #148 [{r1.status_code}]", r1.status_code == 200 and bits(148) & B20)
r = c.post("/remitos/pedido/148/salida-sin-papel", json={"motivo": "lo retiró el cliente"})
check(f"el botón del #148 da 200 [{r.status_code}]", r.status_code == 200)
nuevo = [a for a in remitos(148) if a[1]]
check(f"solo el remito del botón tiene número; el armado a mano sigue sin él {[(a[1], a[2]) for a in remitos(148)]}", len(remitos(148)) == 2 and len(nuevo) == 1)
its = dict(q("select ri.pedido_item_id, ri.cantidad_remitida from remitos_items ri where ri.remito_id=?", nuevo[0][0]))
falta = {ren[0][0]: ren[0][1] - 1, **{rid: cant for rid, cant in ren[1:]}}
check(f"lleva lo que faltaba (el primer renglón menos 1, el resto completo) {its}", {k: round(v, 3) for k, v in its.items()} == {k: round(v, 3) for k, v in falta.items()})
check("el motivo escrito viaja en la nota del remito",
      any("lo retiró el cliente" in n[0] for n in q("select texto from remitos_notas where remito_id=?", nuevo[0][0])))
check("el pedido quedó con la entrega completa (bit 21) y sin parcial (bit 20)", bits(148) & B21 and not bits(148) & B20)

# ---------- con transportista ----------
cand = q("select p.id, p.domicilio_entrega_id from pedidos p where (p.flags_estado>>12)&1=0 and p.estado='PENDIENTE' and p.domicilio_entrega_id is not null and p.id not in (145,148) "
         "and not exists(select 1 from remitos r where r.pedido_id=p.id) and exists(select 1 from pedidos_items i where i.pedido_id=p.id) order by p.id limit 1")
tr = q("select id from empresas_transporte limit 1")
if cand and tr:
    pid = cand[0][0]; x("update pedidos set transporte_id=? where id=?", tr[0][0], pid)
    r = c.post(f"/remitos/pedido/{pid}/salida-sin-papel", json={})
    fila = remitos(pid)
    check(f"con transportista en el pedido (#{pid}): sale por el transporte del pedido, sin método de mostrador, y toma número [{r.status_code}]",
          r.status_code == 200 and len(fila) == 1 and fila[0][1] and fila[0][4] is None and fila[0][5] == tr[0][0])
else:
    check("(sin pedido candidato con domicilio para la prueba del transportista)", False)

# ---------- guardas ----------
check("pedido inexistente: 404", c.post("/remitos/pedido/999999/salida-sin-papel", json={}).status_code == 404)
x("update pedidos set flags_estado = flags_estado | ? where id = ?", 1 << 5 if False else int(__import__("backend.pedidos.constants", fromlist=["PedidoFlags"]).PedidoFlags.ES_ANULADO), 144)
r = c.post("/remitos/pedido/144/salida-sin-papel", json={})
check(f"pedido anulado: 409 PEDIDO_ANULADO [{r.status_code}]", r.status_code == 409 and "PEDIDO_ANULADO" in r.text)
r = c.post("/remitos/pedido/141/salida-sin-papel", json={})
rosa = remitos(141)
check(f"un Rosa también puede salir con un 0015: queda dicho en el remito que no se factura [{r.status_code}]",
      r.status_code == 200 and rosa and int(rosa[0][3]) & int(RemitoFlags.CIRCUITO_ROSA)
      and any("factur" in n[0].lower() for n in q("select texto from remitos_notas where remito_id=?", rosa[0][0])))

# ---------- el «Salió sin papel» de siempre, sin cambios ----------
libre = q("select p.id, p.domicilio_entrega_id from pedidos p where (p.flags_estado>>12)&1=0 and p.estado='PENDIENTE' and p.id not in (144, 145, 148) and p.transporte_id is null "
          "and not exists(select 1 from remitos r where r.pedido_id=p.id) and exists(select 1 from pedidos_items i where i.pedido_id=p.id and i.cantidad>=1) order by p.id limit 1")
pl = libre[0][0] if libre else 0
r = c.post("/remitos/armar", json={"pedido_id": pl, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": renglones(pl)[0][0], "cantidad": 1}]}) if pl else None
rid = r.json().get("id") if r is not None and r.status_code == 200 else None
r = c.post(f"/remitos/{rid}/salida-sin-papel", json={"motivo": "prueba"}) if rid else None
rid_db = q("select id from remitos where numero_legal=?", r.json().get("numero_legal"))[0][0] if r is not None and r.status_code == 200 else None
check(f"«Salió sin papel» de un remito suelto sigue igual: número 0015, salida confirmada, nota con el motivo [{r.status_code if r is not None else '-'}]",
      r is not None and r.status_code == 200 and (r.json().get("numero_legal") or "").startswith("0015-")
      and any("Motivo: prueba" in n[0] for n in q("select texto from remitos_notas where remito_id=?", rid_db)))
r = c.post(f"/remitos/{rid}/salida-sin-papel", json={}) if rid else None
check(f"y repetirlo da 409 REMITO_CON_NUMERO [{r.status_code if r is not None else '-'}]", r is not None and r.status_code == 409 and "REMITO_CON_NUMERO" in r.text)

# ---------- pantalla (estática): los tres lugares del cartel usan la misma resolución ----------
def leer(rel): return open(os.path.join(RAIZ, "frontend", "src", rel), encoding="utf-8").read()
comp, insp, lista = leer(r"composables\usePedidoEstado.js"), leer(r"views\Pedidos\PedidoInspector.vue"), leer(r"views\Pedidos\PedidoList.vue")
check("el composable ofrece «Salió sin papel» (POST /remitos/pedido/{id}/salida-sin-papel) antes del cierre con discrepancia, y lo usa su propio cambiarEstado",
      "/remitos/pedido/${pedidoId}/salida-sin-papel" in comp and "export async function resolverCierreConDiscrepancia" in comp and "await resolverCierreConDiscrepancia(" in comp)
check("la ficha del pedido y el Tablero importan y usan la misma resolución, y ya no tienen su confirm() propio del cartel",
      all("import { resolverCierreConDiscrepancia }" in s and "await resolverCierreConDiscrepancia(" in s and "confirm(`⚠️ ${mensaje}`)" not in s for s in (insp, lista)))
check("tras registrar la salida se reenvía el estado SIN cierre_confirmado; solo «cerrar igual» lo manda",
      all("accion === 'cerrar' ?" in s for s in (comp, insp, lista)))

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
_aparte.__exit__(None, None, None)
try: os.remove(T)
except OSError: pass
sys.exit(1 if falla else 0)
