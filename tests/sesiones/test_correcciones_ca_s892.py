r"""S892, correcciones de la auditoría de CA de la S891 (INBOX 22/10 noche, puntos 1 y 2), antes del despliegue del paquete 2.
(1) Anular un remito facturado: la nota de crédito no borra el vínculo facturas_remitos (es historia), así que el remito quedaba
    trabado para siempre. Ahora manda lo facturado NETO de NC: por renglón si el remito tiene lo facturado por renglón; si no (lo que
    hay en P), por factura: la factura vinculada ampara al remito salvo que sus NC no anuladas cubran su total. En P hay un solo caso
    real con NC (el 0016-2597 de Cassará: FC 2597 con las NC 72 y 73, parcial); el caso «NC por el total» y el de renglón se arman en
    la copia porque P no los tiene (solo hay esas dos NC y ningún renglón de remito con lo facturado cargado).
(2) Quitar un renglón del pedido borraba los renglones de sus remitos anulados con número, y DELETE /pedidos/items/{id} (clic
    derecho «Eliminar Item» en el Tablero: CA creyó que no tenía pantalla) borraba sin ninguna guarda, aun con entregas y facturas.
    Ahora los dos caminos usan la misma regla. Sobre una COPIA de P con migrate_066 aplicada."""
import sys, os, shutil, sqlite3, glob, subprocess, io, uuid
from datetime import datetime
from _esquema_p import asegurar_esquema, imagenes_aparte
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = sorted(glob.glob(r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\PRODUCCION_P_al_*.db"))[-1]
TMP = os.path.join(RAIZ, "scratch", "test_correcciones_ca_s892"); os.makedirs(TMP, exist_ok=True)
T = os.path.join(TMP, "P.db"); shutil.copyfile(ORIG, T)
PY = os.path.join(RAIZ, "backend", "venv", "Scripts", "python.exe")
r = subprocess.run([PY, "-X", "utf8", os.path.join(RAIZ, "scripts", "migrate_066_remitos_genoma_fecha_emision.py")], capture_output=True, text=True,
                   encoding="utf-8", env=dict(os.environ, DATABASE_URL=f"sqlite:///{T}", PYTHONIOENCODING="utf-8"))
asegurar_esquema(T)
check(f"setup: copia de P con migrate_066 [rc {r.returncode}]", r.returncode == 0)

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
import backend.remitos.router as _router
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(_router.__file__))))
_aparte = imagenes_aparte(BASE); _aparte.__enter__()
SALIDA = os.path.join(BASE, "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida")
previos = set(os.listdir(SALIDA)) if os.path.isdir(SALIDA) else set()
def q(sql, *a):
    con = sqlite3.connect(T); x = con.execute(sql, a).fetchall(); con.commit(); con.close(); return x
def guid(x): x = x.replace("-", ""); return f"{x[:8]}-{x[8:12]}-{x[12:16]}-{x[16:20]}-{x[20:]}"
def remito(numero): return q("select id from remitos where numero_legal=?", numero)[0][0]
def estado(rid): return q("select estado from remitos where id=?", rid.replace("-", ""))[0][0]
def anular(rid, motivo="Prueba S892"): return cli.post(f"/remitos/{guid(rid)}/anular", json={"motivo": motivo})

def nueva_nc(modelo_id, numero, total, estado_nc):
    """Una NC más en la copia, igual en todo a la NC real `modelo_id` salvo id, número, total y estado."""
    cols = [c[1] for c in q("pragma table_info(facturas)")]
    fila = dict(zip(cols, q(f"select * from facturas where id=?", modelo_id)[0]))
    fila.update(id=uuid.uuid4().hex, numero_comprobante=numero, total=total, estado=estado_nc)
    if "cae" in fila: fila["cae"] = f"PRUEBA{numero}"
    q(f"insert into facturas ({','.join(cols)}) values ({','.join('?' * len(cols))})", *[fila[c] for c in cols])
    return fila["id"]

