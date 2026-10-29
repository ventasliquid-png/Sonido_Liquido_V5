r"""S895, Carlos 29/10 (caso Castro #145: cobrado con IVA y sin factura; si después pide la factura hay que volver a Blanco). Los precios del pedido son netos: el Blanco suma el IVA
(x 1,21) al total y el Rosa no, así que cambiar de circuito cambia el total. PATCH /pedidos/{id}/circuito-bipolar con conservar_total=true multiplica los precios (y los
descuentos en pesos) por 1,21 al pasar a Rosa y los divide por 1,21 al pasar a Blanco, de modo que lo cobrado no cambie, y deja una nota [SISTEMA]. Sin el pedido, nada cambia
(el comportamiento de siempre). Un pedido con factura no se convierte (sus precios son la evidencia). Sobre una COPIA de la base de P del 28/10 16:51."""
import sys, os, sqlite3
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user, get_current_user_optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261028_1651.db"
T = os.path.join(RAIZ, "scratch", "test_conversion_circuito_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "prueba"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
app.dependency_overrides[get_current_user_optional] = lambda: U()
c = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
def x(sql, *a):
    con = sqlite3.connect(T); con.execute(sql, a); con.commit(); con.close()
def precios(pid): return [(round(a, 2), round(b, 2)) for a, b in q("select precio_unitario, subtotal from pedidos_items where pedido_id=? order by id", pid)]
def total(pid): return round(q("select total from pedidos where id=?", pid)[0][0], 2)
def rosa(pid): return int(q("select (flags_estado>>12)&1 from pedidos where id=?", pid)[0][0])
def notas(pid): return q("select nota from pedidos where id=?", pid)[0][0] or ""
def circuito(pid, a_rosa, conservar=None):
    body = {"is_interno": a_rosa}
    if conservar is not None: body["conservar_total"] = conservar
    return c.patch(f"/pedidos/{pid}/circuito-bipolar", json=body)

check("partida: #145 (Castro) es Blanco, 6 x 45.800 + 6 x 12.100, total 420.354 con IVA",
      rosa(145) == 0 and [p for p, _ in precios(145)] == [45800.0, 12100.0] and total(145) == 420354.0)

# ---------- sin conservar: lo de siempre ----------
r = circuito(145, True)
check(f"sin conservar_total: pasa a Rosa, los precios NO se tocan y el total pierde el IVA (347.400) [{r.status_code}]",
      r.status_code == 200 and rosa(145) == 1 and [p for p, _ in precios(145)] == [45800.0, 12100.0] and total(145) == 347400.0 and "conservando el total" not in notas(145))
circuito(145, False)
check("y de vuelta a Blanco sin conservar: total 420.354 otra vez, precios iguales", rosa(145) == 0 and total(145) == 420354.0 and [p for p, _ in precios(145)] == [45800.0, 12100.0])

# ---------- conservando: Blanco -> Rosa ----------
r = circuito(145, True, True)
check(f"conservar_total a Rosa [{r.status_code}]: precios x 1,21 (55.418 y 14.641), el total sigue en 420.354", r.status_code == 200 and rosa(145) == 1
      and [p for p, _ in precios(145)] == [55418.0, 14641.0] and total(145) == 420354.0)
check("los subtotales de los renglones acompañan (6 x precio nuevo) y suman el total", [s for _, s in precios(145)] == [332508.0, 87846.0] and round(sum(s for _, s in precios(145)), 2) == 420354.0)
check("la nota [SISTEMA] del pedido dice el sentido, el total de antes y el de ahora",
      "[SISTEMA] Circuito pasado de Blanco a Rosa (precios x 1,21, IVA incluido) conservando el total: antes 420,354.00, ahora 420,354.00." in notas(145))

# ---------- conservando: Rosa -> Blanco (el camino de vuelta) ----------
r = circuito(145, False, True)
check(f"conservar_total de vuelta a Blanco [{r.status_code}]: precios / 1,21 = los originales (45.800 y 12.100) y total 420.354 (no 508.628)",
      r.status_code == 200 and rosa(145) == 0 and [p for p, _ in precios(145)] == [45800.0, 12100.0] and total(145) == 420354.0)
check("el ida y vuelta es exacto: subtotales originales y dos notas [SISTEMA] (una por sentido)",
      [s for _, s in precios(145)] == [274800.0, 72600.0] and notas(145).count("conservando el total") == 2 and "Rosa a Blanco (precios / 1,21, IVA discriminado)" in notas(145))

# ---------- descuentos ----------
x("update pedidos_items set descuento_importe=1000, subtotal=cantidad*precio_unitario-1000 where pedido_id=145 and id=(select min(id) from pedidos_items where pedido_id=145)")
x("update pedidos set descuento_global_importe=500 where id=145")
con_dto = (total(145), )
circuito(145, False)   # no-op de circuito: recalcula el total con el descuento
antes = total(145)
r = circuito(145, True, True)
despues = total(145)
d_item = q("select descuento_importe from pedidos_items where pedido_id=145 order by id")[0][0]
check(f"con descuentos: el del renglón (1.000 -> 1.210) y el global (500 -> 605) escalan y el total se conserva ({antes} -> {despues}) [{r.status_code}]",
      r.status_code == 200 and round(d_item, 2) == 1210.0 and round(q("select descuento_global_importe from pedidos where id=145")[0][0], 2) == 605.0 and abs(antes - despues) <= 0.05)
circuito(145, False, True)
check("y de vuelta, los descuentos regresan a 1.000 y 500", round(q("select descuento_importe from pedidos_items where pedido_id=145 order by id")[0][0], 2) == 1000.0
      and round(q("select descuento_global_importe from pedidos where id=145")[0][0], 2) == 500.0 and abs(total(145) - antes) <= 0.05)

# ---------- guardas ----------
con = q("select p.id, p.total from pedidos p where (p.flags_estado>>12)&1=0 and exists(select 1 from facturas f where f.pedido_id=p.id) order by p.id limit 1")
pid_f, t_f = con[0]; ps_f = precios(pid_f)
r = circuito(pid_f, True, True)
check(f"pedido con factura (#{pid_f}): conservar_total da 409 PEDIDO_FACTURADO y no toca nada [{r.status_code}]",
      r.status_code == 409 and "PEDIDO_FACTURADO" in r.text and rosa(pid_f) == 0 and precios(pid_f) == ps_f and round(q("select total from pedidos where id=?", pid_f)[0][0], 2) == round(t_f, 2))
r = circuito(pid_f, True)
check(f"el mismo pedido SIN conservar_total sigue pudiendo cambiar de circuito, como siempre [{r.status_code}]", r.status_code == 200 and rosa(pid_f) == 1 and precios(pid_f) == ps_f)

cli_rosa = q("select p.id from pedidos p join clientes c on c.id=p.cliente_id where (c.flags_estado>>4)&1=1 and (p.flags_estado>>12)&1=1 and not exists(select 1 from facturas f where f.pedido_id=p.id) order by p.id limit 1")
if cli_rosa:
    pr = cli_rosa[0][0]; ps_r = precios(pr)
    r = circuito(pr, False, True)
    check(f"un cliente Rosa de ley (#{pr}) que pide Blanco sigue Rosa: el circuito no cambia, así que los precios tampoco [{r.status_code}]", r.status_code == 200 and rosa(pr) == 1 and precios(pr) == ps_r)
else:
    check("(sin pedido de cliente Rosa para la prueba)", False)

# ---------- pantalla (estática) ----------
def leer(rel): return open(os.path.join(RAIZ, "frontend", "src", rel), encoding="utf-8").read()
util = leer(r"utils\conservarTotal.js")
check("el ayudante pregunta si conservar el total y dice qué hace cada botón (multiplica / divide por 1,21)",
      "export function preguntarConservarTotal" in util and "multiplican por 1,21" in util and "dividen por 1,21" in util and "ACEPTAR" in util and "CANCELAR" in util)
for nombre, rel in (("la ficha del pedido", r"views\Ventas\PedidoCanvas.vue"), ("el Tablero", r"views\Pedidos\PedidoList.vue"), ("los informes", r"components\informes\CircuitoEditable.vue")):
    s = leer(rel)
    check(f"{nombre} importa el ayudante, lo pregunta y manda conservar_total al servidor",
          "import { preguntarConservarTotal } from '@/utils/conservarTotal'" in s and "preguntarConservarTotal(" in s and "conservar_total: conservar" in s)
canvas = leer(r"views\Ventas\PedidoCanvas.vue")
check("la ficha del pedido solo pregunta si no hay cambios sin guardar, y vuelve a leer los renglones si el servidor convirtió",
      "!hayCambiosSinGuardar() && Number(totalFinal.value) > 0" in canvas and "else if (conservar) {" in canvas and "await loadPedido(pid)" in canvas)

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
try: os.remove(T)
except OSError: pass
sys.exit(1 if falla else 0)
