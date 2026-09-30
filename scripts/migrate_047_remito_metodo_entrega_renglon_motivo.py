"""
migrate_047_remito_metodo_entrega_renglon_motivo.py
====================================
Confeccion de remitos y seguimiento a nivel renglon -- especificacion cerrada de Carlos + Arq + Nike
(Sello de Oro, tres rondas), 30/09/2026 (PROMPTS_TRABAJO/2026-09-30_NS_implementar_remito_renglon_S875.txt):

  1. remitos.transporte_id pasa a NULLABLE. Un retiro en MOSTRADOR (o con transporte propio) no tiene
     empresa de transporte de terceros. remitos.domicilio_entrega_id NO se toca: el mostrador usa un
     domicilio real (la oficina), no hace falta volverlo nullable.
  2. remitos.metodo_entrega (VARCHAR, nullable) -- como salio fisicamente ESTA entrega: MOSTRADOR,
     FLETE_TERCERO, TRANSPORTE_PROPIO, MOTO_CADETERIA, REMITO_EXTERNO. Se fija una sola vez al crear el
     remito. Los remitos que ya existen quedan en NULL: no se inventa un metodo retroactivo.
  3. remitos_items.motivo_no_facturable (VARCHAR, nullable) -- NULL = facturable normal; CONSIGNACION,
     MUESTRA_SIN_CARGO, GARANTIA_REEMPLAZO = el renglon salio sin ser venta firme. Vive en el renglon,
     no en el remito. Las filas existentes quedan en NULL.

(1) requiere reconstruir la tabla `remitos` (SQLite no soporta ALTER COLUMN DROP NOT NULL) -- mismo
patron que migrate_043 (rename con legacy_alter_table=ON para que los FK de remitos_items,
remitos_notas y facturas_remitos no queden apuntando a "remitos_old"), con dos diferencias:
  - Lee la estructura REAL de la tabla (columnas, defaults, FKs, indices) en vez de fijar un CREATE
    TABLE a mano: D (migrada hasta 041) y P (migrada hasta 045) tienen la tabla en estados distintos --
    remitos.pedido_id es nullable en una y NOT NULL en la otra -- y esta migracion no debe decidir
    por ellos. Conserva todo tal cual, salvo transporte_id.
  - Es ATOMICA: todo el rebuild corre dentro de una sola transaccion, asi que si algo falla la base
    queda como estaba (sin un remitos_old colgado a mitad de camino).

La oficina (DOMICILIO_ROSETI_ID, Roseti 1482) NO se toca desde aca: el domicilio se crea solo, la
primera vez que se arma un remito de mostrador (ClienteService.ensure_domicilio_oficina).

Requiere 041 y 043 aplicadas (la 043 reconstruye remitos con un DDL fijo y tiene que correr antes). Idempotente.

MIGRATION_ID = "047_remito_metodo_entrega_renglon_motivo"
NRO_SESION = 876
"""
import sqlite3
import os

MIGRATION_ID = "047_remito_metodo_entrega_renglon_motivo"
NRO_SESION = 876

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db"
)

# isolation_level=None: las transacciones se manejan a mano (BEGIN/COMMIT) para que el rebuild de
# la tabla, que mezcla DDL y DML, sea todo-o-nada.
conn = sqlite3.connect(DB_PATH, isolation_level=None)
cur = conn.cursor()


def _q(nombre: str) -> str:
    return '"' + nombre.replace('"', '""') + '"'


def _columnas(tabla: str):
    # (cid, name, type, notnull, dflt_value, pk)
    return cur.execute(f"PRAGMA table_info({_q(tabla)})").fetchall()


cur.execute("""
    CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (
        id VARCHAR PRIMARY KEY,
        nro_sesion INTEGER,
        aplicada_en DATETIME DEFAULT (datetime('now'))
    )
""")

