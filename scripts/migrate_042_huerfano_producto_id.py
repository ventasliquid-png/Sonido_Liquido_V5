"""
migrate_042_huerfano_producto_id.py
====================================
Etapa 4-bis del PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md -- cierre del hueco huerfano
reportado durante la verificacion de Etapa 4 (armar_remito no podia cubrir Circuito 17 porque
remitos_items.pedido_item_id era NOT NULL y no existia forma de decir "que producto y cuanto"
sin un pedido detras).

Decision de Carlos (24/09, addendum a 2026-09-24_NS_etapa4.txt): aditivo, mismo patron que
Etapa 1 -- relajar un NOT NULL, sumar una columna nullable. FK a producto real (productos.id),
no texto libre, para no reabrir el agujero "Ghost Style" que la guarda de Card #125 ya cerro en
update_remito (addendum Etapa 0): un huerfano sigue siendo mercaderia real (HuerfanoDestino
rastrea cantidades que reingresan o se comercializan), tiene que apuntar a un producto del
catalogo. Regla de aplicacion (no CHECK de base): un RemitoItem tiene pedido_item_id XOR
producto_id -- validada en RemitosService.armar_remito, no aca.

remitos_items.pedido_item_id nullable requiere reconstruir la tabla (SQLite no soporta ALTER
COLUMN DROP NOT NULL) -- mismo patron que migrate_041_circuito_pr_schema.py paso 4: rename a
_old con legacy_alter_table=ON (para que remitos_notas.remito_item_id y
huerfano_destinos.huerfano_item_id, que apuntan a esta tabla, no queden apuntando a
"remitos_items_old" para siempre), crear tabla nueva, copiar filas, borrar _old.

MIGRATION_ID = "042_huerfano_producto_id"
NRO_SESION = 873  # continuacion directa de Etapa 4 (S871-872), sin ceremonia ALFA/OMEGA completa
"""
import sqlite3
import os

MIGRATION_ID = "042_huerfano_producto_id"
NRO_SESION = 873

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db"
)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

ya_aplicada = cur.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()

if ya_aplicada:
    print(f"[migrate_042] SKIP — {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_042] Iniciando {MIGRATION_ID}...")
    antes_items = cur.execute("SELECT COUNT(*) FROM remitos_items").fetchone()[0]
    antes_notas = cur.execute("SELECT COUNT(*) FROM remitos_notas").fetchone()[0]
    antes_huerfano_destinos = cur.execute("SELECT COUNT(*) FROM huerfano_destinos").fetchone()[0]

    # --- remitos_items: pedido_item_id nullable + producto_id (reconstruccion de tabla) ---
    # Schema calcado 1:1 del sqlite_master real de hoy (verificado antes de escribir esto), con
    # el unico cambio de NOT NULL -> nullable en pedido_item_id y la columna nueva al final.
    print("[1] remitos_items: relajando pedido_item_id a nullable + agregando producto_id...")
    cur.execute("PRAGMA foreign_keys=OFF")
    cur.execute("PRAGMA legacy_alter_table=ON")

    cur.execute("DROP INDEX IF EXISTS ix_remitos_items_id")
    cur.execute("ALTER TABLE remitos_items RENAME TO remitos_items_old")

    cur.execute("""
        CREATE TABLE remitos_items (
            id INTEGER NOT NULL,
            remito_id CHAR(32) NOT NULL,
            pedido_item_id INTEGER,
            cantidad_remitida FLOAT, cantidad_declarada FLOAT NOT NULL DEFAULT 0.0, cantidad_recibida FLOAT, cantidad_facturada FLOAT,
            producto_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY(remito_id) REFERENCES remitos (id),
            FOREIGN KEY(pedido_item_id) REFERENCES pedidos_items (id),
            FOREIGN KEY(producto_id) REFERENCES productos (id)
        )
    """)

    cols = "id, remito_id, pedido_item_id, cantidad_remitida, cantidad_declarada, cantidad_recibida, cantidad_facturada"
    cur.execute(f"INSERT INTO remitos_items ({cols}) SELECT {cols} FROM remitos_items_old")
    filas_copiadas = cur.rowcount
    cur.execute("DROP TABLE remitos_items_old")

    cur.execute("CREATE INDEX ix_remitos_items_id ON remitos_items (id)")
    cur.execute("PRAGMA legacy_alter_table=OFF")
    cur.execute("PRAGMA foreign_keys=ON")

    # --- Verificacion antes de registrar la migracion como aplicada ---
    despues_items = cur.execute("SELECT COUNT(*) FROM remitos_items").fetchone()[0]
    despues_notas = cur.execute("SELECT COUNT(*) FROM remitos_notas").fetchone()[0]
    despues_huerfano_destinos = cur.execute("SELECT COUNT(*) FROM huerfano_destinos").fetchone()[0]
    print(f"   Verificacion: remitos_items {antes_items} -> {despues_items} (copiadas: {filas_copiadas}), "
          f"remitos_notas {antes_notas} -> {despues_notas}, huerfano_destinos {antes_huerfano_destinos} -> {despues_huerfano_destinos}")
    if despues_items != antes_items or despues_notas != antes_notas or despues_huerfano_destinos != antes_huerfano_destinos:
        raise RuntimeError(
            f"Conteo de filas no coincide tras la migracion -- remitos_items {antes_items}->{despues_items}, "
            f"remitos_notas {antes_notas}->{despues_notas}, huerfano_destinos {antes_huerfano_destinos}->{despues_huerfano_destinos}. "
            f"Abortando sin registrar."
        )

    # Chequeo de que los FKs hijos (remitos_notas, huerfano_destinos) siguen apuntando a
    # "remitos_items" y no a "remitos_items_old" (la trampa de legacy_alter_table).
    for tabla in ("remitos_notas", "huerfano_destinos"):
        sql_tabla = cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tabla,)
        ).fetchone()[0]
        if "remitos_items_old" in sql_tabla:
            raise RuntimeError(
                f"{tabla} quedo con un FK apuntando a remitos_items_old -- legacy_alter_table no "
                f"tuvo el efecto esperado. Abortando sin registrar."
            )

    cur.execute(
        "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION),
    )
    conn.commit()
    print(f"[migrate_042] OK — {MIGRATION_ID} aplicada. {despues_items} remitos_items intactos.")

except sqlite3.OperationalError as e:
    conn.rollback()
    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
        print(f"[migrate_042] SKIP parcial -- {e}. Revisar a mano si la migracion quedo a mitad de camino "
              f"(la tabla remitos_items_old, si existe, es la senal). No se registro como aplicada.")
    else:
        print(f"[migrate_042] ERROR: {e}")
        raise
except Exception as e:
    conn.rollback()
    print(f"[migrate_042] ERROR: {e}")
    raise
finally:
    conn.close()
