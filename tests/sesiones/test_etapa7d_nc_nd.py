"""Etapa 7d -- NC/ND end to end contra COPIAS descartables de pilot_v5x.db. Nunca toca la base viva.
Datos reales de D: pedido #24 (Genesis Bag) == factura ARCA 2526. Las NC/ND son SINTETICAS (no hay ninguna real
en el corpus): se fabrican a partir del PDF real de la 2526 cambiando leyenda/codigo AFIP/numero (nc_sintetica.py);
para los casos parciales/excedidos se parchea _parsear (los renglones y totales del PDF) en proceso."""
import shutil, sys, os, sqlite3, uuid, subprocess, io
from _esquema_p import copiar_p   # [S888] copia la base de P y le asegura la columna pedidos_items.kit_grupo (migrate_063)
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(r"C:\dev\Sonido_Liquido_V5")

import backend.main as main_module
from backend.main import app
from backend.core.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException
from fastapi.testclient import TestClient
import backend.ingesta.conciliador as conc_mod
import backend.ingesta.conciliador_ajuste as aj_mod
from nc_sintetica import fabricar

SCRATCH = r"C:\dev\Sonido_Liquido_V5\scratch\pilot_v5x_etapa7d_test.db"
DOM = "0358b5a6d2ec461caec2c3978930499a"
TRANS = "44264d5c43a147d3997fd558d38b3db6"
BIT_TIENE_NC, BIT_TIENE_ND, BIT_ES_NC, BIT_ES_ND = 1 << 17, 1 << 18, 1 << 19, 1 << 20

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
    from backend.core.database import Base
    Base.metadata.create_all(engine)  # lo que hace el arranque del backend: crea facturas_ajustes vacia
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

def uid(hexstr):
    return str(uuid.UUID(hexstr))

