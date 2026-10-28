"""
migrate_070_iva_facturas_bonificadas.py
=======================================
Card #164 (S894, 28/10/2026): con una bonificacion en la factura, el IVA quedaba calculado sobre los renglones SIN bonificar.
El parser lee cada renglon como cantidad x precio (sin el % de bonificacion) y backend/ingesta/conciliador.py::desglose_importes
multiplicaba esos subtotales por la alicuota; el neto y el total, que los manda ARCA, estaban bien, asi que las percepciones
(lo que sobra hasta el total) quedaban NEGATIVAS. Caso real en P: Wullich 2616, 2617 y 2620 (bonificacion del 5 %, cargadas del
15 al 22/10); en la 2616 V5 guardaba IVA 876.960 y ARCA imprime 833.112. El codigo ya se corrigio (la base de cada alicuota se
lleva al neto de ARCA en proporcion); esta migracion corrige las que ya quedaron asi.

QUE HACE: para cada factura o nota con CAE y percepciones negativas, toma la base de cada alicuota de sus renglones, la lleva al
neto gravado de la factura en proporcion y recalcula IVA 21 %, IVA 10,5 % y percepciones. Solo corrige si el resultado cierra el
total sin percepciones negativas; si no, informa y deja la factura como estaba. Nota [SISTEMA] en notas_auditoria.
QUE NO HACE: no toca neto, total, renglones, estado, pedidos ni remitos (los renglones sin bonificar son la Card #144).

SEGURIDAD: SAVEPOINT por factura, despues del backup de auto_migrar; idempotente (registro en _migraciones_aplicadas y el
criterio de percepciones negativas); sale 0.

MIGRATION_ID = "070_iva_facturas_bonificadas"
NRO_SESION = 894
"""
import os
import sqlite3

MIGRATION_ID = "070_iva_facturas_bonificadas"
NRO_SESION = 894
EPS = 0.5

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_070] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("facturas", "facturas_items"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_070] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)

candidatas = cur.execute("""SELECT id, punto_venta, numero_comprobante, neto_gravado, iva_21, iva_105, exento, percepciones, total, notas_auditoria
                            FROM facturas WHERE cae IS NOT NULL AND trim(cae) != '' AND percepciones < ?""", (-EPS,)).fetchall()
print(f"[migrate_070] Iniciando {MIGRATION_ID}: {len(candidatas)} comprobante(s) con CAE y percepciones negativas a revisar...")
corregidas, saltadas, errores = [], [], []
for fid, pv, nc, neto, iva21_v5, iva105_v5, exento, percep_v5, total, notas in candidatas:
    etiqueta = f"{(pv or 0):05d}-{(nc or 0):08d}"
    try:
        cur.execute("SAVEPOINT fac")
        renglones = cur.execute("SELECT subtotal_neto, alicuota_iva FROM facturas_items WHERE factura_id = ?", (fid,)).fetchall()
        alic = [(s or 0.0, 21.0 if a is None else a) for s, a in renglones]
        base_21 = sum(s for s, a in alic if abs(a - 21) < 0.01)
        base_105 = sum(s for s, a in alic if abs(a - 10.5) < 0.01)
        gravado = sum(s for s, a in alic if abs(a) >= 0.01)
        if neto is None or total is None or gravado <= EPS:
            saltadas.append((etiqueta, "sin neto, sin total o sin renglones gravados")); cur.execute("RELEASE fac"); continue
        iva21 = round(base_21 * neto / gravado * 0.21, 2)
        iva105 = round(base_105 * neto / gravado * 0.105, 2)
        percep = round(total - neto - iva21 - iva105 - (exento or 0.0), 2)
        if abs(percep) < EPS:
            percep = 0.0
        if percep < 0:
            saltadas.append((etiqueta, f"con el IVA prorrateado las percepciones siguen negativas ({percep}): no cierra, queda como estaba")); cur.execute("RELEASE fac"); continue
        marca = (f"[SISTEMA] IVA recalculado sobre el neto bonificado de ARCA (S894, migrate_070, Card #164): IVA 21 % {iva21_v5} -> {iva21}, "
                 f"IVA 10,5 % {iva105_v5} -> {iva105}, percepciones {percep_v5} -> {percep}.")
        cur.execute("UPDATE facturas SET iva_21 = ?, iva_105 = ?, percepciones = ?, notas_auditoria = ? WHERE id = ?",
                    (iva21, iva105, percep, ((notas or "") + " | " + marca) if notas else marca, fid))
        corregidas.append((etiqueta, iva21_v5, iva21, percep_v5, percep))
        cur.execute("RELEASE fac")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO fac"); cur.execute("RELEASE fac")
        errores.append((etiqueta, f"{type(e).__name__}: {e}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_070] OK -- corregidas {len(corregidas)}, saltadas {len(saltadas)}, con error {len(errores)}; {MIGRATION_ID} registrada.")
for n, antes, despues, p_antes, p_despues in corregidas:
    print(f"[migrate_070]   {n}: IVA 21 % {antes:,.2f} -> {despues:,.2f}; percepciones {p_antes:,.2f} -> {p_despues:,.2f}")
for n, m in saltadas:
    print(f"[migrate_070] AVISO -- {n}: {m}")
for n, m in errores:
    print(f"[migrate_070] ERROR -- {n}: {m} (ese comprobante quedo como estaba)")
conn.close()
