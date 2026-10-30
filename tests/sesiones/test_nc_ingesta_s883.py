r"""S883 (auditoria de CA, N1): la ingesta creadora (POST /ingesta/raw/{id}/approve) no acepta una NC ni una ND: 409 NOTA_NO_SE_INGESTA, antes de tocar el raw.
Sobre una COPIA de la base de P de las 17:51 (con las migraciones 051-059 ya aplicadas)."""
import sys, os, shutil, sqlite3, json, uuid
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.main import app
from backend.core.database import get_db
from backend.auth.dependencies import get_current_active_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
ORIG = r"Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\PRODUCCION_P\FIJAS_DE_PRUEBAS\PRODUCCION_P_al_20261008_1751.db"
T = os.path.join(RAIZ, "scratch", "test_nc_ingesta_tmp.db"); copiar_p(ORIG, T)
eng = create_engine(f"sqlite:///{T}"); S = sessionmaker(bind=eng)
def ov():
    db = S()
    try: yield db
    finally: db.close()
class U: id = 1; username = "tmp"; is_active = True
app.dependency_overrides[get_db] = ov; app.dependency_overrides[get_current_active_user] = lambda: U()
cli = TestClient(app, raise_server_exceptions=False)
def q(sql, *a):
    con = sqlite3.connect(T); v = con.execute(sql, a).fetchall(); con.close(); return v

cliente_id = q("select cliente_id from pedidos where id=82")[0][0]
cuit = q("select cuit from clientes where id=?", cliente_id)[0][0]
prod_vet = q("select producto_id from pedidos_items where id=181")[0][0]
ITEM = {"descripcion": "GUANTES VETERINARIOS 90 CM BOLSA X 100 UN", "cantidad": 5.0, "precio_unitario": 9750.0, "producto_id": prod_vet}

def raw(factura_extra, nombre="nc.pdf"):
    rid = uuid.uuid4().hex
    f = {"numero": "00001-00002990", "cae": "86416772099990", "vto_cae": "2026-10-18"}; f.update(factura_extra)
    con = sqlite3.connect(T)
    con.execute("insert into ingesta_facturas_raw (id, filename, pdf_bytes, audit_status, parsed_data_raw, flags_estado, created_at) values (?, ?, ?, 'RECIBIDO', ?, 0, datetime('now'))",
                (rid, nombre, b"%PDF-1.4", json.dumps({"cliente": {"cuit": cuit}, "factura": f, "items": []})))
    con.commit(); con.close(); return rid

def payload(numero, cae, vto="18/10/2026", **fac):
    f = {"numero": numero, "cae": cae, "vto_cae": vto}; f.update(fac)
    return {"cliente": {"id": cliente_id, "cuit": cuit, "razon_social": "LACTEOS DE POBLET SA"}, "factura": f, "items": [ITEM], "bultos": 1, "valor_declarado": 0.0,
            "modo_ingesta": "VINCULAR_EXISTENTE", "pedido_id_vinculado": 82}

def conteos():
    return tuple(q(f"select count(*) from {t}")[0][0] for t in ("facturas", "facturas_items", "remitos", "remitos_items", "pedidos", "ingesta_facturas_procesadas"))

def estado_raw(rid): return q("select audit_status from ingesta_facturas_raw where id=?", rid)[0][0]

# ---- H) NC: el parser la lee como NOTA_CREDITO_A; la pantalla manda solo numero, CAE y vencimiento
antes = conteos()
rid = raw({"codigo_afip": "03", "tipo_comprobante": "NOTA_CREDITO_A", "clase_comprobante": "NOTA_CREDITO", "letra": "A", "fecha_emision": "2026-10-08", "total_neto": 48750.0, "total_final": 58987.5})
r = cli.post(f"/ingesta/raw/{rid}/approve", json=payload("00001-00002990", "86416772099990"))
check(f"H: una NC se rechaza con 409 NOTA_NO_SE_INGESTA [{r.status_code}] {r.text[:110]}", r.status_code == 409 and "NOTA_NO_SE_INGESTA" in r.text and "Conciliar" in r.text)
check("H: no deja nada: ni factura, ni renglones, ni remito, ni pedido, ni 'procesada'", conteos() == antes)
check(f"H: el raw queda como estaba (RECIBIDO), listo para conciliarlo; no queda trabado en PROCESANDO [{estado_raw(rid)}]", estado_raw(rid) == "RECIBIDO")