def token(client):
    r = client.post("/auth/token", data={"username": "admin", "password": "admin123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

def armar(client, items):
    r = client.post("/remitos/armar", json={"pedido_id": 24, "domicilio_entrega_id": DOM, "transporte_id": TRANS,
                                             "items": [{"pedido_item_id": a, "cantidad": b} for a, b in items]})
    assert r.status_code == 200, r.text
    return r.json()

PEDIDO_24 = [(40, 3), (41, 1), (42, 1), (43, 2), (44, 2)]
def ri_de(remito, pid):
    return next(i["id"] for i in remito["items"] if i["pedido_item_id"] == pid)

PDF_2526 = sqlite3.connect("pilot_v5x.db").execute(
    "SELECT pdf_bytes FROM ingesta_facturas_raw WHERE filename LIKE '%00002526%' LIMIT 1").fetchone()[0]

def subir(client, nombre, **kw):
    """Sube una NC/ND sintetica por el endpoint real de ingesta. Devuelve (raw_id_uuid, respuesta)."""
    pdf = fabricar(PDF_2526, **kw)
    r = client.post("/ingesta/raw", files={"file": (nombre, io.BytesIO(pdf), "application/pdf")})
    assert r.status_code == 200, r.text
    return uid(r.json()["id"]) if len(r.json()["id"]) == 32 else r.json()["id"], r.json()

def factura_2526(client):
    """Estado base de casi todos los escenarios: PR armado con el pedido #24 y la factura 2526 conciliada
    (5 renglones atados a sus renglones de PR, cantidad_facturada 3/1/1/2/2)."""
    pr = armar(client, PEDIDO_24)
    raw = uid(sql("SELECT id FROM ingesta_facturas_raw WHERE filename LIKE '%00002526%' LIMIT 1")[0][0])
    emp = [{"item_pdf": i, "remito_item_id": ri_de(pr, pid)} for i, (pid, _) in enumerate(PEDIDO_24)]
    r = client.post(f"/ingesta/raw/{raw}/conciliacion/confirmar", json={"remito_ids": [pr["id"]], "emparejamiento": emp}, headers=token(client))
    assert r.status_code == 200, r.text
    return pr, r.json()["factura_id"]

def orm(fn):
    db = Session()
    try:
        return fn(db)
    finally:
        db.close()

def neto_pr(pr):
    from backend.remitos.models import RemitoItem
    def f(db):
        out = {}
        for it in db.query(RemitoItem).filter(RemitoItem.remito_id == uuid.UUID(pr["id"])).all():
            out[it.pedido_item_id] = (it.cantidad_facturada, it.cantidad_acreditada, it.cantidad_facturada_neta)
        return out
    return orm(f)

def flags(factura_id):
    return sql("SELECT flags_estado FROM facturas WHERE id = ?", (factura_id.replace("-", ""),))[0][0] or 0

# --- parche de _parsear para casos parciales/excedidos: {numero_completo: {"solo": [(idx_renglon, cantidad)], "total": x}}
OVERRIDES = {}
_real_parsear = conc_mod._parsear
def _parsear_parcheado(raw):
    parsed = _real_parsear(raw)
    ov = OVERRIDES.get(parsed["factura"].get("numero"))
    if not ov:
        return parsed
    items = []
    for idx, cant in ov["solo"]:
        it = dict(parsed["items"][idx]); it["cantidad"] = cant; it["subtotal"] = round(cant * (it.get("precio_unitario") or 0), 2)
        items.append(it)
    neto = sum(i["subtotal"] for i in items)
    iva = sum(i["subtotal"] * (i.get("alicuota_iva") or 0) / 100 for i in items)
    parsed = {**parsed, "items": items, "factura": {**parsed["factura"], "total_neto": round(neto, 2),
                                                    "total_final": ov.get("total", round(neto + iva, 2)),
                                                    **({"fecha_emision": ov["fecha"]} if "fecha" in ov else {})}}
    return parsed
conc_mod._parsear = _parsear_parcheado
aj_mod._parsear = _parsear_parcheado

# =========================================================== 1. camino feliz: NC total de la 2526
client = copia_fresca()
pr, fid = factura_2526(client)
check("Base: tabla facturas_ajustes existe y arranca vacia (create_all del arranque)", sql("SELECT COUNT(*) FROM facturas_ajustes")[0][0] == 0)
check("Base: la factura 2526 arranca sin bits 17-20", flags(fid) & (BIT_TIENE_NC | BIT_TIENE_ND | BIT_ES_NC | BIT_ES_ND) == 0)
base = neto_pr(pr)
check(f"Base: cantidad_facturada 3/1/1/2/2, acreditada 0, neta = facturada ({base})",
      {k: v for k, v in base.items()} == {40: (3.0, 0, 3.0), 41: (1.0, 0, 1.0), 42: (1.0, 0, 1.0), 43: (2.0, 0, 2.0), 44: (2.0, 0, 2.0)})

# Caso critico del dictamen: numero de NC IGUAL al de una factura existente (2526, pv 1) -> NO es duplicado
rid_igual, resp = subir(client, "NC_mismo_numero_que_factura.pdf", numero="00002526")
check("Upload de una NC cuyo numero coincide con una factura: NO muestra 'documento ya procesado'", resp["duplicado"]["encontrado"] is False)

rid, resp = subir(client, "NC_0001-00000101.pdf", numero="00000101")
check("Upload de NC nueva: sin duplicado", resp["duplicado"]["encontrado"] is False)

c = client.get(f"/ingesta/raw/{rid}/conciliacion/candidatos").json()
check("Candidatos de una NC: modo AJUSTE (no PR)", c["modo"] == "AJUSTE" and c["factura"]["tipo_comprobante"] == "NOTA_CREDITO_A")
check("Candidatos: sin bloqueos", c["bloqueos"] == [])
f_c = next((f for f in c["facturas"] if f["factura_id"] == fid), None)
check("Candidatos: ofrece la factura 2526 con 5 renglones", f_c is not None and len(f_c["renglones"]) == 5)
check("Candidatos: cada renglon trazable con 'disponible' = cantidad facturada (3/1/1/2/2)",
      f_c and [r["disponible"] for r in f_c["renglones"]] == [3.0, 1.0, 1.0, 2.0, 2.0] and all(r["trazable"] for r in f_c["renglones"]))
check("Candidatos: NO ofrece una NC como factura ajustable (ninguna NC en la lista)",
      all(not (f["tipo_comprobante"] or "").startswith("NOTA_CREDITO") for f in c["facturas"]))

ev0 = client.post(f"/ingesta/raw/{rid}/ajuste/evaluar", json={"factura_ids": []}).json()
check("NC sin factura -> bloqueo NC_SIN_FACTURA", any("NC_SIN_FACTURA" in b for b in ev0["bloqueos"]))

ev = client.post(f"/ingesta/raw/{rid}/ajuste/evaluar", json={"factura_ids": [fid]}).json()
sug = {e["item_pdf"]: (e["factura_item_id"], e.get("como")) for e in ev["emparejamiento"]}
check("Evaluar: sugiere los 5 pares por nombre", ev["emparejamiento_sugerido"] and all(v[0] is not None and v[1] == "nombre" for v in sug.values()) and len(sug) == 5)
check("Evaluar: sin bloqueos y sin Clase B/C", ev["bloqueos"] == [] and not any(d["clase"] in ("B", "C") for d in ev["diferencias"]))
check("Evaluar: Clase A informativa con tipo y numero de ARCA", any(d["clase"] == "A" and "NOTA_CREDITO_A" in d["detalle"] for d in ev["diferencias"]))
check("Evaluar: no filtra claves privadas (_facturas, _parsed...)", not any(k.startswith("_") for k in ev))
emp = ev["emparejamiento"]

r = client.post(f"/ingesta/raw/{rid}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": emp})
check("Confirmar NC SIN sesion -> 401", r.status_code == 401)
r = client.post(f"/ingesta/raw/{rid}/ajuste/confirmar", json={"factura_ids": [fid]}, headers=token(client))
check("Confirmar sin emparejamiento -> 400", r.status_code == 400)
r = client.post(f"/ingesta/raw/{rid}/ajuste/confirmar", json={"factura_ids": [], "emparejamiento": emp}, headers=token(client))
check("Confirmar NC sin facturas -> 409 y NO deja nada a medias", r.status_code == 409 and sql("SELECT COUNT(*) FROM facturas WHERE tipo_comprobante LIKE 'NOTA_%'")[0][0] == 0)
r = client.post(f"/ingesta/raw/{rid}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": emp}, headers=token(client))
check(f"Confirmar NC total con sesion -> 200 ({r.status_code})", r.status_code == 200)
nc1 = r.json()["factura_id"]

