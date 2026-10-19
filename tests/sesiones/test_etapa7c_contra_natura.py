"""Etapa 7c -- facturas contra natura, end to end contra COPIAS descartables de pilot_v5x.db.
Datos reales: factura ARCA 2496 (Jorgito, CUIT 33516033199, cliente blanco existente, 6 guantes a
10900) y 2458 (Ceretti, CUIT fuera del padron de D). Nunca toca la base viva."""
import shutil, sys, os, sqlite3, uuid
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5")
os.chdir(r"C:\dev\Sonido_Liquido_V5")

import backend.main as main_module
from backend.main import app
from backend.core.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

SCRATCH = r"C:\dev\Sonido_Liquido_V5\scratch\pilot_v5x_etapa7c_test.db"
TRANS = "44264d5c43a147d3997fd558d38b3db6"
GUANTES = 175

checks = []
def check(desc, cond):
    checks.append((desc, bool(cond)))
    print(("[OK]  " if cond else "[FAIL]"), desc)

engine = None
Session = None
def copia_fresca():
    global engine, Session
    if engine is not None:
        engine.dispose()
    copiar_p("pilot_v5x.db", SCRATCH)
    engine = create_engine(f"sqlite:///{SCRATCH}")
    Session = sessionmaker(bind=engine)
    def override():
        db = Session()
        try:
            yield db
        finally:
            db.close()
    app.dependency_overrides[get_db] = override
    return TestClient(app)

def sql(q, args=()):
    con = sqlite3.connect(SCRATCH); cur = con.cursor(); cur.execute(q, args); r = cur.fetchall(); con.close(); return r
def exe(q, args=()):
    con = sqlite3.connect(SCRATCH); con.execute(q, args); con.commit(); con.close()
def raw_uuid(numero):
    return str(uuid.UUID(sql("SELECT id FROM ingesta_facturas_raw WHERE filename LIKE ? LIMIT 1", (f"%{numero}%",))[0][0]))
def token(client):
    r = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

# =========================================================== 1. retroactivo (Jorgito 2496)
client = copia_fresca()
rid = raw_uuid("00002496")
pedidos_antes = sql("SELECT COUNT(*) FROM pedidos")[0][0]
stock_antes = float(sql("SELECT stock_reservado FROM productos WHERE id = ?", (GUANTES,))[0][0] or 0)

ev = client.post(f"/ingesta/raw/{rid}/contra-natura/evaluar", json={}).json()
check("Sin asignar producto: 'Guantes de polietileno...' no esta en el catalogo -> DESMADRE", ev["veredicto"] == "DESMADRE")
check("Cliente resuelto por CUIT (unico): Jorgito", ev["cliente_id"] is not None and len(ev["clientes"]) == 1)
check("Sin transporte habitual (sede ni pedidos previos) -> bloqueo TRANSPORTE_REQUERIDO, no elige al azar",
      any("TRANSPORTE_REQUERIDO" in b for b in ev["bloqueos"]) and ev["transporte_id"] is None)
check("Sede sugerida: una de entrega", ev["domicilio_entrega_id"] is not None)

prods = [{"item_pdf": 0, "producto_id": GUANTES}]
ev = client.post(f"/ingesta/raw/{rid}/contra-natura/evaluar", json={"productos": prods, "transporte_id": TRANS}).json()
check("Con producto asignado por el operador y transporte elegido -> RETROACTIVO sin bloqueos",
      ev["veredicto"] == "RETROACTIVO" and ev["bloqueos"] == [])

body = {"productos": prods, "transporte_id": TRANS}
r = client.post(f"/ingesta/raw/{rid}/contra-natura/confirmar", json=body)
check("Confirmar SIN sesion -> 401", r.status_code == 401)
r = client.post(f"/ingesta/raw/{rid}/contra-natura/confirmar", json=body, headers=token(client))
check(f"Confirmar con sesion -> 200 ({r.status_code}: {r.text[:200] if r.status_code != 200 else ''})", r.status_code == 200)
res = r.json() if r.status_code == 200 else {}
pid = res.get("pedido_id")

