r"""S897, Carlos 02/11 (Card #209). «Cuando es Rosa, el precio es el precio... Si un pedido pasa de Blanco a Rosa no se debe tocar el unitario; lo único que hay que hacer es dar el total
como la suma de los totales sin impuestos. La alternancia Rosa/Blanco ad infinitum solo varía el total general: +21% (Blanco) o el neto (Rosa). Los renglones no se deben tocar nunca.»
Reemplaza a test_conversion_circuito_s895 (la conversión «conservando el total», x 1,21 / ÷ 1,21 sobre los renglones, se quitó: dejó el precio 9.586,78 = 11.600 / 1,21 en el pedido #151 de Centro Pet).
PATCH /pedidos/{id}/circuito-bipolar solo cambia el bit de circuito y el total (Blanco = suma de subtotales menos el descuento global, x 1,21; Rosa = lo mismo sin el 1,21), sin tocar nunca
precio, descuento en porcentaje, descuento en pesos ni subtotal de los renglones. Se corre dos veces, con la sesión de producción (autoflush=False, backend/core/database.py) y con la de las pruebas
(autoflush=True): con la primera, el total que devolvía el servidor salía de los renglones viejos. Sobre una COPIA de la base de P del 28/10 16:51."""
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
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261028_1651.db"
class U: id = 1; username = "prueba"; is_active = True
app.dependency_overrides[get_current_active_user] = lambda: U()
app.dependency_overrides[get_current_user_optional] = lambda: U()

def correr(autoflush):
    tag = "producción (autoflush=False)" if not autoflush else "pruebas (autoflush=True)"
    T = os.path.join(RAIZ, "scratch", f"test_circuito_renglones_{'af' if autoflush else 'sf'}_tmp.db"); copiar_p(ORIG, T)
    S = sessionmaker(bind=create_engine(f"sqlite:///{T}"), autoflush=autoflush)
    def ov():
        db = S()
        try: yield db
        finally: db.close()
    app.dependency_overrides[get_db] = ov
    c = TestClient(app, raise_server_exceptions=False)
    def q(sql, *a):
        con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v
    def x(sql, *a):
        con = sqlite3.connect(T); con.execute(sql, a); con.commit(); con.close()
    def renglones(pid): return q("select id, producto_id, cantidad, precio_unitario, descuento_porcentaje, descuento_importe, subtotal from pedidos_items where pedido_id=? order by id", pid)
    def total(pid): return round(q("select total from pedidos where id=?", pid)[0][0], 2)
    def glob(pid): return round(q("select coalesce(descuento_global_importe,0) from pedidos where id=?", pid)[0][0], 2)
    def rosa(pid): return int(q("select (flags_estado>>12)&1 from pedidos where id=?", pid)[0][0])
    def notas(pid): return q("select nota from pedidos where id=?", pid)[0][0] or ""
    def neto(pid): return round(sum(r[6] for r in renglones(pid)) - glob(pid), 2)
    def circuito(pid, a_rosa, **extra): return c.patch(f"/pedidos/{pid}/circuito-bipolar", json={"is_interno": a_rosa, **extra})

    # ---------- Castro #145: alternar muchas veces ----------
    base = renglones(145)
    check(f"[{tag}] partida: #145 (Castro) es Blanco, 6 x 45.800 + 6 x 12.100, total 420.354 con IVA",
          rosa(145) == 0 and [r[3] for r in base] == [45800.0, 12100.0] and total(145) == 420354.0)
    ok = True; detalle = ""
    for i in range(1, 9):   # Rosa, Blanco, Rosa, Blanco... ocho veces; las pares mandan además el viejo conservar_total, que se ignora
        a_rosa = (i % 2 == 1)
        r = circuito(145, a_rosa, **({"conservar_total": True} if i % 2 == 0 else {}))
        esperado = round(neto(145), 2) if a_rosa else round(neto(145) * 1.21, 2)
        if not (r.status_code == 200 and rosa(145) == int(a_rosa) and renglones(145) == base and total(145) == esperado and r.json().get("total") == esperado):
            ok = False; detalle = f"vuelta {i}: status {r.status_code}, rosa={rosa(145)}, total={total(145)} (esperado {esperado}), respuesta={r.json().get('total') if r.status_code == 200 else r.text[:80]}"; break
    check(f"[{tag}] ocho cambios de circuito seguidos: los renglones quedan idénticos y el total es 347.400 (Rosa) o 420.354 (Blanco) siempre, también en la respuesta del servidor {detalle}", ok)
    check(f"[{tag}] el pedido termina Blanco con el total de origen y sin nota [SISTEMA] de conversión", rosa(145) == 0 and total(145) == 420354.0 and "Circuito pasado" not in notas(145) and "conservando el total" not in notas(145))

    # ---------- con descuentos ----------
    x("update pedidos_items set descuento_porcentaje=0, descuento_importe=1000, subtotal=cantidad*precio_unitario-1000 where id=(select min(id) from pedidos_items where pedido_id=145)")
    x("update pedidos set descuento_global_importe=500 where id=145")
    circuito(145, False)   # recalcula el total con los descuentos
    base_d = renglones(145); glob_d = glob(145)
    check(f"[{tag}] con descuento en un renglón (1.000) y global (500): Blanco = (347.400 - 1.500) x 1,21 = {round(neto(145) * 1.21, 2)}", total(145) == round((347400 - 1000 - 500) * 1.21, 2))
    r1 = circuito(145, True); t_rosa = total(145)
    r2 = circuito(145, False, conservar_total=True); t_blanco = total(145)
    check(f"[{tag}] con descuentos, a Rosa y de vuelta: los descuentos (renglón y global) y los precios no se tocan; Rosa = neto {t_rosa}, Blanco = neto x 1,21 {t_blanco}",
          r1.status_code == 200 and r2.status_code == 200 and renglones(145) == base_d and glob(145) == glob_d == 500.0 and t_rosa == 345900.0 and t_blanco == round(345900.0 * 1.21, 2))

    # ---------- el caso de Centro Pet (#151): clon de #111, Rosa y de vuelta a Blanco aceptando el viejo «conservar el total» ----------
    nid = c.post("/pedidos/111/clone").json()["id"]
    base_c = renglones(nid); t_c = total(nid)
    circuito(nid, True)                             # CANCELAR: solo cambia el circuito
    circuito(nid, False, conservar_total=True)      # ACEPTAR en el cartel viejo
    check(f"[{tag}] Centro Pet: clon de #111 a Rosa y de vuelta a Blanco con el viejo «conservar_total»: el renglón sigue en 360 x 11.600 (antes quedaba en 9.586,78) y el total vuelve a {t_c:,.2f}",
          renglones(nid) == base_c and base_c[0][3] == 11600.0 and total(nid) == t_c and "Circuito pasado" not in notas(nid))

    # ---------- pedido con factura: cambia el circuito y los renglones (la evidencia de lo facturado) siguen igual ----------
    pid_f = q("select p.id from pedidos p where (p.flags_estado>>12)&1=0 and exists(select 1 from facturas f where f.pedido_id=p.id) order by p.id limit 1")[0][0]
    base_f = renglones(pid_f)
    r = circuito(pid_f, True, conservar_total=True)
    check(f"[{tag}] pedido con factura (#{pid_f}): ya no hay 409 por el viejo conservar_total; cambia el circuito y los renglones no se tocan [{r.status_code}]", r.status_code == 200 and rosa(pid_f) == 1 and renglones(pid_f) == base_f)

    # ---------- cliente Rosa de ley que pide Blanco ----------
    cli_rosa = q("select p.id from pedidos p join clientes c on c.id=p.cliente_id where (c.flags_estado>>4)&1=1 and (p.flags_estado>>12)&1=1 and not exists(select 1 from facturas f where f.pedido_id=p.id) order by p.id limit 1")
    if cli_rosa:
        pr = cli_rosa[0][0]; base_r = renglones(pr)
        r = circuito(pr, False, conservar_total=True)
        check(f"[{tag}] un cliente Rosa de ley (#{pr}) que pide Blanco sigue Rosa y sus renglones no se tocan [{r.status_code}]", r.status_code == 200 and rosa(pr) == 1 and renglones(pr) == base_r)
    else:
        check(f"[{tag}] (sin pedido de cliente Rosa para la prueba)", False)
    try: os.remove(T)
    except OSError: pass