nota = sql("SELECT tipo_comprobante, estado, punto_venta, numero_comprobante, cae, cuit_comprador, total, neto_gravado FROM facturas WHERE id = ?", (nc1.replace("-", ""),))[0]
check(f"NC registrada como fila de facturas: {nota[:5]}", nota[0] == "NOTA_CREDITO_A" and nota[1] == "AUTORIZADA_AFIP" and nota[2] == 1 and nota[3] == 101 and nota[4])
check("Importes POSITIVOS como los manda ARCA (el signo lo da el tipo): neto 252350", nota[7] > 0 and abs(nota[7] - 252350.0) < 0.01 and nota[6] > 0)
aju = sql("SELECT factura_nc_nd_id, factura_ajustada_id, monto_aplicado FROM facturas_ajustes")
check(f"facturas_ajustes: 1 fila NC -> factura 2526, monto_aplicado = total de la NC ({aju})",
      len(aju) == 1 and aju[0][0] == nc1.replace("-", "") and aju[0][1] == fid.replace("-", "") and abs(aju[0][2] - nota[6]) < 0.01)
check("Bit ES_NC(19) prendido en la NC, sin TIENE_NC en ella", flags(nc1) & BIT_ES_NC and not flags(nc1) & BIT_TIENE_NC)
check("Bit TIENE_NC(17) prendido en la factura, TIENE_ND(18) apagado", flags(fid) & BIT_TIENE_NC and not flags(fid) & BIT_TIENE_ND)
check("Bit EXISTENCE (0) de la factura intacto (los toggles no pisan otros bits)", flags(fid) & 1)

despues = neto_pr(pr)
check(f"cantidad_facturada NO se muto (sigue 3/1/1/2/2) -- dictamen punto 3 ({ {k: v[0] for k, v in despues.items()} })",
      {k: v[0] for k, v in despues.items()} == {40: 3.0, 41: 1.0, 42: 1.0, 43: 2.0, 44: 2.0})
check(f"Acreditada 3/1/1/2/2 y neta 0 en los 5 renglones (calculada en la @property) ({despues})",
      all(v[1] == v[0] and v[2] == 0 for v in despues.values()))
nfi = sql("SELECT remito_item_id, pedido_item_id FROM facturas_items WHERE factura_id = ?", (nc1.replace("-", ""),))
check("Los 5 renglones de la NC apuntan a los MISMOS renglones de PR que la factura", len(nfi) == 5 and all(x[0] is not None for x in nfi))
check("Sin nota [SISTEMA] (no hubo Clase B)", sql("SELECT COUNT(*) FROM remitos_notas")[0][0] == 0)
check("Auditoria: FacturasProcesadas CONCILIADA_AJUSTE + raw PROCESADO",
      sql("SELECT COUNT(*) FROM ingesta_facturas_procesadas WHERE estado = 'CONCILIADA_AJUSTE'")[0][0] == 1
      and sql("SELECT audit_status FROM ingesta_facturas_raw WHERE id = ?", (rid.replace("-", ""),))[0][0] == "PROCESADO")

from backend.facturacion.models import Factura
def props(db):
    n = db.query(Factura).filter(Factura.id == uuid.UUID(nc1)).first()
    f = db.query(Factura).filter(Factura.id == uuid.UUID(fid)).first()
    return (str(n.comprobante_ajustado_principal.id), [str(x.id) for x in n.comprobantes_ajustados],
            len(f.ajustes_recibidos), len(f.ajustes_emitidos), len(n.ajustes_emitidos))
p = orm(props)
check(f"Propiedades del modelo: principal y lista apuntan a la factura; la factura ve 1 ajuste recibido ({p})",
      p[0] == fid and p[1] == [fid] and p[2] == 1 and p[3] == 0 and p[4] == 1)

# Duplicado: la MISMA NC (tipo, pv, numero) no entra dos veces
c2 = client.get(f"/ingesta/raw/{rid}/conciliacion/candidatos").json()
check("Re-intentar la misma NC -> bloqueo AJUSTE_DUPLICADO", any("AJUSTE_DUPLICADO" in b for b in c2["bloqueos"]))
r = client.post(f"/ingesta/raw/{rid}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": emp}, headers=token(client))
check("Confirmar la NC duplicada -> 409", r.status_code == 409 and sql("SELECT COUNT(*) FROM facturas_ajustes")[0][0] == 1)
c3 = client.get(f"/ingesta/raw/{rid_igual}/conciliacion/candidatos").json()
check("La NC con numero 2526 NO choca con la factura 2526 (ni con la NC 101): se puede conciliar", not any("DUPLICADO" in b for b in c3["bloqueos"]))
r = client.post(f"/ingesta/raw/{rid}/anular-y-reingestar", json={"pin": "1974", "factura_id": fid})
check("anular-y-reingestar de una factura CON notas vinculadas -> 409 FACTURA_CON_AJUSTES (no borra)",
      r.status_code == 409 and "FACTURA_CON_AJUSTES" in r.text and sql("SELECT COUNT(*) FROM facturas WHERE id = ?", (fid.replace("-", ""),))[0][0] == 1)
r = client.post(f"/ingesta/raw/{rid}/anular-y-reingestar", json={"pin": "1974", "factura_id": nc1})
check("anular-y-reingestar de la propia NC tambien -> 409", r.status_code == 409 and "FACTURA_CON_AJUSTES" in r.text)

# La factura 2526 ya NO es candidata a ser conciliada de nuevo, y una factura NC no se ofrece como ajustable
rid_b, _ = subir(client, "NC_0001-00000102.pdf", numero="00000102")
cb = client.get(f"/ingesta/raw/{rid_b}/conciliacion/candidatos").json()
check("Segunda NC: la lista de facturas ajustables no incluye la NC 101", all(f["factura_id"] != nc1 for f in cb["facturas"]))

