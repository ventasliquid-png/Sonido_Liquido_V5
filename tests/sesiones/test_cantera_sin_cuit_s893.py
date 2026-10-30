r"""S893, Tomy 26/10 (producción): buscó «Ceretti 2098», que existe en Cantera, y no pudo ponerlo en un pedido: POST /bridge/clientes/{id}/import devolvía 500 y la pantalla un genérico «Error al importar
cliente desde Cantera». Causa: Cantera guarda el CUIT «00000000000» cuando el cliente viejo no tenía CUIT (82 de sus 135 clientes). Ese número es exclusivo del Mostrador/Genérico (Nike 806), así que
create_cliente lo rechazaba («CUIT reservado») y la importación fallaba SIEMPRE para esos 82. Ahora esos clientes se importan sin CUIT (el alta ya sabe qué hacer con un cliente sin CUIT), un freno del
alta (duplicado, CUIT reservado) llega con su mensaje y su código 400 en vez de un 500, y la pantalla muestra el motivo. Sobre una COPIA de P y el espejo de Cantera de D."""
import sys, os, shutil, sqlite3, glob, json, io
from _esquema_p import asegurar_esquema
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_*.db"))[-1]
TMP = os.path.join(RAIZ, "scratch", "test_cantera_sin_cuit_s893"); os.makedirs(TMP, exist_ok=True)
T = os.path.join(TMP, "P.db"); shutil.copyfile(ORIG, T); asegurar_esquema(T)
def q(sql, *a):
    con = sqlite3.connect(T); x = con.execute(sql, a).fetchall(); con.commit(); con.close(); return x

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

espejo = json.load(io.open("backend/data/json_mirror/clientes.json", encoding="utf-8"))
espejo = espejo if isinstance(espejo, list) else (espejo.get("clientes") or espejo.get("items") or list(espejo.values()))
sin_cuit = [c for c in espejo if str(c.get("cuit") or "").strip() in ("", "0", "00000000000")]
con_cuit = [c for c in espejo if c not in sin_cuit]
check(f"Cantera tiene {len(espejo)} clientes y {len(sin_cuit)} sin CUIT real (00000000000 o vacío): el caso de Ceretti 2098 no era único", len(sin_cuit) >= 80 and len(con_cuit) > 0)
mostrador = q("select id from clientes where cuit='00000000000'")
check("antes: el Mostrador/Genérico es el único cliente con 00000000000", len(mostrador) == 1)

# ---- el caso de Tomy
cer = next(c for c in espejo if c["razon_social"] == "Ceretti 2098 SRL")
r = cli.post(f"/bridge/clientes/{cer['id']}/import")
nuevo = r.json().get("imported_id") if r.status_code == 200 else None
check(f"importar «Ceretti 2098 SRL» (CUIT 00000000000 en Cantera) [{r.status_code}]: se importa", r.status_code == 200 and nuevo)
fila = q("select razon_social, cuit, activo, flags_estado from clientes where id=?", (nuevo or "").replace("-", ""))
check(f"queda como cliente SIN CUIT (vacío, no con el reservado): {fila}", fila and fila[0][0] == "Ceretti 2098 SRL" and fila[0][1] in (None, ""))
check("el 00000000000 sigue siendo exclusivo del Mostrador/Genérico", q("select count(*) from clientes where cuit='00000000000'")[0][0] == 1)

# ---- todos los demás sin CUIT
malos, por_nombre = [], 0
for c in sin_cuit:
    if c["id"] == cer["id"]:
        continue
    r = cli.post(f"/bridge/clientes/{c['id']}/import")
    if r.status_code == 200:
        continue
    if r.status_code == 400 and ("BLOQUEO" in r.text):
        por_nombre += 1      # ya existía en el sistema con ese nombre: se frena CON su motivo, no con un 500
        continue
    malos.append((c["razon_social"], r.status_code, r.text[:100]))
check(f"los otros {len(sin_cuit) - 1} sin CUIT: ninguno da 500 ({por_nombre} ya existían con ese nombre y se frenaron con su motivo; fallas: {malos[:3]})", not malos)
check("y después de importarlos a todos, el 00000000000 sigue siendo solo del Mostrador/Genérico", q("select count(*) from clientes where cuit='00000000000'")[0][0] == 1)

# ---- los que tienen CUIT real siguen igual
mar = next(c for c in con_cuit if q("select count(*) from clientes where cuit=?", c["cuit"])[0][0] == 0)
r = cli.post(f"/bridge/clientes/{mar['id']}/import")
check(f"un cliente de Cantera con CUIT real se importa con su CUIT [{r.status_code}]", r.status_code == 200 and q("select cuit from clientes where id=?", r.json()["imported_id"].replace("-", ""))[0][0] == mar["cuit"])
check("y todas las importaciones de Cantera nacen igual (misma marca de «a revisar»): el cliente con CUIT y el de Ceretti tienen los mismos flags, y se terminan de completar en su ficha",
      q("select flags_estado from clientes where id=?", r.json()["imported_id"].replace("-", ""))[0][0] == fila[0][3])
r2 = cli.post(f"/bridge/clientes/{mar['id']}/import")
check(f"importarlo otra vez se frena con su motivo (400, BLOQUEO DE DUPLICADO), no con un 500 [{r2.status_code}]: {r2.text[:90]}", r2.status_code == 400 and "BLOQUEO" in r2.text)
check("un id que no está en Cantera: 404", cli.post("/bridge/clientes/no-existe/import").status_code == 404)

# ---- la pantalla muestra el motivo
cc = io.open("frontend/src/views/Hawe/ClientCanvas.vue", encoding="utf-8").read()
check("dentro de un PEDIDO (alta en ventana) el cliente importado de Cantera VUELVE al pedido en vez de llevarlo a la ficha y perder el pedido en curso: avisa que no está consistido y el pedido ya frena con «FALTAN» hasta completarlo",
      "if (props.isModal) {" in cc and "emit('save', { id: res.data.imported_id, razon_social: canteraClient.razon_social })" in cc and "todavía no está consistido: el pedido no sigue hasta completar sus datos" in cc
      and "router.replace({ name: 'HaweClientCanvas', params: { id: res.data.imported_id } })" in cc)
pc = io.open("frontend/src/views/Ventas/PedidoCanvas.vue", encoding="utf-8").read()
check("y el pedido ya tenía el freno: con un cliente incompleto avisa qué falta y no guarda («Complete la ficha», abre la ficha)",
      "if (!clientValidation.value.valid) {" in pc and "El cliente no cumple los requisitos para este circuito. Complete la ficha." in pc and "completarFichaCliente();" in pc)
check("la ficha del cliente muestra el motivo del servidor al fallar la importación (en vez de un «Error al importar» siempre igual)",
      "e?.response?.data?.detail" in cc and "No se pudo importar desde Cantera: ${motivo}" in cc)

ok = sum(1 for _, c in checks if c)
print(f"\nRESULTADO: {ok}/{len(checks)} checks OK")
if ok != len(checks):
    print("FALLO:", *[d for d, c in checks if not c], sep="\n  ")
    sys.exit(1)
