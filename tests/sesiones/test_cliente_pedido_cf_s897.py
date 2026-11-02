r"""S897, Carlos 02/11. «Queremos dar de alta un rosa desde el pedido y nos dice "Falta dirección", y eso no es lógico... además pide CUIT.»
Caso real en producción (P, 02/11 16:07): MARÍA CLAUDIA RIVAS, alta desde el pedido, retira en el depósito de Vía Cargo de Santa Rosa (La Pampa), cargada con la
condición «Consumidor Final», segmento Distribuidor y sin CUIT: flags 3, o sea ni Rosa (bit 4) ni validada por ARCA (bit 2). La pantalla del pedido la mandaba a la
regla de «sin clasificar», que exige todo («Faltan: Domicilio, CUIT»), y no dejaba guardar. Un Consumidor Final es Blanco a los efectos fiscales (Nike S894), no tiene
CUIT en la ficha (S896) y su entrega no es un dato fiscal: se opera con lo mismo que un Rosa, el segmento.
(1) La regla (frontend/src/utils/clientePedido.js, en Node). (2) El pedido la usa y ya no tiene la regla suelta. (3) Servidor, sobre una COPIA de la base de P del 29/10: el
alta de un CF con segmento y sin CUIT sale sin sello Rosa (flags 3, como en P) y sacarle la condición de IVA la deja Rosa (bit 4): es la salida inmediata para el
operador mientras el arreglo no llega a producción."""
import sys, os, io, json, sqlite3, subprocess
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
SRC = os.path.join(RAIZ, "frontend", "src")
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)

# ---------- (1) la regla, en Node ----------
util = os.path.join(SRC, "utils", "clientePedido.js").replace("\\", "/")
casos = {
    "rivas":        ({"flags_estado": 3, "segmento_id": "s", "condicion_iva_id": "cf", "cuit": None, "domicilios": []}, "Consumidor Final"),
    "cf_sin_seg":   ({"flags_estado": 3, "segmento_id": None, "condicion_iva_id": "cf", "cuit": None, "domicilios": []}, "Consumidor Final"),
    "cf_minuscula": ({"flags_estado": 3, "segmento_id": "s", "condicion_iva_id": "cf", "cuit": None, "domicilios": []}, "consumidor final"),
    "rosa":         ({"flags_estado": 19, "segmento_id": "s", "condicion_iva_id": None, "cuit": None, "domicilios": []}, None),
    "rosa_sin_seg": ({"flags_estado": 19, "segmento_id": None, "condicion_iva_id": None, "cuit": None, "domicilios": []}, None),
    "gold":         ({"flags_estado": 15, "segmento_id": None, "condicion_iva_id": None, "cuit": None, "domicilios": []}, None),
    "ri_vacio":     ({"flags_estado": 3, "segmento_id": "s", "condicion_iva_id": "ri", "cuit": None, "domicilios": []}, "Responsable Inscripto"),
    "sin_nada":     ({"flags_estado": 3, "segmento_id": "s", "condicion_iva_id": None, "cuit": "", "domicilios": []}, None),
    "ri_completo":  ({"flags_estado": 3, "segmento_id": "s", "condicion_iva_id": "ri", "cuit": "30715603973", "domicilios": [{"id": 1}]}, "Responsable Inscripto"),
    "sin_cliente":  (None, None),
}
js = ("import { validarClienteParaPedido as v } from 'file:///" + util + "'; const C = " + json.dumps({k: list(x) for k, x in casos.items()}) +
      "; const R = {}; for (const [k, [c, n]] of Object.entries(C)) R[k] = v(c, n); console.log(JSON.stringify(R))")
r = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True, encoding="utf-8")
try: R = json.loads(r.stdout.strip())
except Exception: R = {}; print(r.stderr[:300])
check("Consumidor Final sin CUIT, sin domicilio y con segmento (María Claudia Rivas): válido, ya no «Faltan: Domicilio, CUIT»", R.get("rivas") == {"valid": True, "missing": []})
check("el nombre de la condición se compara sin importar mayúsculas", R.get("cf_minuscula") == {"valid": True, "missing": []})
check("un Consumidor Final sin segmento sigue faltando el segmento, y solo eso", R.get("cf_sin_seg") == {"valid": False, "missing": ["Segmento"]})
check("Rosa con segmento: válido; sin segmento: solo falta el segmento (como antes)", R.get("rosa", {}).get("valid") is True and R.get("rosa_sin_seg") == {"valid": False, "missing": ["Segmento"]})
check("Gold (validado por ARCA): siempre válido (como antes)", R.get("gold") == {"valid": True, "missing": []})
check("un Responsable Inscripto sin clasificar sigue exigiéndolo todo: Domicilio y CUIT (como antes)", R.get("ri_vacio") == {"valid": False, "missing": ["Domicilio", "CUIT"]})
check("sin condición de IVA y sin nada más: Condición IVA, Domicilio y CUIT (como antes)", R.get("sin_nada") == {"valid": False, "missing": ["Condición IVA", "Domicilio", "CUIT"]})
check("un cliente formal completo: válido; sin cliente: válido", R.get("ri_completo") == {"valid": True, "missing": []} and R.get("sin_cliente") == {"valid": True, "missing": []})

# ---------- (2) el pedido usa la regla ----------
ped = io.open(os.path.join(SRC, "views", "Ventas", "PedidoCanvas.vue"), encoding="utf-8").read()
check("PedidoCanvas importa la regla y la usa con el nombre de la condición de IVA",
      "import { validarClienteParaPedido } from '@/utils/clientePedido'" in ped and "return validarClienteParaPedido(c, iva?.nombre || c.condicion_iva?.nombre);" in ped)
check("y carga las condiciones de IVA antes de validar", "if (maestrosStore.condicionesIva.length === 0) {" in ped and "await maestrosStore.fetchCondicionesIva();" in ped)
check("la regla suelta de «sin clasificar» ya no está en el pedido", "missing.push('CUIT')" not in ped and "missing.push('Domicilio')" not in ped)

# ---------- (3) servidor: la salida inmediata ----------
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user, get_current_user_optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261029_1821.db"
T = os.path.join(RAIZ, "scratch", "test_cliente_pedido_cf_tmp.db"); copiar_p(ORIG, T)
S = sessionmaker(bind=create_engine(f"sqlite:///{T}"))
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
CF = q("select id from condiciones_iva where upper(nombre) like '%CONSUMIDOR FINAL%' limit 1")[0][0]
LISTA = q("select id from listas_precios limit 1")[0][0]
SEG = q("select id from segmentos where upper(nombre) not like '%CONSUMIDOR%' limit 1")[0][0]
r = c.post("/clientes/", json={"razon_social": "PRUEBA S897 RETIRA EN VIA CARGO", "flags_estado": 3, "condicion_iva_id": CF, "lista_precios_id": LISTA, "segmento_id": SEG, "domicilios": [], "vinculos": []})
f = q("select id, cuit, flags_estado from clientes where razon_social='PRUEBA S897 RETIRA EN VIA CARGO'")
check(f"alta como Consumidor Final con segmento y sin CUIT [{r.status_code}]: queda sin CUIT y sin sello Rosa (flags 3, igual que en P)", r.status_code in (200, 201) and f and not f[0][1] and int(f[0][2]) & 16 == 0)
if f:
    r = c.put(f"/clientes/{f[0][0]}", json={"condicion_iva_id": None})
    g = q("select cuit, flags_estado from clientes where id=?", f[0][0])[0]
    check(f"sacarle la condición de IVA [{r.status_code}] la deja Rosa (bit 4) y sin CUIT: la pantalla del pedido ya la acepta con el segmento ({g[1]})", r.status_code == 200 and not g[0] and int(g[1]) & 16)

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
try: os.remove(T)
except OSError: pass
sys.exit(1 if falla else 0)