# =========================================================== 2. parciales acumulativas y Clase B
client = copia_fresca()
pr, fid = factura_2526(client)
def nc_parcial(numero, idx_cant, total=None):
    """Sube y concilia una NC que acredita SOLO el renglon idx (la toalla, 3 unidades facturadas) por cant."""
    n = f"00001-{int(numero):08d}"
    OVERRIDES[n] = {"solo": [idx_cant], **({"total": total} if total is not None else {})}
    rid, _ = subir(client, f"NC_{numero}.pdf", numero=f"{int(numero):08d}")
    ev = client.post(f"/ingesta/raw/{rid}/ajuste/evaluar", json={"factura_ids": [fid]}).json()
    return rid, ev

rid1, ev1 = nc_parcial(201, (0, 1))
check("NC parcial (1 de 3 toallas): sugerido 1 par, sin Clase B", len(ev1["emparejamiento"]) == 1 and ev1["emparejamiento"][0]["factura_item_id"] and not any(d["clase"] == "B" for d in ev1["diferencias"]))
r = client.post(f"/ingesta/raw/{rid1}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": ev1["emparejamiento"]}, headers=token(client))
check("NC parcial confirma -> 200", r.status_code == 200)
n = neto_pr(pr)[40]
check(f"Toallas: facturada 3 (intacta), acreditada 1, neta 2 ({n})", n == (3.0, 1.0, 2.0))
check("Los otros 4 renglones no se movieron (neta = facturada)", all(v[2] == v[0] for k, v in neto_pr(pr).items() if k != 40))
mont = sql("SELECT monto_aplicado FROM facturas_ajustes")[0][0]
check(f"monto_aplicado de la parcial = total de esa NC, no el de la factura ({mont})", 0 < mont < 60000)

rid2, ev2 = nc_parcial(202, (0, 2))
check("Segunda NC parcial (2 mas): entra justo, sin Clase B (disponible era 2)", not any(d["clase"] == "B" for d in ev2["diferencias"]))
r = client.post(f"/ingesta/raw/{rid2}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": ev2["emparejamiento"]}, headers=token(client))
check("Segunda NC confirma -> 200 y neta de toallas = 0", r.status_code == 200 and neto_pr(pr)[40] == (3.0, 3.0, 0.0))
check("Factura con 2 NC: TIENE_NC sigue prendido, 2 filas de ajuste", flags(fid) & BIT_TIENE_NC and sql("SELECT COUNT(*) FROM facturas_ajustes")[0][0] == 2)

rid3, ev3 = nc_parcial(203, (0, 1))
b3 = [d for d in ev3["diferencias"] if d["clase"] == "B"]
check(f"Tercera NC (ya no queda nada por acreditar): Clase B 'acreditó de más' pero NO bloquea ({len(b3)})", len(b3) >= 1 and ev3["bloqueos"] == [])
r = client.post(f"/ingesta/raw/{rid3}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": ev3["emparejamiento"]}, headers=token(client))
check("Clase B concilia igual (decision Carlos 28/09) -> 200", r.status_code == 200)
notas_sis = sql("SELECT texto FROM remitos_notas WHERE texto LIKE '[SISTEMA]%'")
check(f"Nota [SISTEMA] en el PR del renglón acreditado de más ({len(notas_sis)})", len(notas_sis) == 1 and "NOTA_CREDITO_A" in notas_sis[0][0])
n = neto_pr(pr)[40]
check(f"El neto refleja la verdad aunque sea absurda: acreditada 4 de 3 facturadas, neta -1 ({n})", n == (3.0, 4.0, -1.0))

# NC por mas plata que la factura
client = copia_fresca()
pr, fid = factura_2526(client)
OVERRIDES["00001-00000301"] = {"solo": [(0, 1)], "total": 999999999.0}
rid, _ = subir(client, "NC_301.pdf", numero="00000301")
ev = client.post(f"/ingesta/raw/{rid}/ajuste/evaluar", json={"factura_ids": [fid]}).json()
check("NC por mas que el total de la factura -> Clase B de importe (no bloquea)",
      any(d["clase"] == "B" and "acreditó de más" in d["detalle"] and d.get("item_pdf") is None for d in ev["diferencias"]) and ev["bloqueos"] == [])

# =========================================================== 2b. fecha de emision de la NC: la de ARCA si se lee; si no, hoy
import datetime as _dt
OVERRIDES["00001-00000801"] = {"solo": [(0, 1)], "fecha": "2026-05-15"}
rid_f, _ = subir(client, "NC_801.pdf", numero="00000801")
evf = client.post(f"/ingesta/raw/{rid_f}/ajuste/evaluar", json={"factura_ids": [fid]}).json()
check("Fecha leida de ARCA: la Clase A la informa", "2026-05-15" in evf["diferencias"][-1]["detalle"])
r = client.post(f"/ingesta/raw/{rid_f}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": evf["emparejamiento"]}, headers=token(client))
check("NC con fecha de ARCA: se registra con esa fecha, no la de carga",
      r.status_code == 200 and str(sql("SELECT fecha_emision FROM facturas WHERE id = ?", (r.json()["factura_id"].replace("-", ""),))[0][0]).startswith("2026-05-15"))