correr(False)
correr(True)

# ---------- código (estático) ----------
def leer(*p): return open(os.path.join(RAIZ, *p), encoding="utf-8").read()
router = leer("backend", "pedidos", "router.py")
check("el servidor ya no tiene la conversión: sin conservar_total como campo, sin IVA_FACTOR ni la nota «Circuito pasado de»",
      "conservar_total:" not in router and "IVA_FACTOR" not in router and "Circuito pasado de" not in router and "convertir" not in router.split("def toggle_circuito_bipolar")[1].split("@router.patch(\"/{pedido_id}/no-comercial\"")[0])
check("y calcula el total desde los renglones en memoria, no con una suma en la base (que con autoflush=False veía los viejos)",
      "items_neto = sum((it.subtotal or 0.0) for it in pedido.items)" in router.split("def toggle_circuito_bipolar")[1].split("@router.patch(\"/{pedido_id}/no-comercial\"")[0])
check("la pregunta «¿Conservar el total?» ya no existe: el ayudante conservarTotal.js se quitó", not os.path.exists(os.path.join(RAIZ, "frontend", "src", "utils", "conservarTotal.js")))
for nombre, rel in (("la ficha del pedido", ("views", "Ventas", "PedidoCanvas.vue")), ("el Tablero", ("views", "Pedidos", "PedidoList.vue")), ("los informes", ("components", "informes", "CircuitoEditable.vue"))):
    s = leer("frontend", "src", *rel)
    check(f"{nombre} no pregunta ni manda conservar_total: el PATCH lleva solo is_interno", "preguntarConservarTotal" not in s and "conservarTotal" not in s and "conservar_total" not in s and "circuito-bipolar`, { is_interno:" in s)
canvas = leer("frontend", "src", "views", "Ventas", "PedidoCanvas.vue")
check("la ficha del pedido ya no vuelve a leer los renglones tras cambiar el circuito (no cambian)", "else if (conservar)" not in canvas and "Circuito cambiado conservando el total" not in canvas)

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