# ---- (1) anular un remito facturado: lo que libera es el neto de notas de crédito
r2597 = remito("0016-00002597")
f2597 = q("""select f.id from facturas f join facturas_remitos fr on replace(fr.factura_id,'-','')=replace(f.id,'-','')
             where replace(fr.remito_id,'-','')=? and f.numero_comprobante=2597""", r2597.replace("-", ""))[0][0]
nc73 = q("select id from facturas where tipo_comprobante like 'NOTA_CREDITO%' and numero_comprobante=73")[0][0]
r = anular(r2597)
check(f"0016-2597 (Cassará, caso real): FC 0001-00002597 con NC 72 y 73 que cubren una parte -> 409 que dice cuánto se acreditó de cuánto [{r.status_code}]",
      r.status_code == 409 and "REMITO_FACTURADO" in r.text and "0001-00002597" in r.text
      and "notas de crédito por $ 1.002.727,00 de $ 2.604.525,00" in r.text and estado(r2597) != "ANULADO")
resto = 2604525.0 - 1002727.0
nc_resto = nueva_nc(nc73, 999074, resto, "ANULADA")
q("insert into facturas_ajustes (factura_nc_nd_id, factura_ajustada_id, monto_aplicado, fecha_vinculo) values (?,?,?,?)",
  nc_resto, f2597, resto, datetime.now().isoformat(sep=" "))
r = anular(r2597)
check(f"una NC por el resto pero ANULADA no cuenta: sigue 409 [{r.status_code}]", r.status_code == 409 and estado(r2597) != "ANULADO")
q("update facturas set estado='AUTORIZADA_AFIP' where id=?", nc_resto)
r = anular(r2597, "Facturado y acreditado por completo con NC")
check(f"con las NC cubriendo el total de la factura, el remito se anula [{r.status_code}]", r.status_code == 200 and estado(r2597) == "ANULADO")
check("el vínculo con la factura queda (es historia): la NC no lo borra y la anulación tampoco",
      q("select count(*) from facturas_remitos where replace(remito_id,'-','')=?", r2597.replace("-", ""))[0][0] >= 1)

# por renglón: el 3030 (Coalix, sin factura vinculada)
r3030 = remito("0015-00003030")
ri30, pi30, cant30 = q("select id, pedido_item_id, cantidad_remitida from remitos_items where replace(remito_id,'-','')=?", r3030.replace("-", ""))[0]
q("update remitos_items set cantidad_facturada=? where id=?", cant30, ri30)
r = anular(r3030)
check(f"3030 con lo facturado por renglón y sin NC: 409 que nombra el renglón [{r.status_code}]",
      r.status_code == 409 and "facturado sin nota de crédito" in r.text and estado(r3030) != "ANULADO")
nc_renglon = nueva_nc(nc73, 999075, 1.0, "AUTORIZADA_AFIP")
q("insert into facturas_items (factura_id, pedido_item_id, remito_item_id, descripcion, cantidad, precio_unitario_neto, alicuota_iva, subtotal_neto) values (?,?,?,?,?,?,?,?)",
  nc_renglon, pi30, ri30, "NC de prueba", cant30, 0.0, 21.0, 0.0)
r = anular(r3030, "Acreditado con NC por renglón")
check(f"una NC que acredita todo el renglón lo libera: se anula [{r.status_code}]", r.status_code == 200 and estado(r3030) == "ANULADO")

# ---- (2) quitar renglones: una sola regla para el guardado del pedido y para «Eliminar Item»
pid = q("""select p.id from pedidos p join pedidos_items pi on pi.pedido_id=p.id where p.estado='PENDIENTE'
           and not exists(select 1 from remitos_items ri where ri.pedido_item_id=pi.id)
           and not exists(select 1 from facturas_items fi where fi.pedido_item_id=pi.id)
           group by p.id having count(*) >= 2 order by p.id desc limit 1""")[0][0]
