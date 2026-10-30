r"""S896, Carlos 30/10. Dos arreglos chicos.
(1) «El sistema, al ponerle Consumidor Final el operador, le asigna 11111111119 y eso hace que el cliente nazca Blanco y ya no se puede volver a Rosa. El sistema
fuerza el CUIT y no debe hacerlo si el operador lo deja en blanco.» El respaldo del servidor (_apply_cf_cuit_fallback) y el reloj de la ficha (ClientCanvas.vue)
escribían el CUIT comodín en un Consumidor Final sin CUIT. Se retiraron: lo que queda en blanco queda en blanco (Nike S894: el CUIT comodín de CF no se guarda en la ficha).
(2) Opción A del bit 46 (CIERRE_CON_AJUSTE): reabrir un pedido cerrado con ajuste NO apaga la marca (cicatriz de Nike, S863), pero deja una nota [SISTEMA] que lo dice.
Sobre una COPIA de la base de P del 29/10 18:21."""
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
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_20261029_1821.db"
T = os.path.join(RAIZ, "scratch", "test_cf_sin_cuit_tmp.db"); copiar_p(ORIG, T)
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
B4, B19, B46 = 1 << 4, 1 << 19, 1 << 46
CF = q("select id from condiciones_iva where upper(nombre) like '%CONSUMIDOR FINAL%' limit 1")[0][0]
RI = q("select id from condiciones_iva where upper(nombre) like '%RESPONSABLE INSCRIPTO%' limit 1")[0][0]
LISTA = q("select id from listas_precios limit 1")[0][0]
SEG = q("select id from segmentos where upper(nombre) not like '%CONSUMIDOR%' limit 1")[0][0]
def hex_(i): return i.replace("-", "")

# ---------- (1) el CUIT en blanco queda en blanco ----------
def alta(nombre, **kw):
    body = {"razon_social": nombre, "flags_estado": 3, "condicion_iva_id": CF, "lista_precios_id": LISTA, "segmento_id": SEG, "domicilios": [], "vinculos": []}
    body.update(kw)
    return c.post("/clientes/", json=body)
r = alta("PRUEBA S896 ROSA NUEVA")
fila = q("select cuit, flags_estado from clientes where razon_social='PRUEBA S896 ROSA NUEVA'")
check(f"alta con condición Consumidor Final y CUIT vacío [{r.status_code}]: el CUIT queda vacío (antes se escribía 11111111119)", r.status_code in (200, 201) and fila and not fila[0][0])
r = alta("MOSTRADOR")
fila = q("select cuit from clientes where razon_social='MOSTRADOR' and id != (select id from clientes where cuit='00000000000' limit 1)") if q("select 1 from clientes where cuit='00000000000'") else q("select cuit from clientes where razon_social='MOSTRADOR'")
check(f"y un «MOSTRADOR» nuevo sin CUIT tampoco se queda con el 00000000000 (ese lo carga quien lo escribe) [{r.status_code}]", all(not f[0] for f in fila))

# ---------- el cliente sin CUIT conserva la salida a Rosa ----------
cid = q("select id from clientes where razon_social='PRUEBA S896 ROSA NUEVA'")[0][0]
r = c.put(f"/clientes/{cid}", json={"condicion_iva_id": RI})
f = q("select cuit, flags_estado from clientes where id=?", cid)[0]
check(f"al sacarle la condición Consumidor Final (sin CUIT) vuelve a poder ser Rosa: sello Rosa inferido, CUIT todavía vacío [{r.status_code}] ({f[1]})",
      r.status_code == 200 and not f[0] and int(f[1]) & B4)

# ---------- el código ya no escribe el comodín ----------
serv = open(os.path.join(RAIZ, "backend", "clientes", "service.py"), encoding="utf-8").read()
canvas = open(os.path.join(RAIZ, "frontend", "src", "views", "Hawe", "ClientCanvas.vue"), encoding="utf-8").read()
check("el servidor ya no tiene el respaldo que escribía el CUIT comodín", "_apply_cf_cuit_fallback" not in serv)
check("la ficha ya no escribe el CUIT al elegir Consumidor Final (el reloj de condicion_iva_id retiró la asignación)",
      "form.value.cuit = esVentaAnonima" not in canvas and "[S896, Carlos 30/10] Antes, al elegir la condición de IVA" in canvas)
check("pero sigue valiendo lo que el operador escribe a mano: el 00000000000 tipeado fija CF y segmento", "if (newCuit === '00000000000') {" in canvas)

# ---------- (2) reabrir un pedido cerrado con ajuste ----------
cand = q("select id, flags_estado from pedidos where (flags_estado & ?) != 0 and (flags_estado & ?) != 0 order by id limit 1", B46, 1 << 34)
if not cand:
    pid0 = q("select id from pedidos where (flags_estado & ?) != 0 and (flags_estado & ?) = 0 order by id limit 1", 1 << 34, B46)[0][0]
    con = sqlite3.connect(T); con.execute("update pedidos set flags_estado = flags_estado | ? where id=?", (B46, pid0)); con.commit(); con.close()
    cand = q("select id, flags_estado from pedidos where id=?", pid0)
pid = cand[0][0]
nota0 = q("select nota from pedidos where id=?", pid)[0][0] or ""
check(f"partida: el pedido #{pid} está Cumplido y con el bit 46 prendido", int(cand[0][1]) & B46 and int(cand[0][1]) & (1 << 34))
r = c.patch(f"/pedidos/{pid}", json={"estado": "Pendiente"})
f, nota1 = q("select flags_estado, nota from pedidos where id=?", pid)[0]
check(f"al reabrirlo (Pendiente) [{r.status_code}]: el bit 46 NO se apaga (cicatriz de Nike)", r.status_code == 200 and int(f) & B46 and not int(f) & (1 << 34))
check("y la nota recibe la línea [SISTEMA] que dice que el cierre anterior con ajuste queda como historia",
      "[SISTEMA] El pedido salió de Cumplido (Pendiente). El cierre anterior con ajuste queda como historia" in (nota1 or "") and (nota1 or "").startswith(nota0))
n_antes = (nota1 or "").count("salió de Cumplido")
r = c.patch(f"/pedidos/{pid}", json={"estado": "Pendiente"})
check("guardar otra vez en Pendiente no repite la línea", (q("select nota from pedidos where id=?", pid)[0][0] or "").count("salió de Cumplido") == n_antes)

libre = q("select id from pedidos where (flags_estado & ?) = 0 and (flags_estado & ?) != 0 limit 1", B46, 1 << 34)
if libre:
    r = c.patch(f"/pedidos/{libre[0][0]}", json={"estado": "Pendiente"})
    check(f"un pedido Cumplido SIN marca de ajuste reabre sin la línea nueva [{r.status_code}]", r.status_code == 200 and "salió de Cumplido" not in (q("select nota from pedidos where id=?", libre[0][0])[0][0] or ""))

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
try: os.remove(T)
except OSError: pass
sys.exit(1 if falla else 0)