rid_nf, _ = subir(client, "NC_802.pdf", numero="00000802")   # el PDF sintetico pierde la fecha (orden de texto)
evn = client.post(f"/ingesta/raw/{rid_nf}/ajuste/evaluar", json={"factura_ids": [fid]}).json()
check("Fecha ilegible: la Clase A lo avisa ('se usa hoy')", "fecha ilegible" in evn["diferencias"][-1]["detalle"])
r = client.post(f"/ingesta/raw/{rid_nf}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": evn["emparejamiento"]}, headers=token(client))
check("NC sin fecha legible: se registra con la fecha de hoy",
      r.status_code == 200 and str(sql("SELECT fecha_emision FROM facturas WHERE id = ?", (r.json()["factura_id"].replace("-", ""),))[0][0]).startswith(str(_dt.date.today())))

# =========================================================== 3. renglon de NC sin par = concepto de solo monto
client = copia_fresca()
pr, fid = factura_2526(client)
rid, _ = subir(client, "NC_401.pdf", numero="00000401")
ev = client.post(f"/ingesta/raw/{rid}/ajuste/evaluar", json={"factura_ids": [fid]}).json()
emp_concepto = [{"item_pdf": i, "factura_item_id": (None if i == 4 else e["factura_item_id"])} for i, e in enumerate(ev["emparejamiento"])]
ev_c = client.post(f"/ingesta/raw/{rid}/ajuste/evaluar", json={"factura_ids": [fid], "emparejamiento": emp_concepto}).json()
check("Un renglon de NC sin par -> INFO 'concepto de solo monto' (no B, no bloquea)",
      any(d["clase"] == "INFO" and d.get("item_pdf") == 4 for d in ev_c["diferencias"]) and not any(d["clase"] == "B" for d in ev_c["diferencias"]) and ev_c["bloqueos"] == [])
ev_inc = client.post(f"/ingesta/raw/{rid}/ajuste/evaluar", json={"factura_ids": [fid], "emparejamiento": emp_concepto[:4]}).json()
check("Emparejamiento incompleto -> bloqueo EMPAREJAMIENTO_INCOMPLETO", any("EMPAREJAMIENTO_INCOMPLETO" in b for b in ev_inc["bloqueos"]))
emp_mal = [dict(e) for e in emp_concepto]; emp_mal[1]["factura_item_id"] = emp_mal[0]["factura_item_id"]
ev_mal = client.post(f"/ingesta/raw/{rid}/ajuste/evaluar", json={"factura_ids": [fid], "emparejamiento": emp_mal}).json()
check("Mismo renglon de factura usado dos veces -> bloqueo EMPAREJAMIENTO_INVALIDO", any("usado dos veces" in b for b in ev_mal["bloqueos"]))
r = client.post(f"/ingesta/raw/{rid}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": emp_concepto}, headers=token(client))
check("Confirma con un concepto sin par -> 200", r.status_code == 200)
nn = neto_pr(pr)
check(f"El concepto no movio cantidades: los 4 pares acreditan, el renglon 44 queda neto 2 ({nn[44]})", nn[44] == (2.0, 0, 2.0) and nn[40][2] == 0)
nfi = sql("SELECT remito_item_id FROM facturas_items WHERE factura_id = ?", (r.json()["factura_id"].replace("-", ""),))
check("El renglon concepto de la NC queda con remito_item_id NULL", sum(1 for x in nfi if x[0] is None) == 1)

# =========================================================== 4. ND: suelta y con factura; una ND no mueve cantidades
client = copia_fresca()
pr, fid = factura_2526(client)
rid_nd, resp = subir(client, "ND_0001-00000501.pdf", leyenda="NOTA DE DEBITO", cod="02", numero="00000501")
c = client.get(f"/ingesta/raw/{rid_nd}/conciliacion/candidatos").json()
check("Candidatos de una ND: modo AJUSTE, aviso ND_PUEDE_IR_SUELTA, sin bloqueos",
      c["modo"] == "AJUSTE" and c["factura"]["tipo_comprobante"] == "NOTA_DEBITO_A" and any("ND_PUEDE_IR_SUELTA" in a for a in c["avisos"]) and c["bloqueos"] == [])
ev = client.post(f"/ingesta/raw/{rid_nd}/ajuste/evaluar", json={"factura_ids": []}).json()
check("ND suelta: evalua sin bloqueos (a diferencia de la NC)", ev["bloqueos"] == [] and ev["cliente_id"])
r = client.post(f"/ingesta/raw/{rid_nd}/ajuste/confirmar", json={"factura_ids": [], "emparejamiento": []}, headers=token(client))
check(f"ND suelta confirma -> 200 ({r.status_code})", r.status_code == 200)
nd1 = r.json()["factura_id"]
fila = sql("SELECT factura_ajustada_id, monto_aplicado FROM facturas_ajustes WHERE factura_nc_nd_id = ?", (nd1.replace("-", ""),))
check(f"ND suelta: fila con factura_ajustada_id NULL ({fila})", fila == [(None, None)])
check("ND suelta: ES_ND(20) prendido, TIENE_ND no (no es factura ajustada), la factura 2526 no se toco",
      flags(nd1) & BIT_ES_ND and not flags(nd1) & BIT_TIENE_ND and not flags(fid) & (BIT_TIENE_NC | BIT_TIENE_ND))
def prop_suelta(db):
    n = db.query(Factura).filter(Factura.id == uuid.UUID(nd1)).first()
    return n.comprobante_ajustado_principal, n.comprobantes_ajustados
check("ND suelta: comprobante_ajustado_principal None y comprobantes_ajustados vacia (sin reventar por el NULL)", orm(prop_suelta) == (None, []))
check("ND no mueve cantidades: neto del PR intacto", all(v[1] == 0 and v[2] == v[0] for v in neto_pr(pr).values()))
check("ND: sus renglones no se atan a ningun renglon de PR", all(x[0] is None for x in sql("SELECT remito_item_id FROM facturas_items WHERE factura_id = ?", (nd1.replace("-", ""),))))

