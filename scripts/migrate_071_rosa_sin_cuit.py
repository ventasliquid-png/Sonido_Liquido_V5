"""
migrate_071_rosa_sin_cuit.py
============================
S894 (28/10/2026). Carlos: un Consumidor Final es Blanco, nunca Rosa; y el CUIT 11111111111 como marca de Rosa fue un error de la S875
(verificador inválido, se confunde con 11111111119). Nike (Sello de Oro, CONSULTA_NIKE_cf_rosa_cuit_2026-10-28.md): la identidad Rosa del
cliente vive solo en los bits (bit 4 sello Rosa, bit 19 medalla, nivel 9/11); el Rosa va con CUIT vacío; el CUIT comodín de CF no se guarda
en la ficha. En P había clientes informales cargados como «Consumidor Final + 11111111119» que compran solo en Rosa (sus «facturas» son
PRESUPUESTO_X en borrador, sin CAE). Carlos aprobó (28/10, «1 Ok») pasar estos nueve a Rosa, como ya están Pao Tandil y Ana Robles:
CUIT vacío (Adri Nails conserva su CUIT real), sin condición de IVA, nivel 9 (existencia + estructura, sin validación ARCA), sello Rosa
(bit 4) y medalla (bit 19) si tiene lista y segmento. M&M Odontológicos La Plata queda Blanco (Carlos). DAI y M&M Insumos no se tocan.

QUÉ HACE: por cada uno de los nueve (por nombre exacto), SOLO si sigue como se auditó (CUIT 11111111119, o el de Adri Nails, y condición
Consumidor Final): cambia CUIT, condición y bits, y suma una línea [SISTEMA] en observaciones. QUÉ NO HACE: no toca pedidos (el color de cada
pedido es suyo), facturas, domicilios ni otros clientes; lo que no coincide se informa y queda como estaba.
SEGURIDAD: SAVEPOINT por cliente, después del backup de auto_migrar; idempotente (registro y la condición de partida); sale 0.

MIGRATION_ID = "071_rosa_sin_cuit"
NRO_SESION = 894
"""
import os
import sqlite3

MIGRATION_ID = "071_rosa_sin_cuit"
NRO_SESION = 894
B4, B19 = 1 << 4, 1 << 19
NIVEL_ROSA = 9   # existencia (1) + estructura V14 (8): Rosa operativo, sin validación ARCA ni virginidad (tienen pedidos)
CUIT_REAL = {"Adri Nails Adriana Vaquero": "27182292368"}
CLIENTES = ("ASTRID MANICURA DEVOTO", "Adri Nails Adriana Vaquero", "DAI SALOMÉ", "DELICIA ALDERETES", "Federico Acuario",
            "LILIA MORALES", "LUCIANA FLORENTÍN", "MIRTA ROSSINI", "VLAJEC INSUMOS TATTOO")
NOTA = ("[SISTEMA] 28/10/2026 (S894, migrate_071): pasa a Rosa con CUIT vacío y sin condición de IVA (Carlos: un Consumidor Final es Blanco; "
        "Nike: la identidad Rosa vive en los bits). Antes: CUIT {cuit}, Consumidor Final, marcas {antes}.")

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db")
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (id VARCHAR PRIMARY KEY, nro_sesion INTEGER, aplicada_en DATETIME DEFAULT (datetime('now')))""")
if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_071] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    raise SystemExit(0)
for t in ("clientes", "condiciones_iva"):
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone():
        print(f"[migrate_071] AVISO -- falta la tabla '{t}': no se hace nada y la migracion NO se registra (se reintenta en el proximo arranque).")
        conn.close()
        raise SystemExit(0)

print(f"[migrate_071] Iniciando {MIGRATION_ID}: {len(CLIENTES)} cliente(s) informales cargados como Consumidor Final a revisar...")
hechos, saltados, errores = [], [], []
for nombre in CLIENTES:
    try:
        cur.execute("SAVEPOINT cli")
        filas = cur.execute("""SELECT c.id, c.cuit, c.flags_estado, c.observaciones, ci.nombre, c.lista_precios_id, c.segmento_id
                               FROM clientes c LEFT JOIN condiciones_iva ci ON ci.id = c.condicion_iva_id WHERE c.razon_social = ?""", (nombre,)).fetchall()
        if len(filas) != 1:
            saltados.append((nombre, f"hay {len(filas)} clientes con ese nombre")); cur.execute("RELEASE cli"); continue
        cid, cuit, flags, obs, iva, lista, segmento = filas[0]
        flags = int(flags or 0)
        cuit_esperado = CUIT_REAL.get(nombre, "11111111119")
        if cuit != cuit_esperado or "CONSUMIDOR FINAL" not in (iva or "").upper():
            saltados.append((nombre, f"ya no está como se auditó (CUIT {cuit}, condición {iva}): no se toca")); cur.execute("RELEASE cli"); continue
        nuevos = (flags & ~15 & ~B19) | NIVEL_ROSA | B4 | (B19 if (lista and segmento) else 0)
        nuevo_cuit = CUIT_REAL.get(nombre)   # None = CUIT vacío
        nota = NOTA.format(cuit=cuit, antes=flags)
        cur.execute("UPDATE clientes SET cuit = ?, condicion_iva_id = NULL, flags_estado = ?, observaciones = ? WHERE id = ?",
                    (nuevo_cuit, nuevos, ((obs + "\n") if obs else "") + nota, cid))
        hechos.append((nombre, cuit, nuevo_cuit, flags, nuevos))
        cur.execute("RELEASE cli")
    except Exception as e:  # noqa: BLE001
        cur.execute("ROLLBACK TO cli"); cur.execute("RELEASE cli")
        errores.append((nombre, f"{type(e).__name__}: {e}"))

cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
print(f"[migrate_071] OK -- a Rosa {len(hechos)}, saltados {len(saltados)}, con error {len(errores)}; {MIGRATION_ID} registrada.")
for n, c_ant, c_nuevo, f_ant, f_nuevo in hechos:
    print(f"[migrate_071]   {n}: CUIT {c_ant} -> {c_nuevo or 'vacío'}; marcas {f_ant} -> {f_nuevo}")
for n, m in saltados:
    print(f"[migrate_071] AVISO -- {n}: {m}")
for n, m in errores:
    print(f"[migrate_071] ERROR -- {n}: {m} (ese cliente quedó como estaba)")
conn.close()