p = sql("SELECT flags_estado, origen, nota, estado, fecha, tipo_facturacion, total FROM pedidos WHERE id = ?", (pid,))
flags = p[0][0] if p else 0
check("Pedido creado", len(p) == 1 and sql("SELECT COUNT(*) FROM pedidos")[0][0] == pedidos_antes + 1)
check("Marcado con ORIGEN_FACTURA (38) y ORIGEN_RETROACTIVO (39)", bool(flags & (1 << 38)) and bool(flags & (1 << 39)))
check("Estado ES_FIRME (33), blanco (sin NO_FISCAL_FORCE 12)", bool(flags & (1 << 33)) and not flags & (1 << 12))
check("origen = CONTRA_NATURA (no INGESTA_PDF: el borrado de remitos no lo arrastra)", p and p[0][1] == "CONTRA_NATURA")
check("Nota [SISTEMA] con el prefijo catalogado", p and p[0][2].startswith("[SISTEMA] Pedido reconstruido desde factura FACTURA_A"))
check(f"Fecha del pedido = emision de la factura (2026-03-05): {p and p[0][4]}", p and str(p[0][4]).startswith("2026-03-05"))
check("Tipo de facturacion A (de la letra del comprobante)", p and p[0][5] == "A")
check(f"Total = neto 65400 x 1,21 = 79134 ({p and p[0][6]})", p and abs(p[0][6] - 79134.0) < 0.01)
pi = sql("SELECT producto_id, cantidad, precio_unitario, subtotal FROM pedidos_items WHERE pedido_id = ?", (pid,))
check(f"Renglon del pedido desde el PDF: {pi}", pi == [(GUANTES, 6.0, 10900.0, 65400.0)])
stock_despues = float(sql("SELECT stock_reservado FROM productos WHERE id = ?", (GUANTES,))[0][0] or 0)
check(f"Stock reservado +6 igual que el alta normal ({stock_antes} -> {stock_despues})", abs(stock_despues - stock_antes - 6) < 0.001)

rem = sql("SELECT id, estado, numero_legal FROM remitos WHERE pedido_id = ?", (pid,))
check("PR retroactivo creado, BORRADOR y sin numerar (se numera al imprimir)", len(rem) == 1 and rem[0][1] == "BORRADOR" and rem[0][2] is None)
ri = sql("SELECT cantidad_remitida, cantidad_facturada FROM remitos_items WHERE remito_id = ?", (rem[0][0],)) if rem else []
check(f"Renglon del PR: remitido 6, facturado 6 ({ri})", ri == [(6.0, 6.0)])
f = sql("SELECT tipo_comprobante, estado, numero_comprobante, notas_auditoria FROM facturas WHERE numero_comprobante = 2496")
check("Factura real registrada y marcada CONTRA NATURA", len(f) == 1 and f[0][1] == "AUTORIZADA_AFIP" and "CONTRA NATURA" in f[0][3])
check("Factura vinculada al PR retroactivo", sql("SELECT COUNT(*) FROM facturas_remitos WHERE remito_id = ?", (rem[0][0],))[0][0] == 1)
check("Auditoria de ingesta: estado CONTRA_NATURA", sql("SELECT COUNT(*) FROM ingesta_facturas_procesadas WHERE estado = 'CONTRA_NATURA'")[0][0] == 1)

cats = client.get("/informes/notas-categorias").json()
check("Informe D ofrece la categoria 'Contra natura'", any(c["key"] == "contra_natura" for c in cats))
filas = client.get("/informes/notas-pedidos", params={"categorias": "contra_natura"}).json()["filas"]
check(f"Informe D la cuenta: filtrando 'Contra natura' aparece el pedido #{pid}", [x["pedido_id"] for x in filas] == [pid])

r = client.post(f"/ingesta/raw/{rid}/contra-natura/confirmar", json=body, headers=token(client))
check("Reintentar la misma factura -> 409 FACTURA_DUPLICADA", r.status_code == 409 and "FACTURA_DUPLICADA" in r.text)

# =========================================================== 2. desmadre (Ceretti 2458)
client = copia_fresca()
rid = raw_uuid("00002458")
n = [sql(f"SELECT COUNT(*) FROM {t}")[0][0] for t in ("pedidos", "remitos", "facturas")]
ev = client.post(f"/ingesta/raw/{rid}/contra-natura/evaluar", json={}).json()
check("Ceretti (CUIT fuera del padron) -> DESMADRE con motivo de cliente", ev["veredicto"] == "DESMADRE" and any("CUIT" in m for m in ev["motivos_desmadre"]))
r = client.post(f"/ingesta/raw/{rid}/contra-natura/confirmar", json={"productos": []}, headers=token(client))
check("Confirmar un desmadre -> 409, dice NC por el total", r.status_code == 409 and "nota de crédito" in r.text)
check("No se creo nada (pedidos/remitos/facturas iguales)", [sql(f"SELECT COUNT(*) FROM {t}")[0][0] for t in ("pedidos", "remitos", "facturas")] == n)
r = client.post(f"/ingesta/raw/{rid}/contra-natura/marcar-desmadre")
check("Marcar desmadre SIN sesion -> 401", r.status_code == 401)
r = client.post(f"/ingesta/raw/{rid}/contra-natura/marcar-desmadre", headers=token(client))
st = sql("SELECT audit_status, audit_warning FROM ingesta_facturas_raw WHERE id = ?", (rid.replace("-", ""),))
check("Marcado: raw.audit_status = DESMADRE con motivo y quien lo marco (nunca en silencio)",
      r.status_code == 200 and st[0][0] == "DESMADRE" and "NC" in st[0][1] and "admin" in st[0][1])
