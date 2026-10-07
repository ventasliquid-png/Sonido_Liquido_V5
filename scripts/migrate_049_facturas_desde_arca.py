"""
migrate_049_facturas_desde_arca.py
==================================
Auditoria de facturas (S881, idea de Carlos 07/10; Cards #161, #163, #164): corrige en V5 las facturas con CAE para que coincidan con el
PDF que emitio ARCA: tipo de comprobante (eran Factura A y estaban como B o presupuesto X), fecha de emision, vencimiento del CAE, neto, IVA y
total (V5 guardaba el neto como total) y, cuando la lectura del PDF cierra con el total impreso, los renglones (con su enlace al renglon del
pedido). Las correcciones salen de `scripts/auditoria_facturas.py --generar-correcciones` y viajan en `scripts/data/correcciones_facturas_s881.json`.

Por que una migracion y no un script contra la base de P: no se escribe SQLite de P por la red mientras el servidor corre; las migraciones
se aplican al arrancar Soberana, despues del backup previo de auto_migrar, y quedan registradas.

Seguridad (cada factura por separado, con SAVEPOINT):
  - Solo se toca si la factura existe con el mismo (punto de venta, numero, CAE) y SIGUE como la audito el 06/10 (tipo, total, neto, cantidad y suma
    de renglones). Si cambio desde entonces, o no coincide, se SALTA y se informa: nunca se pisa algo que no se reconoce.
  - No cambia el ESTADO, ni los flags, ni el pedido: solo los campos de la factura y, cuando corresponde, sus renglones.
  - Si el renglon viejo tenia remito_item_id, se conservan los renglones (solo se corrigen cabecera y totales).
  - Idempotente: una factura ya corregida se reconoce y se saltea; ademas queda registrada en _migraciones_aplicadas.
  - Un error en una factura no frena el arranque: se informa y se sigue (sale siempre con codigo 0 salvo que falte la tabla).

MIGRATION_ID = "049_facturas_desde_arca"
NRO_SESION = 881
"""
import json
import os
import sqlite3

MIGRATION_ID = "049_facturas_desde_arca"
NRO_SESION = 881

AQUI = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(AQUI, "..", "pilot_v5x.db")
JSON_PATH = os.path.join(AQUI, "data", "correcciones_facturas_s881.json")
TOL = 0.011

conn = sqlite3.connect(DB_PATH, isolation_level=None)  # transacciones a mano (SAVEPOINT por factura)
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (
        id VARCHAR PRIMARY KEY,
        nro_sesion INTEGER,
        aplicada_en DATETIME DEFAULT (datetime('now'))
    )
""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_049] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)

if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='facturas'").fetchone():
    print("[migrate_049] ERROR -- no existe la tabla 'facturas': no es una base de V5.")
    conn.close()
    raise SystemExit(1)
if not os.path.exists(JSON_PATH):
    print(f"[migrate_049] AVISO -- falta {JSON_PATH}: no se corrige nada y la migracion NO se registra (se reintenta en el proximo arranque).")
    conn.close()
    raise SystemExit(0)

correcciones = json.load(open(JSON_PATH, encoding="utf-8"))["correcciones"]
print(f"[migrate_049] Iniciando {MIGRATION_ID}: {len(correcciones)} factura(s) a contrastar con ARCA...")
aplicadas, ya, saltadas, errores = [], [], [], []

