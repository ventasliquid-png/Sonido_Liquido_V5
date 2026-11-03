r"""S897, Carlos 02/11. «Cuando un alta se ponga null en el CUIT, ¿no podemos poner grisada la Condición ante el IVA? Y si se pone 11111111119, que el sistema infiera
Consumidor Final; o si tipea un CUIT, que verifique contra la lupa y ponga la condición real que trae ARCA.»
Origen: la ficha nueva nacía con «Consumidor Final» puesto de fábrica y el CUIT vacío (alta de María Claudia Rivas desde el pedido, 02/11), combinación que no es ni Rosa
ni formal. En la copia de P del 30/10, los 12 clientes activos sin CUIT tienen todos la condición vacía: el CUIT ya decide la condición.
(1) La regla del CUIT (frontend/src/utils/cuitFicha.js, en Node). (2) El cableado en la ficha (ClientCanvas.vue). (3) Con la regla puesta el pedido deja armar el pedido
del Consumidor Final con 11111111119 aunque no tenga domicilio (frontend/src/utils/clientePedido.js, en Node). (4) Servidor, sobre una COPIA de la base de P del 29/10:
alta sin CUIT ni condición = Rosa; alta con 11111111119 + Consumidor Final = Blanco (sin sello Rosa)."""
import sys, os, io, re, json, sqlite3, subprocess
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
SRC = os.path.join(RAIZ, "frontend", "src")
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
def node(js):
    r = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True, encoding="utf-8")
    try: return json.loads(r.stdout.strip())
    except Exception: print(r.stderr[:400]); return {}
URL = lambda *p: "file:///" + os.path.join(SRC, *p).replace("\\", "/")

# ---------- (1) la regla del CUIT, en Node ----------
R = node("import * as u from '" + URL("utils", "cuitFicha.js") + "'; "
         "const cl = ['', null, '   ', '11111111119', '00000000000', '11111111111', '99999999999', '3071', '30715603973', '30-71560397-3'].map(x => u.claseDeCuit(x)); "
         "const dv = ['30715603973', '30-71560397-3', '30715603970', '11111111119', '3071560397', 'abc'].map(x => u.cuitVerificadorOk(x)); "
         "const lo = ['', '11111111119', '00000000000', '11111111111', '99999999999', '3071', '30715603973'].map(x => u.ivaLoDecideElCuit(x)); "
         "const co = [u.debeConsultarArca('30715603973', ''), u.debeConsultarArca('30715603973', '30715603973'), u.debeConsultarArca('30-71560397-3', '30715603973'), "
         "u.debeConsultarArca('30715603970', ''), u.debeConsultarArca('11111111119', ''), u.debeConsultarArca('3071560', ''), u.debeConsultarArca('', '')]; "
         "console.log(JSON.stringify({cl, dv, lo, co, cf: u.CUIT_CF_GENERICO, rosa: u.CUIT_ROSA}))")
check("clase del CUIT: vacío, nulo y en blanco = vacio; 11111111119 y 00000000000 = cf; 11111111111 = rosa; 99999999999 = generico; incompleto = parcial; completo (con o sin guiones) = real",
      R.get("cl") == ["vacio", "vacio", "vacio", "cf", "cf", "rosa", "generico", "parcial", "real", "real"])
check("dígito verificador: el CUIT propio vale (con o sin guiones); uno con el último dígito cambiado, uno corto y texto no valen",
      R.get("dv") == [True, True, False, False, False, False])
check("la condición de IVA la decide el CUIT (campo gris) con CUIT vacío o genérico; con uno incompleto o real queda habilitada",
      R.get("lo") == [True, True, True, True, True, False, False])
check("consulta a ARCA sola: un CUIT real completo con verificador correcto que no se consultó; no si ya se consultó (aun con guiones), si el verificador falla, si es genérico, incompleto o vacío",
      R.get("co") == [True, False, False, False, False, False, False])
check("los CUIT reservados: 11111111119 es el Consumidor Final genérico y 11111111111 el Rosa (un dígito de diferencia, por eso el cartel y el botón)", R.get("cf") == "11111111119" and R.get("rosa") == "11111111111")

# ---------- (2) el cableado en la ficha ----------
fi = io.open(os.path.join(SRC, "views", "Hawe", "ClientCanvas.vue"), encoding="utf-8").read()
check("la ficha importa la regla del CUIT", "from '../../utils/cuitFicha'" in fi and "ivaLoDecideElCuit" in fi and "debeConsultarArca" in fi)
check("el campo «Condición IVA» se pone gris cuando el CUIT de un alta lo decide", re.search(r'<select v-model="form\.condicion_iva_id" :disabled="ivaDerivado"', fi) is not None
      and "const ivaDerivado = computed(() => isNew.value && ivaLoDecideElCuit(form.value.cuit))" in fi)