rid_nd2, _ = subir(client, "ND_0001-00000502.pdf", leyenda="NOTA DE DEBITO", cod="02", numero="00000502")
r = client.post(f"/ingesta/raw/{rid_nd2}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": []}, headers=token(client))
check("ND asociada a la factura 2526 -> 200", r.status_code == 200)
nd2 = r.json()["factura_id"]
check("Factura 2526: TIENE_ND(18) prendido y TIENE_NC(17) sigue apagado (bits independientes)", flags(fid) & BIT_TIENE_ND and not flags(fid) & BIT_TIENE_NC)
check("ND asociada: monto_aplicado = total de la ND", abs(sql("SELECT monto_aplicado FROM facturas_ajustes WHERE factura_nc_nd_id = ?", (nd2.replace("-", ""),))[0][0] - sql("SELECT total FROM facturas WHERE id = ?", (nd2.replace("-", ""),))[0][0]) < 0.01)
# una NC puede ajustar una ND (y no al reves): la NC contra la ND
OVERRIDES["00001-00000601"] = {"solo": [(0, 1)]}
rid_ncnd, _ = subir(client, "NC_601.pdf", numero="00000601")
cn = client.get(f"/ingesta/raw/{rid_ncnd}/conciliacion/candidatos").json()
check("Una ND SI es ajustable por una NC (aparece en la lista de facturas ajustables)", any(f["factura_id"] == nd2 for f in cn["facturas"]))

# =========================================================== 5. Clase C y bloqueos
evC = client.post(f"/ingesta/raw/{rid_ncnd}/ajuste/evaluar", json={"factura_ids": [fid]}).json()
con = sqlite3.connect(SCRATCH)
con.execute("UPDATE facturas SET cuit_comprador = '20111111112' WHERE id = ?", (fid.replace("-", ""),)); con.commit(); con.close()
evC = client.post(f"/ingesta/raw/{rid_ncnd}/ajuste/evaluar", json={"factura_ids": [fid]}).json()
check("CUIT de la factura distinto al de la NC -> Clase C y BLOQUEA (compara por CUIT)",
      any(d["clase"] == "C" for d in evC["diferencias"]) and any("CLASE_C" in b for b in evC["bloqueos"]))
r = client.post(f"/ingesta/raw/{rid_ncnd}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": evC["emparejamiento"]}, headers=token(client))
check("Confirmar en Clase C -> 409 y nada a medias", r.status_code == 409 and sql("SELECT COUNT(*) FROM facturas WHERE numero_comprobante = 601")[0][0] == 0)
evX = client.post(f"/ingesta/raw/{rid_ncnd}/ajuste/evaluar", json={"factura_ids": [str(uuid.uuid4())]}).json()
check("Factura inexistente -> bloqueo FACTURA_INEXISTENTE", any("FACTURA_INEXISTENTE" in b for b in evX["bloqueos"]))
evNC = client.post(f"/ingesta/raw/{rid_ncnd}/ajuste/evaluar", json={"factura_ids": [nd1]}).json()
check("Evaluar una NC contra una ND de otro origen funciona (ND ajustable)", not any("AJUSTADA_ES_NC" in b for b in evNC["bloqueos"]))

# Un PDF de FACTURA por el flujo de ajuste
rid_f = uid(sql("SELECT id FROM ingesta_facturas_raw WHERE filename LIKE '%00002526%' LIMIT 1")[0][0])
evF = client.post(f"/ingesta/raw/{rid_f}/ajuste/evaluar", json={"factura_ids": [fid]}).json()
check("Un PDF de FACTURA por el flujo de ajuste -> bloqueo NO_ES_AJUSTE", any("NO_ES_AJUSTE" in b for b in evF["bloqueos"]))
# ...y una NC por el flujo de PR (7b) sigue bloqueada
cnc = conc_mod.ConciliadorService
check("Una NC por el evaluar de 7b sigue bloqueada (ES_AJUSTE)", any("ES_AJUSTE" in b for b in client.post(f"/ingesta/raw/{rid_ncnd}/conciliacion/evaluar", json={"remito_ids": []}).json()["bloqueos"]))

# =========================================================== 6. FacturacionService: validaciones, revertir, bits
client = copia_fresca()
pr, fid = factura_2526(client)
from backend.facturacion.service import FacturacionService
from backend.facturacion import models as fmodels
db = Session()
F = db.query(Factura).filter(Factura.id == uuid.UUID(fid)).first()
def nueva_nota(tipo, numero, cliente_id=None):
    n = Factura(cliente_id=cliente_id or F.cliente_id, tipo_comprobante=tipo, estado="AUTORIZADA_AFIP", punto_venta=1,
                numero_comprobante=numero, neto_gravado=100.0, total=121.0)
    db.add(n); db.flush(); return n
def falla(fn, codigo):
    try:
        fn()
    except HTTPException as e:
        return e.status_code == 409 and codigo in str(e.detail)
    return False