for c in correcciones:
    etiqueta = f"{c['pv']:05d}-{c['numero']:08d}"
    try:
        cur.execute("SAVEPOINT corr")
        fila = cur.execute("""SELECT id, tipo_comprobante, total, neto_gravado, notas_auditoria FROM facturas
                              WHERE punto_venta = ? AND numero_comprobante = ? AND trim(cae) = ?""", (c["pv"], c["numero"], c["cae"])).fetchone()
        if fila is None:
            saltadas.append((etiqueta, "no existe con ese CAE"))
            cur.execute("RELEASE corr"); continue
        fid, tipo, total, neto, notas = fila
        items_v5 = cur.execute("SELECT id, subtotal_neto, remito_item_id FROM facturas_items WHERE factura_id = ?", (fid,)).fetchall()
        d, antes = c["despues"], c["antes"]
        # ¿ya esta corregida?
        if tipo == d["tipo"] and (d.get("total") is None or (total is not None and abs(total - d["total"]) <= TOL)):
            ya.append(etiqueta); cur.execute("RELEASE corr"); continue
        # ¿sigue como la audito el 06/10?
        suma = round(sum((r[1] or 0.0) for r in items_v5), 2)
        igual = (tipo == antes["tipo"] and abs((total or 0.0) - (antes["total"] or 0.0)) <= TOL
                 and abs((neto or 0.0) - (antes["neto"] or 0.0)) <= TOL and len(items_v5) == antes["n_items"] and abs(suma - antes["suma_items"]) <= TOL)
        if not igual:
            saltadas.append((etiqueta, "cambio desde la auditoria del 06/10 (tipo/total/renglones distintos): no se toca"))
            cur.execute("RELEASE corr"); continue
        if tipo != d["tipo"] and cur.execute("SELECT 1 FROM facturas WHERE tipo_comprobante = ? AND punto_venta = ? AND numero_comprobante = ? AND id != ?",
                                              (d["tipo"], c["pv"], c["numero"], fid)).fetchone():
            saltadas.append((etiqueta, f"ya existe otra factura {d['tipo']} con ese numero (UNIQUE)"))
            cur.execute("RELEASE corr"); continue
        campos = {"tipo_comprobante": d["tipo"], "fecha_emision": d["fecha"], "cae_vencimiento": d["vto"]}
        if d.get("total") is not None:
            campos.update({"neto_gravado": d["neto_gravado"], "exento": d["exento"], "iva_21": d["iva_21"], "iva_105": d["iva_105"], "total": d["total"]})
        marca = f"[SISTEMA] Corregida desde el PDF de ARCA (S881, migrate_049): tipo {tipo} -> {d['tipo']}, total {total} -> {d.get('total', total)}."
        campos["notas_auditoria"] = ((notas + " | ") if notas else "") + marca
        sets = ", ".join(f"{k} = ?" for k in campos)
        cur.execute(f"UPDATE facturas SET {sets} WHERE id = ?", (*campos.values(), fid))
        reemplazo = c["items"] is not None
        if reemplazo and any(r[2] is not None for r in items_v5):
            reemplazo = False  # algun renglon viejo esta enlazado a un renglon de remito: no se tocan los renglones
        if reemplazo:
            cur.execute("DELETE FROM facturas_items WHERE factura_id = ?", (fid,))
            for it in c["items"]:
                cur.execute("""INSERT INTO facturas_items (factura_id, pedido_item_id, remito_item_id, descripcion, cantidad, precio_unitario_neto, alicuota_iva, subtotal_neto)
                               VALUES (?, ?, NULL, ?, ?, ?, ?, ?)""", (fid, it["pedido_item_id"], it["descripcion"], it["cantidad"], it["precio"], it["alicuota"], it["subtotal"]))
        aplicadas.append((etiqueta, "cabecera+totales+renglones" if reemplazo else "cabecera+totales (renglones sin tocar)"))
        cur.execute("RELEASE corr")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO corr"); cur.execute("RELEASE corr")
        errores.append((etiqueta, f"{type(e).__name__}: {e}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_049] OK -- corregidas {len(aplicadas)}, ya estaban {len(ya)}, saltadas {len(saltadas)}, con error {len(errores)}; {MIGRATION_ID} registrada.")
for e, m in aplicadas:
    if "sin tocar" in m:
        print(f"[migrate_049]   {e}: {m} -- revisar los renglones a mano (Card #144)")
for e, m in saltadas:
    print(f"[migrate_049] AVISO -- {e}: {m}")
for e, m in errores:
    print(f"[migrate_049] ERROR -- {e}: {m} (esa factura quedo como estaba)")
conn.close()