if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_047] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_047] Iniciando {MIGRATION_ID}...")

    for tabla in ("remitos", "remitos_items", "remitos_notas", "facturas_remitos"):
        if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (tabla,)).fetchone():
            raise RuntimeError(f"No existe la tabla '{tabla}': no es una base de V5 o esta desactualizada.")
    if "cantidad_remitida" not in {c[1] for c in _columnas("remitos_items")}:
        raise RuntimeError("remitos_items no tiene cantidad_remitida: falta aplicar migrate_041 antes que esta.")
    # 043 reconstruye `remitos` con un CREATE TABLE fijo (transporte_id NOT NULL, sin metodo_entrega): si
    # corriera DESPUES de esta, pisaria lo que hace esta migracion. auto_migrar las aplica por orden de
    # numero, asi que solo se cruzan si alguien corre la 047 a mano sobre una base sin la 043.
    if not cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", ("043_revertir_huerfano_pedido_id",)).fetchone():
        raise RuntimeError("Falta aplicar migrate_043 antes que esta (reconstruye remitos con un DDL fijo que pisaria esta migracion).")
    if cur.execute("SELECT 1 FROM sqlite_master WHERE name='remitos_old'").fetchone():
        raise RuntimeError("Existe una tabla 'remitos_old' de un intento anterior: revisar a mano antes de reintentar.")

    antes = {t: cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
             for t in ("remitos", "remitos_items", "remitos_notas", "facturas_remitos")}
    cols_remitos = _columnas("remitos")
    nombres_remitos = [c[1] for c in cols_remitos]
    transporte_nullable_ya = any(c[1] == "transporte_id" and not c[3] for c in cols_remitos)
    metodo_ya = "metodo_entrega" in nombres_remitos
    filas_antes = cur.execute(f"SELECT {', '.join(_q(n) for n in nombres_remitos)} FROM remitos ORDER BY id").fetchall()

    # FOREIGN_KEYS y legacy_alter_table se fijan FUERA de la transaccion (no se pueden cambiar adentro).
    cur.execute("PRAGMA foreign_keys=OFF")
    cur.execute("PRAGMA legacy_alter_table=ON")
    cur.execute("BEGIN IMMEDIATE")

    # --- 1 y 2. remitos: transporte_id nullable + metodo_entrega (reconstruccion de tabla) ---
    if transporte_nullable_ya and metodo_ya:
        print("[1-2] remitos: ya tiene transporte_id nullable y metodo_entrega, sin cambios.")
    else:
        print("[1-2] remitos: transporte_id nullable + columna metodo_entrega (reconstruccion de tabla)...")
        fks = cur.execute(f"PRAGMA foreign_key_list(remitos)").fetchall()  # (id, seq, table, from, to, ...)
        indices = cur.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='remitos' AND sql IS NOT NULL"
        ).fetchall()

        defs = []
        for _cid, nombre, tipo, notnull, dflt, pk in cols_remitos:
            d = f"{_q(nombre)} {tipo or ''}".rstrip()
            if notnull and nombre != "transporte_id":
                d += " NOT NULL"
            if dflt is not None:
                d += f" DEFAULT {dflt}"
            defs.append(d)
        if not metodo_ya:
            defs.append(f"{_q('metodo_entrega')} VARCHAR")
        pks = [c[1] for c in sorted(cols_remitos, key=lambda c: c[5]) if c[5]]
        defs.append(f"PRIMARY KEY ({', '.join(_q(p) for p in pks)})")
        # foreign_key_list numera al reves del orden de declaracion (id 0 = la ultima): se ordena de
        # mayor a menor para declararlas en el mismo orden que tenia la tabla.
        for _i, _s, tabla_ref, desde, hasta, *_resto in sorted(fks, key=lambda f: (-f[0], f[1])):
            defs.append(f"FOREIGN KEY({_q(desde)}) REFERENCES {_q(tabla_ref)} ({_q(hasta)})")

        for nombre_idx, _sql in indices:
            cur.execute(f"DROP INDEX IF EXISTS {_q(nombre_idx)}")
        cur.execute("ALTER TABLE remitos RENAME TO remitos_old")
        cur.execute(f"CREATE TABLE remitos (\n    " + ",\n    ".join(defs) + "\n)")
        lista = ", ".join(_q(n) for n in nombres_remitos)
        cur.execute(f"INSERT INTO remitos ({lista}) SELECT {lista} FROM remitos_old")
        copiadas = cur.rowcount
        cur.execute("DROP TABLE remitos_old")
        for _nombre_idx, sql_idx in indices:
            cur.execute(sql_idx)
        print(f"      filas copiadas: {copiadas}; indices recreados: {[i[0] for i in indices]}")

    # --- 3. remitos_items.motivo_no_facturable ---
    if "motivo_no_facturable" in {c[1] for c in _columnas("remitos_items")}:
        print("[3] remitos_items: motivo_no_facturable ya existe, sin cambios.")
    else:
        print("[3] remitos_items: agregando motivo_no_facturable...")
        cur.execute("ALTER TABLE remitos_items ADD COLUMN motivo_no_facturable VARCHAR")

    # --- Verificacion antes de confirmar ---
    despues = {t: cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
               for t in ("remitos", "remitos_items", "remitos_notas", "facturas_remitos")}
    print(f"      conteos antes -> despues: { {t: (antes[t], despues[t]) for t in antes} }")
    if antes != despues:
        raise RuntimeError(f"El conteo de filas no coincide tras la migracion ({antes} -> {despues}).")
    filas_despues = cur.execute(f"SELECT {', '.join(_q(n) for n in nombres_remitos)} FROM remitos ORDER BY id").fetchall()
    if filas_antes != filas_despues:
        raise RuntimeError("Los datos de remitos no quedaron identicos tras la reconstruccion de la tabla.")
    for tabla in ("remitos_items", "remitos_notas", "facturas_remitos"):
        sql_tabla = cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tabla,)).fetchone()[0]
        if "remitos_old" in sql_tabla:
            raise RuntimeError(f"{tabla} quedo con un FK apuntando a remitos_old (legacy_alter_table no tuvo el efecto esperado).")
    col_t = next(c for c in _columnas("remitos") if c[1] == "transporte_id")
    if col_t[3]:
        raise RuntimeError("remitos.transporte_id sigue NOT NULL despues de la reconstruccion.")

    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    cur.execute("COMMIT")
    cur.execute("PRAGMA legacy_alter_table=OFF")
    cur.execute("PRAGMA foreign_keys=ON")
    print(f"[migrate_047] OK -- {despues['remitos']} remitos y {despues['remitos_items']} renglones intactos; {MIGRATION_ID} registrada.")

except Exception as e:
    try:
        cur.execute("ROLLBACK")
    except sqlite3.OperationalError:
        pass
    print(f"[migrate_047] ERROR -- se deshizo todo, la base quedo como estaba: {e}")
    conn.close()
    exit(1)

conn.close()