# ---- I) ND
rid = raw({"codigo_afip": "02", "tipo_comprobante": "NOTA_DEBITO_A", "clase_comprobante": "NOTA_DEBITO", "letra": "A", "fecha_emision": "2026-10-08", "total_neto": 1000.0, "total_final": 1210.0})
r = cli.post(f"/ingesta/raw/{rid}/approve", json=payload("00001-00002989", "86416772099989"))
check(f"I: una ND tambien se rechaza [{r.status_code}]", r.status_code == 409 and "NOTA_NO_SE_INGESTA" in r.text and conteos() == antes and estado_raw(rid) == "RECIBIDO")

# ---- J) el raw dice NC pero la pantalla mando tipo Factura A: manda el raw (lo peligroso es guardar una NC como factura)
rid = raw({"tipo_comprobante": "NOTA_CREDITO_A", "clase_comprobante": "NOTA_CREDITO"})
r = cli.post(f"/ingesta/raw/{rid}/approve", json=payload("00001-00002988", "86416772099988", tipo_comprobante="FACTURA_A"))
check(f"J: raw con clase NC y pantalla con tipo Factura A: se rechaza igual [{r.status_code}]", r.status_code == 409 and conteos() == antes)

# ---- K) parser viejo (sin tipo ni clase en el raw) pero la pantalla manda el tipo de una NC
rid = raw({})
r = cli.post(f"/ingesta/raw/{rid}/approve", json=payload("00001-00002987", "86416772099987", tipo_comprobante="NOTA_CREDITO_B"))
check(f"K: sin datos en el raw, el tipo NOTA_CREDITO que manda la pantalla tambien se rechaza [{r.status_code}]", r.status_code == 409 and conteos() == antes)

# ---- L) una factura comun sigue entrando igual
neto = 5 * 9750.0
rid = raw({"numero": "00001-00002986", "cae": "86416772099986", "codigo_afip": "01", "tipo_comprobante": "FACTURA_A", "clase_comprobante": "FACTURA", "letra": "A", "fecha_emision": "2026-10-08", "total_neto": neto, "total_final": round(neto * 1.21, 2)})
con = sqlite3.connect(T); con.execute("update ingesta_facturas_raw set parsed_data_raw=? where id=?", (json.dumps({"cliente": {"cuit": cuit}, "factura": {"numero": "00001-00002986", "cae": "86416772099986", "vto_cae": "2026-10-18", "codigo_afip": "01", "tipo_comprobante": "FACTURA_A", "clase_comprobante": "FACTURA", "letra": "A", "fecha_emision": "2026-10-08", "total_neto": neto, "total_final": round(neto * 1.21, 2)},
        "items": [{"descripcion": ITEM["descripcion"], "cantidad": 5.0, "precio_unitario": 9750.0, "subtotal": neto, "alicuota_iva": 21.0}]}), rid)); con.commit(); con.close()
r = cli.post(f"/ingesta/raw/{rid}/approve", json=payload("00001-00002986", "86416772099986"))
f = q("select tipo_comprobante, estado, total from facturas where numero_comprobante=2986")
check(f"L: una Factura A normal sigue entrando: AUTORIZADA_AFIP, tipo A, total del PDF [{r.status_code}] {f}", r.status_code == 200 and f == [("FACTURA_A", "AUTORIZADA_AFIP", round(neto * 1.21, 2))] and estado_raw(rid) == "PROCESADO")

# ---- M) defensa en profundidad: create_from_ingestion directo con un tipo de NC
from backend.remitos.service import RemitosService
from backend.remitos.schemas import IngestionPayload
from fastapi import HTTPException
antes = conteos()
s = S()
try:
    RemitosService.create_from_ingestion(s, IngestionPayload(**payload("00001-00002985", "86416772099985", tipo_comprobante="NOTA_DEBITO_A")))
    hubo = None
except HTTPException as e:
    hubo = e
except Exception as e:
    hubo = e
s.rollback(); s.close()
check(f"M: create_from_ingestion directo con tipo NOTA_DEBITO_A: HTTPException 409 y no crea nada [{getattr(hubo, 'status_code', hubo)}]",
      isinstance(hubo, HTTPException) and hubo.status_code == 409 and "NOTA_NO_SE_INGESTA" in str(hubo.detail) and conteos() == antes)

del cli; eng.dispose()
try: os.remove(T)
except Exception: pass
falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