check("la ficha nueva ya no nace con «Consumidor Final» puesto de fábrica", "condicion_iva_id: 'f9cb56f12b2c47169b0f7bed74196d4c'" not in fi
      and re.search(r"const resetForm = \(\) => \{.*?condicion_iva_id: null,", fi, re.S) is not None)
check("al tipear el CUIT, la ficha infiere la condición (handleCuitInput) y lo hace solo en altas",
      re.search(r"const handleCuitInput = \(e\) => \{.*?inferirIvaDesdeCuit\(\)", fi, re.S) is not None and "const inferirIvaDesdeCuit = ({ consultar = true } = {}) => {\n    if (!isNew.value) return" in fi)
check("la consulta sola a ARCA sale de un solo lugar, el que tipea (no de un watch ni de la carga de la ficha)", fi.count("consultarAfip({ auto: true })") == 1
      and not re.search(r"watch\(\(\) => form\.value\.cuit[^)]*\)[^\n]*\n[^\n]*consultarAfip\(\{ auto", fi))
check("el botón «Consumidor Final: usar 11111111119» y la nota de qué se infirió están en la ficha", 'data-test="usar-cuit-cf"' in fi and 'data-test="nota-condicion-iva"' in fi and "Según ARCA:" in fi)
check("una ficha que pasa a alta (clonar, formalizar) también queda coherente, sin consultar a ARCA", "watch(isNew, (esAlta) => { if (esAlta) inferirIvaDesdeCuit({ consultar: false }) })" in fi)
check("si el CUIT cambia, la condición que había puesto el sistema (comodín o ARCA) para el número anterior se borra; la que eligió el operador a mano no se toca; y si vuelve al número de antes, ARCA se consulta de nuevo",
      "const ivaDelSistema = ref({ cuit: '', ivaId: null })" in fi and "if (s.ivaId && form.value.condicion_iva_id === s.ivaId && s.cuit !== soloDigitos(cuit)) {" in fi
      and "ultimoCuitConsultadoSolo.value = '' // si vuelve al número de antes" in fi)
check("una respuesta tardía de ARCA se descarta si el operador ya tipeó otro CUIT", "if (auto && soloDigitos(form.value.cuit) !== soloDigitos(cuitConsultado)) return" in fi)
check("la lupa distingue la consulta del sistema de la del operador (Enter y clic le pasan el evento): solo opts.auto === true, y en ese caso no abre el alert que bloquea",
      "const consultarAfip = async (opts) => {\n    const auto = opts?.auto === true" in fi and "if (!auto) alert(`❌ ERROR ARCA/AFIP:\\n\\n${res.error}" in fi and "if (!auto) alert(`❌ ERROR ARCA/AFIP:\\n\\n${msg}" in fi)
check("la lupa con CUIT genérico pone Consumidor Final solo con 11111111119 y 00000000000 (no con el 11111111111, que es Rosa) y el nombre del 11111111119 ya no es «RESPONSABLE INSCRIPTO GENÉRICO»",
      "if (claseDeCuit(form.value.cuit) === 'cf') {" in fi and "|| 5" not in fi and "RESPONSABLE INSCRIPTO GENÉRICO" not in fi.replace("antes decía «RESPONSABLE INSCRIPTO GENÉRICO»", ""))
check("las condiciones de reserva de ARCA (monotributo, inferido, desconocido) ya no escriben ids numéricos inexistentes: se buscan por nombre",
      re.search(r"condicion_iva_id\s*=\s*\d+\b", fi) is None and "ivaPorNombre('MONOTRIBUTO')" in fi and "ivaPorNombre('RESPONSABLE INSCRIPTO')" in fi)
check("el cartel del alta sin CUIT («¿Es un cliente Rosa?») ya no manda a elegir la condición, que está gris: manda al 11111111119",
      "o elija Consumidor Final como condición de IVA" not in fi and "para un Consumidor Final, ${CUIT_CF_GENERICO}" in fi)

