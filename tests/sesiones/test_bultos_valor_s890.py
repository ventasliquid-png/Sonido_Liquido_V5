r"""S890, Carlos (21/10): el valor declarado y los bultos no son casilleros del formulario de armado: aparecen en una ventana AL TERMINAR el remito.
El operador puede ignorarla: «Cancelar» sigue con lo que propone (1 bulto y el valor sugerido). El valor sugerido es «el del producto antes de los
impuestos» (Carlos, 21/10): el neto de lo que sale, con el descuento global prorrateado; con el pedido completo, el neto del pedido. Se puede cambiar.
Caso real: el 0015-00003031 (Petroplastic) necesitó 200 bultos y $ 2.980.000,00 y hubo que agregarlos rehaciendo el PDF a mano (20/10).
(1) Servidor: POST /remitos/armar acepta bultos y valor_declarado; sin dato: 1 bulto y valor NULL. (2) El PDF imprime el valor en formato argentino
($ 2.980.000,00; antes «$ 2,980,000.00») y los bultos. (3) Pantalla (estática): la ventana aparece al terminar el armado y «Cancelar» no corta el remito.
Sobre una COPIA de la base de P (la más nueva de BACKUPS_DB/PRODUCCION_P)."""
import sys, os, shutil, sqlite3, glob, io, re
from _esquema_p import copiar_p
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from backend.remitos.remito_engine import generar_remito_pdf
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import fitz

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
TMP = os.path.join(RAIZ, "scratch", "test_bultos_valor"); os.makedirs(TMP, exist_ok=True)

ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_*.db"))[-1]
T = os.path.join(RAIZ, "scratch", "test_bultos_valor_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); r = con.execute(sql, a).fetchall(); con.commit(); con.close(); return r

# renglones con pendiente (pedido - remitido en remitos no anulados), de pedidos vivos
pend = q("""select pi.pedido_id, pi.id, pi.cantidad - coalesce((select sum(ri.cantidad_remitida) from remitos_items ri join remitos r on r.id=ri.remito_id
                                                         where ri.pedido_item_id=pi.id and r.estado<>'ANULADO'), 0) as falta
            from pedidos_items pi join pedidos p on p.id=pi.pedido_id where p.estado in ('PENDIENTE') order by pi.pedido_id desc""")
pend = [(p, i, f) for p, i, f in pend if f and f > 0]
check(f"setup: hay renglones con pendiente en la copia de P ({len(pend)})", len(pend) >= 2)
(p1, i1, f1), (p2, i2, f2) = pend[0], next(x for x in pend if x[0] != pend[0][0])

def armar(pedido_id, item_id, cant, **extra):
    return cli.post("/remitos/armar", json={"pedido_id": pedido_id, "metodo_entrega": "MOSTRADOR", "items": [{"pedido_item_id": item_id, "cantidad": cant}], **extra})

# ---- (1) servidor
r = armar(p1, i1, f1, bultos=200, valor_declarado=2980000)
j = r.json() if r.status_code == 200 else {}
check(f"armar con 200 bultos y valor declarado 2.980.000 [{r.status_code}] -> bultos {j.get('bultos')}, valor {j.get('valor_declarado')}", r.status_code == 200 and j.get("bultos") == 200 and j.get("valor_declarado") == 2980000)
r2 = armar(p2, i2, f2)
j2 = r2.json() if r2.status_code == 200 else {}
check(f"armar sin esos datos («Cancelar» en la ventana) [{r2.status_code}] -> 1 bulto y valor en blanco ({j2.get('bultos')}, {j2.get('valor_declarado')})", r2.status_code == 200 and j2.get("bultos") == 1 and j2.get("valor_declarado") is None)

# ---- (2) papel
p = os.path.join(TMP, "valor.pdf")
cli_data = {"razon_social": "PETROPLASTIC S A", "cuit": "30663253529", "domicilio_fiscal": "RUTA 234 KM. 16", "condicion_iva": "RESPONSABLE INSCRIPTO", "referencia": "Pedido #137",
            "oc": "", "bultos": 200, "valor_declarado": 2980000.0, "fecha": "20/10/2026"}
generar_remito_pdf(cli_data, [{"codigo": "", "descripcion": "BOBINA 300 MTS PACK X 2 UN", "cantidad": 400, "unidad": "UN"}], is_preview=False, output_path=p, numero_remito="0015-00003031")
txt = " ".join(fitz.open(p)[0].get_text().split())
check(f"el PDF imprime el valor en formato argentino ($ 2.980.000,00) y los bultos (200)", "$ 2.980.000,00" in txt and "BULTOS: 200" in txt and "2,980,000" not in txt)
cli_data.update(bultos=1, valor_declarado=1234.5)
generar_remito_pdf(cli_data, [{"codigo": "", "descripcion": "X", "cantidad": 1, "unidad": "UN"}], is_preview=False, output_path=p, numero_remito="0015-00003031")
txt = " ".join(fitz.open(p)[0].get_text().split())
check(f"con decimales: $ 1.234,50", "$ 1.234,50" in txt)
cli_data.update(valor_declarado=None)
generar_remito_pdf(cli_data, [{"codigo": "", "descripcion": "X", "cantidad": 1, "unidad": "UN"}], is_preview=False, output_path=p, numero_remito="0015-00003031")
txt = " ".join(fitz.open(p)[0].get_text().split())
check("sin valor declarado: el casillero queda en blanco (no dice $ 0,00)", "$ 0" not in txt and "VALOR DECL.:" in txt)

# ---- (3) pantalla (estática)
v = io.open(os.path.join(RAIZ, "frontend", "src", "views", "Logistica", "LogisticaSplitter.vue"), encoding="utf-8").read()
cuerpo = v[v.index("const confirmArmar"):v.index("const netoDelRemito")]
check("al terminar el armado (después de validar y de confirmar los parciales) aparece la ventana con el valor sugerido, en vez de armar enseguida",
      "const sugerido = netoDelRemito(elegidos);" in cuerpo and "Object.assign(datosTransporte, { visible: true, bultos: 1, valor: sugerido ? formatoAR(sugerido) : '', sugerido, imprimir, elegidos })" in cuerpo
      and "armarRemito" not in cuerpo)
check("la ventana pide valor declarado (sugerido: el neto sin impuestos, se puede cambiar) y bultos (1)",
      'data-modal="datos-transporte"' in v and 'data-campo="valor-declarado"' in v and 'data-campo="bultos"' in v and "Sugerido: el neto de lo que sale, sin impuestos" in v)
check("«Cancelar» no corta el remito: sigue con 1 bulto y el valor sugerido", "ejecutarArmado(datosTransporte.imprimir, datosTransporte.elegidos, 1, datosTransporte.sugerido)" in v)
check("el neto por unidad de cada renglón sale de su subtotal (ya descontado) y el descuento global se prorratea",
      "neto_unitario: item.cantidad_original ? (Number(item.subtotal) || 0) / item.cantidad_original : 0" in v
      and "(subtotales - (Number(localPedido.value?.descuento_global_importe) || 0)) / subtotales" in v)
# el mismo cálculo sobre un pedido real de la copia: remito = pedido completo -> neto del pedido (suma de subtotales - descuento global)
def neto_del_remito(pedido_id, parcial=None):
    items = q("select id, cantidad, subtotal from pedidos_items where pedido_id=?", pedido_id)
    dg = q("select coalesce(descuento_global_importe,0) from pedidos where id=?", pedido_id)[0][0]
    subt = sum(s or 0 for _, _, s in items); factor = (subt - dg) / subt if subt > 0 else 1
    return round(sum(((s or 0) / c if c else 0) * (parcial.get(i, c) if parcial else c) for i, c, s in items) * factor, 2), round(subt - dg, 2)
pid_dg = q("select id from pedidos where coalesce(descuento_global_importe,0) > 0 order by id desc limit 1")
pid = pid_dg[0][0] if pid_dg else p1
completo, neto_pedido = neto_del_remito(pid)
check(f"pedido #{pid} completo: el valor sugerido ({completo}) es el neto del pedido sin impuestos ({neto_pedido})", abs(completo - neto_pedido) < 0.01)
it0, c0 = q("select id, cantidad from pedidos_items where pedido_id=? order by id limit 1", pid)[0]
mitad, _ = neto_del_remito(pid, {i: (c0 / 2 if i == it0 else 0) for i, *_ in q("select id from pedidos_items where pedido_id=?", pid)})
check(f"remito parcial (la mitad del primer renglón): el sugerido es proporcional ({mitad}) y menor que el del pedido", 0 < mitad < completo or completo == 0)
check("«Aceptar» manda bultos y valor_declarado al armar (el valor se lee en formato argentino: 2.980.000 / 2980000,50)",
      "ejecutarArmado(datosTransporte.imprimir, datosTransporte.elegidos, bultos, montoAR(datosTransporte.valor))" in v and "bultos," in v and "valor_declarado: valorDeclarado" in v
      and ".replace(/\\./g, '').replace(',', '.')" in v)
# la lectura del valor, igual que montoAR
def montoAR(texto):
    limpio = re.sub(r"[$\s]", "", str(texto or "")).replace(".", "").replace(",", ".")
    try: n = float(limpio)
    except ValueError: return None
    return n if limpio and n > 0 else None
check("montoAR: «2.980.000» -> 2980000; «2980000,50» -> 2980000.5; «$ 2.980.000» -> 2980000; vacío o «abc» -> en blanco",
      montoAR("2.980.000") == 2980000 and montoAR("2980000,50") == 2980000.5 and montoAR("$ 2.980.000") == 2980000 and montoAR("") is None and montoAR("abc") is None)

# ---- limpieza
del cli; eng.dispose()
shutil.rmtree(TMP, ignore_errors=True)
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
