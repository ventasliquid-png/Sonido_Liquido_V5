"""
migrate_066_remitos_genoma_fecha_emision.py
===========================================
S891 (22/10/2026), paquete 2 de remitos, tramo 1. Nike ratificó con Sello de Oro (tres dictámenes del 22/10,
CONSULTA_NIKE_genoma_remito_2026-10-22.md) el genoma del remito: CLASE 30 EGRESO / 31 EGRESO_AVIOS / 32 INTERNO (29 reservado para
ajustes de stock), ESTADO 33 EMITIDO / 35 ANULADO / 36 PERDIDO, LOGÍSTICA 37 EN_DEPOSITO / 38 RETIRADO / 39 RECIBIDO, calificadores
42 DIFERENCIA_RECEPCION / 43 FUE_ANULADO / 44 IMPRESO / 45 SALIDA_DIFERIDA. Carlos separó la fecha de EMISIÓN (la del papel, el día en
que toma número) de la salida física.

QUE HACE:
  1. remitos.fecha_emision DATETIME NULL (columna nueva).
  2. A cada remito con número le pone fecha_emision = fecha_creacion (el número se asignaba al abrir el PDF, casi siempre el mismo día;
     es la mejor aproximación) y, si no está anulado y no tiene fecha de salida, fecha_salida = fecha_emision (Carlos: «si queda en
     blanco se asume», hasta que exista Stock).
  3. Calcula el genoma de TODOS los remitos con la misma función que usa el servidor (backend/remitos/genoma.py): la clase sale del
     número y del pedido, el estado y la logística del estado de hoy, IMPRESO si existe su PDF en DOCUMENTOS_GENERADOS_RAR/Remitos de
     salida, DIFERENCIA_RECEPCION si algún renglón tiene recibido distinto de remitido, SALIDA_DIFERIDA si salió otro día que el de
     emisión. Los demás bits (0, 1, 4, 10, 11, 13, 41) quedan como estaban.
QUE NO HACE: no cambia ningún estado, número, renglón ni pedido; no toca fecha_creacion; no pisa una fecha de salida que ya existe.
GUARDAS: si falta la tabla remitos no se hace nada y NO se registra. Todo en una transacción.
FALLA RUIDOSO: si algo falla, deshace todo y sale con 1 para que auto_migrar frene el arranque: el modelo ya declara fecha_emision y
arrancar sin ella dejaría en error todas las consultas de remitos.

MIGRATION_ID = "066_remitos_genoma_fecha_emision"
NRO_SESION = 891
"""
import os
import sqlite3
import sys

MIGRATION_ID = "066_remitos_genoma_fecha_emision"
NRO_SESION = 891

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, RAIZ)
from backend.remitos.genoma import calcular_flags, diferencia_recepcion, describir  # noqa: E402  (sin base de datos: funciones puras)

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(RAIZ, "pilot_v5x.db")
CARPETA_PDF = os.path.join(RAIZ, "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida")

conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_066] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='remitos'").fetchone():
    print("[migrate_066] AVISO -- falta la tabla 'remitos': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
    conn.close()
    raise SystemExit(0)

print(f"[migrate_066] Iniciando {MIGRATION_ID}...")
try:
    cur.execute("BEGIN")
    if "fecha_emision" not in {r[1] for r in cur.execute("PRAGMA table_info(remitos)")}:
        cur.execute("ALTER TABLE remitos ADD COLUMN fecha_emision DATETIME")
    items = {}
    for rid, rem, rec in cur.execute("SELECT remito_id, cantidad_remitida, cantidad_recibida FROM remitos_items"):
        items.setdefault(rid, []).append((rem, rec))
    filas = cur.execute("""SELECT r.id, r.numero_legal, r.estado, r.fecha_creacion, r.fecha_salida, r.fecha_emision, r.flags_estado, p.flags_estado
                           FROM remitos r LEFT JOIN pedidos p ON p.id = r.pedido_id""").fetchall()
    conteo = {}
    fechas_emision = fechas_salida = 0
    for rid, numero, estado, f_creacion, f_salida, f_emision, flags, pflags in filas:
        if numero and not f_emision and f_creacion:
            f_emision = f_creacion
            fechas_emision += 1
        if numero and (estado or "").upper() != "ANULADO" and not f_salida and f_emision:
            f_salida = f_emision
            fechas_salida += 1
        impreso = bool(numero) and os.path.exists(os.path.join(CARPETA_PDF, f"remito_{numero.replace('-', '_')}.pdf"))
        nuevos = calcular_flags(flags, numero, estado, pflags, f_emision, f_salida, diferencia_recepcion(items.get(rid, [])), impreso)
        cur.execute("UPDATE remitos SET fecha_emision = ?, fecha_salida = ?, flags_estado = ? WHERE id = ?", (f_emision, f_salida, nuevos, rid))
        d = describir(nuevos)
        clave = f"{d['clase']}/{d['estado'] or 'SIN_NUMERO'}/{d['logistica'] or '-'}"
        conteo[clave] = conteo.get(clave, 0) + 1
        for m in d["marcas"]:
            conteo[m] = conteo.get(m, 0) + 1
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    cur.execute("COMMIT")
    print(f"[migrate_066] OK -- {len(filas)} remitos con genoma; fecha_emision completada en {fechas_emision}, salida asumida en {fechas_salida}.")
    for k in sorted(conteo):
        print(f"[migrate_066]    {k}: {conteo[k]}")
    print(f"[migrate_066] {MIGRATION_ID} registrada.")
except Exception as e:  # noqa: BLE001
    try:
        cur.execute("ROLLBACK")
    except Exception:  # noqa: BLE001
        pass
    print(f"[migrate_066] ERROR -- {type(e).__name__}: {e}. Se deshizo todo y no se registra; auto_migrar frena el arranque.")
    conn.close()
    raise SystemExit(1)
conn.close()