items = q("select id, producto_id, cantidad, precio_unitario, descuento_porcentaje, descuento_importe from pedidos_items where pedido_id=? order by id", pid)
(ia, *_), (ib, *_) = items[0], items[1]
r = cli.post("/remitos/armar", json={"pedido_id": pid, "metodo_entrega": "TRANSPORTE_PROPIO", "items": [{"pedido_item_id": ia, "cantidad": items[0][2]}]})
rid_a = r.json()["id"] if r.status_code == 200 else ""
cli.get(f"/remitos/{rid_a}/pdf")
num_a = q("select numero_legal from remitos where id=?", rid_a.replace("-", ""))[0][0]
r = anular(rid_a.replace("-", ""), "El cliente ya no lo quiere")
check(f"armado: el renglón A del pedido #{pid} queda solo en un remito con número ANULADO ({num_a}) [{r.status_code}]", r.status_code == 200 and num_a)
def renglones_de_remito(item): return q("select count(*) from remitos_items where pedido_item_id=?", item)[0][0]
r = cli.delete(f"/pedidos/items/{ia}")
check(f"«Eliminar Item» (DELETE) sobre ese renglón: 400 que nombra el remito; el renglón del remito anulado no se borra [{r.status_code}]",
      r.status_code == 400 and f"{num_a} (ANULADO)" in r.text and renglones_de_remito(ia) == 1 and q("select count(*) from pedidos_items where id=?", ia)[0][0] == 1)
cuerpo = [{"id": i, "producto_id": p, "cantidad": c, "precio_unitario": pu, "descuento_porcentaje": dp or 0.0, "descuento_importe": di or 0.0}
          for i, p, c, pu, dp, di in items if i != ia]
r = cli.patch(f"/pedidos/{pid}", json={"items": cuerpo})
check(f"guardar el pedido sin ese renglón: 400 con el mismo motivo (antes borraba en masa los renglones de remitos anulados) [{r.status_code}]",
      r.status_code == 400 and f"{num_a} (ANULADO)" in r.text and renglones_de_remito(ia) == 1)
pi137 = q("select ri.pedido_item_id from remitos_items ri join remitos r on r.id=ri.remito_id where r.numero_legal='0015-00003031'")[0][0]
r = cli.delete(f"/pedidos/items/{pi137}")
check(f"«Eliminar Item» sobre un renglón con entregas (3031): 400 «ya tiene … unidades entregadas» y no borra nada (antes borraba hasta el remito vigente) [{r.status_code}]",
      r.status_code == 400 and "unidades entregadas" in r.text and renglones_de_remito(pi137) >= 1)
pi_fact = q("select pedido_item_id from facturas_items fi join facturas f on f.id=fi.factura_id where f.estado='AUTORIZADA_AFIP' and f.tipo_comprobante like 'FACTURA%' and pedido_item_id is not null limit 1")[0][0]
r = cli.delete(f"/pedidos/items/{pi_fact}")
check(f"«Eliminar Item» sobre un renglón facturado: 400 [{r.status_code}]", r.status_code == 400 and q("select count(*) from pedidos_items where id=?", pi_fact)[0][0] == 1)
r = cli.delete(f"/pedidos/items/{ib}")
check(f"«Eliminar Item» sobre un renglón limpio (sin remitos ni facturas): se borra como siempre [{r.status_code}]",
      r.status_code == 204 and q("select count(*) from pedidos_items where id=?", ib)[0][0] == 0)

# ---- pantalla (estática)
lista = io.open(os.path.join(RAIZ, "frontend", "src", "views", "Pedidos", "PedidoList.vue"), encoding="utf-8").read()
check("Tablero: si no se puede eliminar el renglón, la pantalla muestra el motivo del servidor (antes «Error eliminando item»)",
      "'No se pudo eliminar: ' + (e.response?.data?.detail || e.message)" in lista)

# ---- limpieza
del cli; eng.dispose()
for n in (set(os.listdir(SALIDA)) - previos) if os.path.isdir(SALIDA) else []:
    os.remove(os.path.join(SALIDA, n))
_aparte.__exit__(None, None, None)
shutil.rmtree(TMP, ignore_errors=True)
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
