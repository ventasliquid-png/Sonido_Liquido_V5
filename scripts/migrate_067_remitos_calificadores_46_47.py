"""
migrate_067_remitos_calificadores_46_47.py
==========================================
S892 (23/10/2026), paquete 2 de remitos. Nike ratificó con Sello de Oro (cuarta consulta, CONSULTA_NIKE_genoma_remito_2026-10-22.md) dos
calificadores irreversibles de RemitoFlags: bit 46 CIRCULACION_ROSA (un 0015 de un pedido Rosa: no se factura) y bit 47 SALIDA_CONFIRMADA
(una persona, la guía del transporte o la copia firmada confirmó que salió; sin el bit, la salida es la asumida al emitir).

QUE HACE: recalcula el genoma de TODOS los remitos con la misma función que usa el servidor (backend/remitos/genoma.py), que ahora
incluye los dos bits: CIRCULACION_ROSA en los 0015 de pedidos Rosa, SALIDA_CONFIRMADA en los que están EN_CAMINO o ENTREGADO (alguien lo
despachó o lo recibió). Los demás bits quedan como estaban (los calificadores nunca se apagan).
QUE NO HACE: no cambia ningún estado, número, fecha, renglón ni pedido. Idempotente.
GUARDAS: si falta la tabla remitos o la columna flags_estado no se hace nada y NO se registra. Una transacción; si falla, deshace todo y
sale con 1.

MIGRATION_ID = "067_remitos_calificadores_46_47"
NRO_SESION = 892
"""
import os
import sqlite3
import sys

MIGRATION_ID = "067_remitos_calificadores_46_47"
NRO_SESION = 892

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, RAIZ)
from backend.remitos.genoma import calcular_flags, diferencia_recepcion, describir  # noqa: E402  (sin base de datos: funciones puras)

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(RAIZ, "pilot_v5x.db")

conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_067] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='remitos'").fetchone() \
        or "flags_estado" not in {r[1] for r in cur.execute("PRAGMA table_info(remitos)")}:
    print("[migrate_067] AVISO -- falta la tabla 'remitos' o su columna flags_estado: no se hace nada y la migracion NO se registra (se reintenta).")
    conn.close()
    raise SystemExit(0)

print(f"[migrate_067] Iniciando {MIGRATION_ID}...")
try:
    cur.execute("BEGIN")
    items = {}
    for rid, rem, rec in cur.execute("SELECT remito_id, cantidad_remitida, cantidad_recibida FROM remitos_items"):
        items.setdefault(rid, []).append((rem, rec))
    tiene_emision = "fecha_emision" in {r[1] for r in cur.execute("PRAGMA table_info(remitos)")}
    sql = ("SELECT r.id, r.numero_legal, r.estado, r.fecha_salida, r.flags_estado, p.flags_estado" + (", r.fecha_emision" if tiene_emision else ", NULL")
           + " FROM remitos r LEFT JOIN pedidos p ON p.id = r.pedido_id")
    filas = cur.execute(sql).fetchall()
    cambiados = 0
    conteo = {}
    for rid, numero, estado, f_salida, flags, pflags, f_emision in filas:
        nuevos = calcular_flags(flags, numero, estado, pflags, f_emision, f_salida, diferencia_recepcion(items.get(rid, [])), False)
        if nuevos != int(flags or 0):
            cur.execute("UPDATE remitos SET flags_estado = ? WHERE id = ?", (nuevos, rid))
            cambiados += 1
        for m in describir(nuevos)["marcas"]:
            if m in ("CIRCULACION_ROSA", "SALIDA_CONFIRMADA"):
                conteo[m] = conteo.get(m, 0) + 1
    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    cur.execute("COMMIT")
    print(f"[migrate_067] OK -- {len(filas)} remitos revisados, {cambiados} con bits nuevos.")
    for k in sorted(conteo):
        print(f"[migrate_067]    {k}: {conteo[k]}")
    print(f"[migrate_067] {MIGRATION_ID} registrada.")
except Exception as e:  # noqa: BLE001
    try:
        cur.execute("ROLLBACK")
    except Exception:  # noqa: BLE001
        pass
    print(f"[migrate_067] ERROR -- {type(e).__name__}: {e}. Se deshizo todo y no se registra.")
    conn.close()
    raise SystemExit(1)
conn.close()