rid_j = raw_uuid("00002496")
r = client.post(f"/ingesta/raw/{rid_j}/contra-natura/marcar-desmadre", json={"productos": [{"item_pdf": 0, "producto_id": GUANTES}]}, headers=token(client))
check("Con el producto asignado por el operador la mercaderia existe -> NO se deja marcar como desmadre (409)",
      r.status_code == 409 and "NO_ES_DESMADRE" in r.text)
check("...y el raw de Jorgito sigue sin marcar", sql("SELECT audit_status FROM ingesta_facturas_raw WHERE id = ?", (rid_j.replace("-", ""),))[0][0] != "DESMADRE")

# =========================================================== 3. bloqueos y avisos
client = copia_fresca()
rid = raw_uuid("00002496")
exe("UPDATE clientes SET flags_estado = flags_estado | 16 WHERE replace(cuit,'-','') = '33516033199'")
ev = client.post(f"/ingesta/raw/{rid}/contra-natura/evaluar", json={"productos": [{"item_pdf": 0, "producto_id": GUANTES}], "transporte_id": TRANS}).json()
check("Cliente Rosa -> bloqueo CLIENTE_ROSA (una factura fiscal no va a un rosa)", any("CLIENTE_ROSA" in b for b in ev["bloqueos"]))

client = copia_fresca()
ev = client.post(f"/ingesta/raw/{raw_uuid('00002591')}/contra-natura/evaluar", json={}).json()
check("2591 ya registrada -> bloqueo FACTURA_DUPLICADA", any("FACTURA_DUPLICADA" in b for b in ev["bloqueos"]))

r = client.post("/remitos/armar", json={"pedido_id": 24, "domicilio_entrega_id": "0358b5a6d2ec461caec2c3978930499a",
                "transporte_id": TRANS, "items": [{"pedido_item_id": 40, "cantidad": 3}]})
ev = client.post(f"/ingesta/raw/{raw_uuid('00002526')}/contra-natura/evaluar", json={}).json()
check("Genesis con un PR esperando factura -> aviso HAY_PR_PENDIENTES (conciliar en vez de reconstruir)",
      any("HAY_PR_PENDIENTES" in a for a in ev["avisos"]))

# =========================================================== 4. atomicidad: todo o nada
client = copia_fresca()
rid = raw_uuid("00002496")
n = [sql(f"SELECT COUNT(*) FROM {t}")[0][0] for t in ("pedidos", "pedidos_items", "remitos", "remitos_items", "facturas")]
stock0 = sql("SELECT stock_reservado FROM productos WHERE id = ?", (GUANTES,))[0][0]
from backend.ingesta import contra_natura as cn_mod
from backend.ingesta.conciliador import ConciliadorService
original = ConciliadorService.confirmar
def falla(*a, **k):
    raise RuntimeError("falla simulada al conciliar")
ConciliadorService.confirmar = staticmethod(falla)
db = Session()
try:
    try:
        cn_mod.ContraNaturaService.confirmar(db, uuid.UUID(rid), None, [{"item_pdf": 0, "producto_id": GUANTES}], None, TRANS, None)
        rompio = False
    except RuntimeError:
        rompio = True
finally:
    db.close()
    ConciliadorService.confirmar = original
check("Falla simulada despues de crear pedido y PR -> se propaga", rompio)
check("Rollback completo: ni pedido, ni renglones, ni PR, ni factura quedaron",
      [sql(f"SELECT COUNT(*) FROM {t}")[0][0] for t in ("pedidos", "pedidos_items", "remitos", "remitos_items", "facturas")] == n)
check("Rollback completo: la reserva de stock tampoco quedo", sql("SELECT stock_reservado FROM productos WHERE id = ?", (GUANTES,))[0][0] == stock0)

engine.dispose()
os.remove(SCRATCH)
print()
total = len(checks); ok = sum(1 for _, c in checks if c)
print(f"RESULTADO: {ok}/{total} checks OK")
if ok != total: sys.exit(1)