# [S898, Carlos 03/11, H21: «solo máscara»] El 11111111119 ya no se guarda en la ficha: tipearlo o apretar el botón elige Consumidor Final y el CUIT queda vacío; el campo lo muestra atenuado.
check("H21: tipear el 11111111119 vacía el campo y elige Consumidor Final (no se guarda el comodín); el botón alterna entre Consumidor Final y Rosa; un comodín que llega cargado (clonar, Ingesta) queda como máscara",
      "if (digitos === CUIT_CF_GENERICO) {\n        e.target.value = ''\n        ponerConsumidorFinal()" in fi and "const alternarConsumidorFinal = () => (mascaraCuit.value ? quitarConsumidorFinal() : ponerConsumidorFinal())" in fi
      and "if (soloDigitos(cuit) === CUIT_CF_GENERICO) {\n            ponerConsumidorFinal()" in fi and "@click=\"alternarConsumidorFinal\" data-test=\"usar-cuit-cf\"" in fi and "usarCuitConsumidorFinal" not in fi
      and re.search(r"const ponerConsumidorFinal = \(\) => \{.*?form\.value\.cuit = ''.*?form\.value\.condicion_iva_id = cf\.id", fi, re.S) is not None)
check("H21: con Consumidor Final y el CUIT vacío el campo muestra el comodín atenuado (máscara), la lupa no consulta a ARCA y un CUIT vacío con Consumidor Final no se pisa a «sin condición»",
      "const mascaraCuit = computed(() => (esConsumidorFinal.value && !soloDigitos(form.value.cuit)) ? CUIT_CF_GENERICO : '')" in fi and ":placeholder=\"mascaraCuit || 'Sin Guiones'\"" in fi
      and "if (mascaraCuit.value && !auto) {" in fi and "if (!esConsumidorFinal.value) form.value.condicion_iva_id = null" in fi)

# ---------- (3) el pedido con el Consumidor Final del 11111111119 ----------
P = node("import { validarClienteParaPedido as v } from '" + URL("utils", "clientePedido.js") + "'; "
         "const cf = {flags_estado: 3, segmento_id: 's', condicion_iva_id: 'cf', cuit: '11111111119', domicilios: []}; "
         "const rosa = {flags_estado: 19, segmento_id: 's', condicion_iva_id: null, cuit: null, domicilios: []}; "
         "console.log(JSON.stringify({cf: v(cf, 'Consumidor Final'), cf_sin_nombre: v(cf, null), rosa: v(rosa, null)}))")
check("pedido: el Consumidor Final con 11111111119 y sin domicilio se puede operar (antes: «Faltan: Domicilio»); y el Rosa del alta sin CUIT con su segmento también",
      P.get("cf") == {"valid": True, "missing": []} and P.get("rosa") == {"valid": True, "missing": []})
check("pedido: sin el nombre de la condición, ese mismo cliente seguiría pidiendo el domicilio (por eso el pedido carga las condiciones de IVA antes de validar)",
      P.get("cf_sin_nombre") == {"valid": False, "missing": ["Domicilio"]})

# ---------- (4) servidor ----------
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user, get_current_user_optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261029_1821.db"
T = os.path.join(RAIZ, "scratch", "test_ficha_cuit_iva_tmp.db"); copiar_p(ORIG, T)
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
def alta(nombre, **extra):
    body = {"razon_social": nombre, "flags_estado": 3, "lista_precios_id": LISTA, "segmento_id": SEG, "domicilios": [], "vinculos": []}; body.update(extra)
    r = c.post("/clientes/", json=body)
    f = q("select cuit, flags_estado, condicion_iva_id from clientes where razon_social=?", nombre)
    return r.status_code, (f[0] if f else None)
st, f = alta("PRUEBA S897 SIN CUIT NI CONDICION")
check(f"alta sin CUIT y sin condición de IVA (lo que arma la ficha con el campo gris) [{st}]: sale Rosa (bit 4) y sin CUIT", st in (200, 201) and f and not f[0] and not f[2] and int(f[1]) & 16)
st, f = alta("PRUEBA S897 CF 11111111119", cuit="11111111119", condicion_iva_id=CF)
check(f"alta con el 11111111119 guardado y Consumidor Final (una ficha VIEJA, antes de H21) [{st}]: sigue siendo Blanco, sin sello Rosa (bit 4) ni medalla Rosa (bit 19)",
      st in (200, 201) and f and f[0] == "11111111119" and f[2] == CF and int(f[1]) & 16 == 0 and int(f[1]) & 524288 == 0)

st, f = alta("PRUEBA S898 CF SIN CUIT", condicion_iva_id=CF)
check(f"alta con Consumidor Final y el CUIT VACÍO (lo que arma la ficha con la máscara, H21) [{st}]: sale Blanco, sin CUIT guardado, sin sello Rosa (bit 4) ni medalla Rosa (bit 19)",
      st in (200, 201) and f and not f[0] and f[2] == CF and int(f[1]) & 16 == 0 and int(f[1]) & 524288 == 0)

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
try: os.remove(T)
except OSError: pass
sys.exit(1 if falla else 0)
