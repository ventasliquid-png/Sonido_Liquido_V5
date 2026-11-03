"""
migrate_075_renglones_facturas_bonificadas.py
=============================================
Card #144 (S898, 03/11/2026): el lector de PDF de ARCA ignoraba el «% Bonif» de cada renglon y guardaba cantidad x precio de lista, sin la bonificacion.
Desde la S894 (5b701e93, en produccion) el lector lee el «% Bonif» y el «Subtotal» que imprime ARCA; esta migracion corrige los renglones que ya habian
quedado guardados sin bonificar. Neto, IVA y total de esas facturas estaban bien (los manda ARCA y la Card #164 / migrate_070 arreglo el IVA): lo unico mal era
precio_unitario_neto y subtotal_neto del renglon, que no sumaban el neto de la factura.

CASOS (todos de Centro Pet y de Wullich, bonificacion del 5 % por renglon; valores leidos de los PDF de ARCA en el reservorio de facturas):
  2549 y 2589  Surgizime E2 botella x 1 Lt  240 un.: guardado 240 x 11.600 = 2.784.000   -> ARCA imprime 5 % y subtotal 2.644.800  (11.020 por unidad)
  2601         Surgizime E2 botella x 1 Lt  360 un.: guardado precio 0 y subtotal 0       -> ARCA subtotal 3.967.200                (11.020 por unidad)
  2616         Surgizime E2 botella x 1 Lt  360 un.: guardado 360 x 11.600 = 4.176.000   -> ARCA subtotal 3.967.200                (11.020 por unidad)
  2617         Surgizime E2 bidon x 5 Lts     5 un.: guardado   5 x 46.400 =   232.000   -> ARCA subtotal   220.400                (44.080 por unidad)
  2620         Surgizime E2 botella x 1 Lt  144 un.: guardado 144 x 11.600 = 1.670.400   -> ARCA subtotal 1.586.880                (11.020 por unidad)
(2534, 2574 y 2582 ya estaban bien: renglon a 11.020.) Convencion de V5: precio_unitario_neto es el precio por unidad con la bonificacion aplicada.

QUE HACE: para cada una de esas facturas con CAE, SOLO si sigue como se audito (un unico renglon con la cantidad, el precio y el subtotal esperados, y neto gravado igual
al subtotal de ARCA), pone en el renglon el subtotal de ARCA y el precio por unidad con la bonificacion aplicada. Nota [SISTEMA] en notas_auditoria.
QUE NO HACE: no toca neto, IVA, percepciones, total, estado, pedidos ni remitos. Lo que no esta como se audito se informa y se deja como estaba (y la migracion igual se registra).

SEGURIDAD: SAVEPOINT por factura, despues del backup de auto_migrar; idempotente (registro en _migraciones_aplicadas y el criterio de estado); sale 0.

MIGRATION_ID = "075_renglones_facturas_bonificadas"
NRO_SESION = 898
"""
import os
import sqlite3

MIGRATION_ID = "075_renglones_facturas_bonificadas"
NRO_SESION = 898
EPS = 0.011

# numero de factura A (punto de venta 1) -> (cantidad, precio guardado, subtotal guardado, subtotal que imprime ARCA)
ESPERADAS = {
    2549: (240.0, 11600.0, 2784000.0, 2644800.0),
    2589: (240.0, 11600.0, 2784000.0, 2644800.0),
    2601: (360.0, 0.0, 0.0, 3967200.0),
    2616: (360.0, 11600.0, 4176000.0, 3967200.0),
    2617: (5.0, 46400.0, 232000.0, 220400.0),
    2620: (144.0, 11600.0, 1670400.0, 1586880.0),
}

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_075] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("facturas", "facturas_items"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_075] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)