NC = nueva_nota("NOTA_CREDITO_A", 9001)
check("registrar_ajuste: un tipo que no es NC/ND -> AJUSTE_TIPO_INVALIDO", falla(lambda: FacturacionService.registrar_ajuste(db, F, [{"factura_id": fid}]), "AJUSTE_TIPO_INVALIDO"))
check("registrar_ajuste: NC sin factura -> NC_SIN_FACTURA", falla(lambda: FacturacionService.registrar_ajuste(db, NC, []), "NC_SIN_FACTURA"))
check("registrar_ajuste: factura inexistente -> AJUSTADA_INEXISTENTE", falla(lambda: FacturacionService.registrar_ajuste(db, NC, [{"factura_id": str(uuid.uuid4())}]), "AJUSTADA_INEXISTENTE"))
check("registrar_ajuste: id invalido -> AJUSTADA_INEXISTENTE (no un 500)", falla(lambda: FacturacionService.registrar_ajuste(db, NC, [{"factura_id": "no-es-uuid"}]), "AJUSTADA_INEXISTENTE"))
check("registrar_ajuste: ajustarse a si misma -> AJUSTADA_ES_LA_MISMA", falla(lambda: FacturacionService.registrar_ajuste(db, NC, [{"factura_id": NC.id}]), "AJUSTADA_ES_LA_MISMA"))
NC2 = nueva_nota("NOTA_CREDITO_A", 9002)
check("registrar_ajuste: ajustar una NC -> AJUSTADA_ES_NC", falla(lambda: FacturacionService.registrar_ajuste(db, NC, [{"factura_id": NC2.id}]), "AJUSTADA_ES_NC"))
otro_cliente = db.query(fmodels.Factura.cliente_id).filter(fmodels.Factura.cliente_id != F.cliente_id).first()
if otro_cliente is None:
    from backend.clientes.models import Cliente
    otro_cliente = (db.query(Cliente.id).filter(Cliente.id != F.cliente_id).first())
G = nueva_nota("FACTURA_A", 9003, cliente_id=otro_cliente[0])
check("registrar_ajuste: factura de OTRO cliente -> CLIENTE_DISTINTO", falla(lambda: FacturacionService.registrar_ajuste(db, NC, [{"factura_id": G.id}]), "CLIENTE_DISTINTO"))
ANUL = nueva_nota("FACTURA_A", 9004); ANUL.estado = "ANULADA"; db.flush()
check("registrar_ajuste: factura ANULADA -> AJUSTADA_ANULADA", falla(lambda: FacturacionService.registrar_ajuste(db, NC, [{"factura_id": ANUL.id}]), "AJUSTADA_ANULADA"))
check("registrar_ajuste: la misma factura dos veces en la lista -> AJUSTE_DUPLICADO", falla(lambda: FacturacionService.registrar_ajuste(db, NC, [{"factura_id": F.id}, {"factura_id": F.id}]), "AJUSTE_DUPLICADO"))
check("Las validaciones que fallaron no dejaron filas ni bits (nada se escribe antes de validar todo)",
      db.query(fmodels.FacturaAjuste).count() == 0 and not (F.flags_estado or 0) & (BIT_TIENE_NC | BIT_TIENE_ND))

filas = FacturacionService.registrar_ajuste(db, NC, [{"factura_id": F.id, "monto_aplicado": 50.0}])
check("registrar_ajuste feliz: 1 fila, monto_aplicado respetado", len(filas) == 1 and filas[0].monto_aplicado == 50.0)
check("registrar_ajuste feliz: bits ES_NC en la NC y TIENE_NC en la factura", (NC.flags_estado & BIT_ES_NC) and (F.flags_estado & BIT_TIENE_NC))
check("registrar_ajuste: la misma NC contra la misma factura otra vez -> AJUSTE_DUPLICADO (ya vinculada)", falla(lambda: FacturacionService.registrar_ajuste(db, NC, [{"factura_id": F.id}]), "AJUSTE_DUPLICADO"))

# una NC que ajusta VARIAS facturas (caso de ARCA)
F2 = nueva_nota("FACTURA_A", 9005)
NCM = nueva_nota("NOTA_CREDITO_A", 9006)
filas = FacturacionService.registrar_ajuste(db, NCM, [{"factura_id": F.id, "monto_aplicado": 10.0}, {"factura_id": F2.id, "monto_aplicado": 20.0}])
check("Una NC que ajusta 2 facturas: 2 filas, ambas facturas con TIENE_NC", len(filas) == 2 and (F.flags_estado & BIT_TIENE_NC) and (F2.flags_estado & BIT_TIENE_NC))
check("comprobantes_ajustados de la NC multiple devuelve las 2 facturas", {x.id for x in NCM.comprobantes_ajustados} == {F.id, F2.id})

# revertir
fila_ncm_f2 = next(a for a in filas if a.factura_ajustada_id == F2.id)
FacturacionService.revertir_ajuste(db, fila_ncm_f2.id)
check("revertir_ajuste: F2 vuelve a TIENE_NC apagado (ya no la ajusta nadie)", not (F2.flags_estado or 0) & BIT_TIENE_NC)
check("revertir_ajuste: F conserva TIENE_NC (la NC de 9001 y la multiple siguen)", F.flags_estado & BIT_TIENE_NC)
check("revertir_ajuste: la NC multiple SIGUE siendo NC (ES_NC no se apaga)", NCM.flags_estado & BIT_ES_NC)
for a in list(F.ajustes_recibidos):
    FacturacionService.revertir_ajuste(db, a.id)
check("revertir_ajuste: sin ninguna NC vigente, F apaga TIENE_NC", not (F.flags_estado or 0) & BIT_TIENE_NC)
try:
    FacturacionService.revertir_ajuste(db, 999999); ok404 = False
except HTTPException as e:
    ok404 = e.status_code == 404
check("revertir_ajuste de un id inexistente -> 404 (real)", ok404)

