"""
migrate_074_ri_renumerar_talonario.py
=====================================
S895 (29/10/2026). La etapa 1 del remito interno (RI) salió el 29/10 15:47 con el formato «RI-000001». Carlos fijó el mismo día el talonario «RI01» + 8 dígitos
(«RI01-00000001», igual de largo que «0015-00003034»; hasta 99 talonarios RI01..RI99), que es el que el código numera desde ahora. Antes de que el formato nuevo
llegara a P, Tomy probó el Cumplido de dos pedidos y quedaron dos RI con el formato viejo (RI-000001 y RI-000002, ENTREGADOS, sin papel impreso ni factura).

QUE HACE: pasa cada número «RI-nnnnnn» al talonario nuevo conservando su orden (RI-000001 -> RI01-00000001) y deja una nota [SISTEMA] en el remito con el número
anterior. Solo si sigue siendo lo que se auditó: el remito no se imprimió (bit IMPRESO apagado), no está vinculado a ninguna factura y el número nuevo no existe. Un remito
con número es inmortal (S891): esta es una excepción de Carlos y Nike por un cambio de formato ANTES de que haya papel; lo que no cumple se informa y queda como estaba (el
código sigue entendiendo el «RI-» viejo). No toca pedidos, ni las notas históricas que mencionan el número viejo (la nota nueva dice la equivalencia).
SEGURIDAD: SAVEPOINT por remito, después del backup de auto_migrar; idempotente; sale 0.

MIGRATION_ID = "074_ri_renumerar_talonario"
NRO_SESION = 895
"""
import os
import re
import sqlite3

MIGRATION_ID = "074_ri_renumerar_talonario"
NRO_SESION = 895
TALONARIO = "RI01"
IMPRESO = 1 << 44

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_074] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("remitos", "remitos_notas", "facturas_remitos"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_074] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)

viejos = [(i, n, f) for i, n, f in cur.execute("SELECT id, numero_legal, flags_estado FROM remitos WHERE numero_legal LIKE 'RI-%' ORDER BY numero_legal").fetchall()
          if re.fullmatch(r"RI-\d+", n or "")]
print(f"[migrate_074] Iniciando {MIGRATION_ID}: {len(viejos)} remito(s) interno(s) con el formato viejo...")
hechos, saltados, errores = [], [], []
for rid, numero, flags in viejos:
    try:
        cur.execute("SAVEPOINT ri")
        nuevo = f"{TALONARIO}-{int(numero.split('-')[1]):08d}"
        if int(flags or 0) & IMPRESO:
            saltados.append((numero, "ya se imprimió: queda con su número")); cur.execute("RELEASE ri"); continue
        if cur.execute("SELECT 1 FROM facturas_remitos WHERE remito_id = ?", (rid,)).fetchone():
            saltados.append((numero, "está vinculado a una factura: queda con su número")); cur.execute("RELEASE ri"); continue
        if cur.execute("SELECT 1 FROM remitos WHERE numero_legal = ?", (nuevo,)).fetchone():
            saltados.append((numero, f"el número {nuevo} ya existe: queda con su número")); cur.execute("RELEASE ri"); continue
        cur.execute("UPDATE remitos SET numero_legal = ? WHERE id = ?", (nuevo, rid))
        cur.execute("INSERT INTO remitos_notas (remito_id, texto, fecha) VALUES (?, ?, datetime('now', 'localtime'))",
                    (rid, f"[SISTEMA] Renumerado de {numero} a {nuevo}: cambio de formato al talonario {TALONARIO} (Carlos y Nike, S895), antes de que existiera papel. "
                          f"Las notas anteriores que nombran {numero} se refieren a este remito."))
        hechos.append((numero, nuevo))
        cur.execute("RELEASE ri")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO ri"); cur.execute("RELEASE ri")
        errores.append((numero, f"{type(e).__name__}: {e}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_074] OK -- renumerados {len(hechos)}, saltados {len(saltados)}, con error {len(errores)}; {MIGRATION_ID} registrada.")
for a, b in hechos:
    print(f"[migrate_074]   {a} -> {b}")
for n, m in saltados:
    print(f"[migrate_074] AVISO -- {n}: {m}")
for n, m in errores:
    print(f"[migrate_074] ERROR -- {n}: {m} (quedo como estaba)")
conn.close()