print(f"[migrate_075] Iniciando {MIGRATION_ID}: {len(ESPERADAS)} factura(s) a revisar...")
corregidas, ya_estaban, saltadas, errores = [], [], [], []
for numero, (cant, precio_v, subtotal_v, subtotal_arca) in sorted(ESPERADAS.items()):
    etiqueta = f"00001-{numero:08d}"
    try:
        cur.execute("SAVEPOINT fac")
        fac = cur.execute("""SELECT id, neto_gravado, cae, notas_auditoria FROM facturas
                             WHERE tipo_comprobante = 'FACTURA_A' AND punto_venta = 1 AND numero_comprobante = ?""", (numero,)).fetchone()
        if not fac:
            saltadas.append((etiqueta, "la factura no esta en esta base")); cur.execute("RELEASE fac"); continue
        fid, neto, cae, notas = fac
        if not cae or not str(cae).strip():
            saltadas.append((etiqueta, "sin CAE")); cur.execute("RELEASE fac"); continue
        if neto is None or abs(neto - subtotal_arca) > EPS:
            saltadas.append((etiqueta, f"el neto gravado guardado ({neto}) no es el subtotal de ARCA ({subtotal_arca}): no se toca")); cur.execute("RELEASE fac"); continue
        renglones = cur.execute("SELECT id, cantidad, precio_unitario_neto, subtotal_neto FROM facturas_items WHERE factura_id = ?", (fid,)).fetchall()
        if len(renglones) != 1:
            saltadas.append((etiqueta, f"tiene {len(renglones)} renglones y se esperaba 1: no se toca")); cur.execute("RELEASE fac"); continue
        rid, c, p, s = renglones[0]
        precio_nuevo = round(subtotal_arca / cant, 2)
        if abs((c or 0) - cant) < EPS and abs((p or 0) - precio_nuevo) < EPS and abs((s or 0) - subtotal_arca) < EPS:
            ya_estaban.append(etiqueta); cur.execute("RELEASE fac"); continue
        if not (abs((c or 0) - cant) < EPS and abs((p or 0) - precio_v) < EPS and abs((s or 0) - subtotal_v) < EPS):
            saltadas.append((etiqueta, f"el renglon ({c} x {p} = {s}) no es el que se audito ({cant} x {precio_v} = {subtotal_v}): no se toca")); cur.execute("RELEASE fac"); continue
        if abs(round(precio_nuevo * cant, 2) - subtotal_arca) > EPS:
            saltadas.append((etiqueta, f"{subtotal_arca} / {cant} no da un precio exacto ({precio_nuevo}): no se toca")); cur.execute("RELEASE fac"); continue
        marca = (f"[SISTEMA] Renglon corregido al precio con la bonificacion de ARCA (S898, migrate_075, Card #144): {c:g} x {p:,.2f} = {s:,.2f} -> "
                 f"{c:g} x {precio_nuevo:,.2f} = {subtotal_arca:,.2f}. Neto, IVA y total no cambian.")
        cur.execute("UPDATE facturas_items SET precio_unitario_neto = ?, subtotal_neto = ? WHERE id = ?", (precio_nuevo, subtotal_arca, rid))
        cur.execute("UPDATE facturas SET notas_auditoria = ? WHERE id = ?", (((notas or "") + " | " + marca) if notas else marca, fid))
        corregidas.append((etiqueta, c, p, s, precio_nuevo, subtotal_arca))
        cur.execute("RELEASE fac")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO fac"); cur.execute("RELEASE fac")
        errores.append((etiqueta, f"{type(e).__name__}: {e}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_075] OK -- corregidas {len(corregidas)}, ya estaban bien {len(ya_estaban)}, saltadas {len(saltadas)}, con error {len(errores)}; {MIGRATION_ID} registrada.")
for n, c, p, s, pn, sn in corregidas:
    print(f"[migrate_075]   {n}: {c:g} x {p:,.2f} = {s:,.2f} -> {c:g} x {pn:,.2f} = {sn:,.2f}")
for n in ya_estaban:
    print(f"[migrate_075]   {n}: ya estaba como ARCA")
for n, m in saltadas:
    print(f"[migrate_075] AVISO -- {n}: {m}")
for n, m in errores:
    print(f"[migrate_075] ERROR -- {n}: {m} (esa factura quedo como estaba)")
conn.close()