# NC anulada: no cuenta como vigente para TIENE_NC ni para el neto
FacturacionService.registrar_ajuste(db, NC, [{"factura_id": F.id}])
check("Re-vinculada: TIENE_NC prendido de nuevo", F.flags_estado & BIT_TIENE_NC)
NC.estado = "ANULADA"; db.flush()
FacturacionService.sincronizar_bits_ajuste(db, F)
check("Una NC ANULADA no cuenta: sincronizar_bits_ajuste apaga TIENE_NC en la factura", not (F.flags_estado or 0) & BIT_TIENE_NC)
check("sincronizar_bits_ajuste es idempotente (dos llamadas no cambian nada)", (lambda a: (FacturacionService.sincronizar_bits_ajuste(db, F), F.flags_estado == a)[1])(F.flags_estado))
# ND con tipo distinto de letra: A/B/C se reconocen por prefijo
NDB = nueva_nota("NOTA_DEBITO_B", 9007)
FacturacionService.registrar_ajuste(db, NDB, [])
check("ND letra B tambien prende ES_ND (se reconoce por prefijo, no por letra)", NDB.flags_estado & BIT_ES_ND)
db.rollback(); db.close()

# =========================================================== 7. NC anulada baja el neto del PR
client = copia_fresca()
pr, fid = factura_2526(client)
rid, _ = subir(client, "NC_701.pdf", numero="00000701")
ev = client.post(f"/ingesta/raw/{rid}/ajuste/evaluar", json={"factura_ids": [fid]}).json()
r = client.post(f"/ingesta/raw/{rid}/ajuste/confirmar", json={"factura_ids": [fid], "emparejamiento": ev["emparejamiento"]}, headers=token(client))
nc = r.json()["factura_id"]
check("Antes de anular: neto 0 en todos los renglones", all(v[2] == 0 for v in neto_pr(pr).values()))
con = sqlite3.connect(SCRATCH); con.execute("UPDATE facturas SET estado='ANULADA' WHERE id = ?", (nc.replace("-", ""),)); con.commit(); con.close()
check("NC ANULADA: el neto vuelve a ser la cantidad facturada (la @property la ignora)", all(v[1] == 0 and v[2] == v[0] for v in neto_pr(pr).values()))

# =========================================================== 8. migracion 045
copia = r"C:\dev\Sonido_Liquido_V5\scratch\pilot_v5x_mig045.db"
copiar_p("pilot_v5x.db", copia)
con = sqlite3.connect(copia); con.execute("DROP TABLE IF EXISTS facturas_ajustes"); con.execute("DELETE FROM _migraciones_aplicadas WHERE id='045_facturas_ajustes'"); con.commit(); con.close()
env = {**os.environ, "DATABASE_URL": f"sqlite:///{copia}"}
def mig():
    return subprocess.run([sys.executable, "scripts/migrate_045_facturas_ajustes.py"], env=env, capture_output=True, text=True, cwd=r"C:\dev\Sonido_Liquido_V5")
p1, p2 = mig(), mig()
con = sqlite3.connect(copia)
cols = [r[1] for r in con.execute("PRAGMA table_info(facturas_ajustes)")]
idx = [r[1] for r in con.execute("PRAGMA index_list(facturas_ajustes)")]
regs = con.execute("SELECT COUNT(*) FROM _migraciones_aplicadas WHERE id='045_facturas_ajustes'").fetchone()[0]
con.close()
check("Migracion 045: primera corrida OK", p1.returncode == 0 and "OK" in p1.stdout)
check("Migracion 045: segunda corrida SKIP (idempotente) y registrada una sola vez", p2.returncode == 0 and "SKIP" in p2.stdout and regs == 1)
check(f"Migracion 045: columnas del modelo ({cols})", cols == ["id", "factura_nc_nd_id", "factura_ajustada_id", "monto_aplicado", "fecha_vinculo"])
check(f"Migracion 045: 3 indices + el unique ({len(idx)})", len(idx) >= 4)
con = sqlite3.connect(copia)
con.execute("DROP TABLE facturas_ajustes"); con.commit(); con.close()
con = sqlite3.connect(copia)
con.execute("DELETE FROM _migraciones_aplicadas WHERE id='045_facturas_ajustes'"); con.commit(); con.close()
# la tabla del migrate y la del create_all deben ser la misma: create_all primero, migrate despues
eng2 = create_engine(f"sqlite:///{copia}")
from backend.core.database import Base
Base.metadata.create_all(eng2)
p3 = mig()
check("Migracion 045 despues de create_all (orden inverso): no falla y se registra", p3.returncode == 0)
eng2.dispose()

# =========================================================== 9. la base viva no se toco
live = sqlite3.connect("pilot_v5x.db")
conteos = {t: live.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("pedidos", "pedidos_items", "remitos", "remitos_items", "facturas", "facturas_remitos", "ingesta_facturas_procesadas", "remitos_notas")}
tiene_tabla = live.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='facturas_ajustes'").fetchone()[0]
live.close()
print(f"(info) tabla facturas_ajustes en la base viva: {tiene_tabla} -- la crea el arranque del backend, no los tests")
check(f"Base VIVA sin tocar: 47/80/16/31/14/9/4/0 ({conteos})",
      list(conteos.values()) == [47, 80, 16, 31, 14, 9, 4, 0])

fallos = [d for d, ok in checks if not ok]
print(f"\n{len(checks) - len(fallos)}/{len(checks)} checks OK")
for d in fallos:
    print("FALLO:", d)
sys.exit(1 if fallos else 0)
