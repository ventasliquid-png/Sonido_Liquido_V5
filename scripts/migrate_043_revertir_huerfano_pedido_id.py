"""
migrate_043_revertir_huerfano_pedido_id.py
====================================
Reversion de la parte de Etapa 1 (migrate_041_circuito_pr_schema.py) que sostenia el diseno
"Remito sin Pedido" para huerfanos -- reemplazado por decision de Carlos + Nike (Sello de Oro,
tres vueltas, DISENO_PEDIDO_NO_COMERCIAL_S873_2026-09-24.md): un huerfano ahora es un Pedido
normal con PedidoFlags.ES_NO_COMERCIAL (Bit 11, ya existente), no un Remito sin pedido_id.

La migracion 042 (RemitoItem.pedido_item_id nullable + producto_id) nunca llego a aplicarse a
la base real -- esa parte se saco solo con revert de codigo (commit 93790033), sin migracion de
datos. Lo que SI llego a aplicarse contra pilot_v5x.db real fue la parte de 041 que toca
remitos.pedido_id (relajado a nullable) y la tabla huerfano_destinos (creada, siempre vacia,
nunca tuvo lectores ni escritores en codigo) -- esas dos si necesitan revertirse en datos.

Verificado antes de escribir esto (dictamen Nike de hoy autoriza el DROP directo de
huerfano_destinos por estar vacia y sin uso): SELECT COUNT(*) FROM remitos WHERE pedido_id IS
NULL = 0 y SELECT COUNT(*) FROM huerfano_destinos = 0 contra pilot_v5x.db real.

remitos.pedido_id NOT NULL requiere reconstruir la tabla (SQLite no soporta ALTER COLUMN SET
NOT NULL) -- mismo patron que migrate_041/042: rename a _old con legacy_alter_table=ON (para
que remitos_items.remito_id, remitos_notas.remito_id y facturas_remitos.remito_id, que apuntan
a esta tabla, no queden apuntando a "remitos_old" para siempre), crear tabla nueva, copiar
filas, borrar _old. La columna "motivo" queda en la tabla (vestigial, sin lectores en codigo
tras el revert) -- sacarla no fue pedido y no es necesario para el objetivo de esta migracion.

MIGRATION_ID = "043_revertir_huerfano_pedido_id"
NRO_SESION = 874  # continuacion directa de Etapa 4/4-bis (S871-873), sin ceremonia ALFA/OMEGA completa
"""
import sqlite3
import os

MIGRATION_ID = "043_revertir_huerfano_pedido_id"
NRO_SESION = 874

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db"
)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

ya_aplicada = cur.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()

if ya_aplicada:
    print(f"[migrate_043] SKIP — {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_043] Iniciando {MIGRATION_ID}...")

    # --- Guarda de seguridad: nadie uso el huerfano en produccion todavia ---
    huerfanos_existentes = cur.execute("SELECT COUNT(*) FROM remitos WHERE pedido_id IS NULL").fetchone()[0]
    if huerfanos_existentes > 0:
        raise RuntimeError(
            f"Hay {huerfanos_existentes} remito(s) con pedido_id NULL en la base -- no se puede "
            f"volver pedido_id a NOT NULL sin perder o reasignar esos datos. Abortando sin tocar "
            f"nada. Esto necesita una decision de Carlos antes de reintentar esta migracion."
        )
    filas_huerfano_destinos = cur.execute("SELECT COUNT(*) FROM huerfano_destinos").fetchone()[0]
    if filas_huerfano_destinos > 0:
        raise RuntimeError(
            f"huerfano_destinos tiene {filas_huerfano_destinos} fila(s) -- el dictamen de Nike "
            f"autorizo el DROP directo asumiendo la tabla vacia. Abortando sin tocar nada."
        )

    antes_remitos = cur.execute("SELECT COUNT(*) FROM remitos").fetchone()[0]
    antes_items = cur.execute("SELECT COUNT(*) FROM remitos_items").fetchone()[0]
    antes_notas = cur.execute("SELECT COUNT(*) FROM remitos_notas").fetchone()[0]
    antes_facturas_remitos = cur.execute("SELECT COUNT(*) FROM facturas_remitos").fetchone()[0]

    # --- 1. remitos: pedido_id vuelve a NOT NULL (reconstruccion de tabla) ---
    print("[1] remitos: pedido_id vuelve a NOT NULL (reconstruccion de tabla)...")
    cur.execute("PRAGMA foreign_keys=OFF")
    cur.execute("PRAGMA legacy_alter_table=ON")

    cur.execute("DROP INDEX IF EXISTS ix_remitos_pedido_id")
    cur.execute("DROP INDEX IF EXISTS ix_remitos_id")
    cur.execute("ALTER TABLE remitos RENAME TO remitos_old")

    cur.execute("""
        CREATE TABLE remitos (
            id CHAR(32) NOT NULL,
            pedido_id INTEGER NOT NULL,
            domicilio_entrega_id CHAR(32) NOT NULL,
            transporte_id CHAR(32) NOT NULL,
            fecha_salida DATETIME,
            fecha_creacion DATETIME,
            estado VARCHAR,
            numero_legal VARCHAR,
            aprobado_para_despacho BOOLEAN,
            cae VARCHAR,
            vto_cae DATE,
            bultos INTEGER DEFAULT 1,
            valor_declarado FLOAT DEFAULT 0.0,
            flags_estado INTEGER DEFAULT 0,
            motivo VARCHAR,
            PRIMARY KEY (id),
            FOREIGN KEY(pedido_id) REFERENCES pedidos (id),
            FOREIGN KEY(domicilio_entrega_id) REFERENCES "domicilios_legacy" (id),
            FOREIGN KEY(transporte_id) REFERENCES empresas_transporte (id)
        )
    """)

    cols = ("id, pedido_id, domicilio_entrega_id, transporte_id, fecha_salida, fecha_creacion, "
            "estado, numero_legal, aprobado_para_despacho, cae, vto_cae, bultos, valor_declarado, "
            "flags_estado, motivo")
    cur.execute(f"INSERT INTO remitos ({cols}) SELECT {cols} FROM remitos_old")
    filas_copiadas = cur.rowcount
    cur.execute("DROP TABLE remitos_old")

    cur.execute("CREATE INDEX ix_remitos_pedido_id ON remitos (pedido_id)")
    cur.execute("CREATE INDEX ix_remitos_id ON remitos (id)")
    cur.execute("PRAGMA legacy_alter_table=OFF")
    cur.execute("PRAGMA foreign_keys=ON")

    # --- 2. huerfano_destinos: DROP directo (vacia, sin uso, autorizado por Nike hoy) ---
    print("[2] Borrando tabla huerfano_destinos (vacia, sin lectores ni escritores en codigo)...")
    cur.execute("DROP TABLE huerfano_destinos")

    # --- 3. Verificacion antes de registrar la migracion como aplicada ---
    despues_remitos = cur.execute("SELECT COUNT(*) FROM remitos").fetchone()[0]
    despues_items = cur.execute("SELECT COUNT(*) FROM remitos_items").fetchone()[0]
    despues_notas = cur.execute("SELECT COUNT(*) FROM remitos_notas").fetchone()[0]
    despues_facturas_remitos = cur.execute("SELECT COUNT(*) FROM facturas_remitos").fetchone()[0]
    print(f"   Verificacion: remitos {antes_remitos} -> {despues_remitos} (copiadas: {filas_copiadas}), "
          f"remitos_items {antes_items} -> {despues_items}, remitos_notas {antes_notas} -> {despues_notas}, "
          f"facturas_remitos {antes_facturas_remitos} -> {despues_facturas_remitos}")
    if (despues_remitos != antes_remitos or despues_items != antes_items
            or despues_notas != antes_notas or despues_facturas_remitos != antes_facturas_remitos):
        raise RuntimeError(
            f"Conteo de filas no coincide tras la migracion -- remitos {antes_remitos}->{despues_remitos}, "
            f"remitos_items {antes_items}->{despues_items}, remitos_notas {antes_notas}->{despues_notas}, "
            f"facturas_remitos {antes_facturas_remitos}->{despues_facturas_remitos}. Abortando sin registrar."
        )

    # Chequeo de que los FKs hijos no quedaron apuntando a "remitos_old" (la trampa de
    # legacy_alter_table, misma verificacion que en 041/042).
    for tabla in ("remitos_items", "remitos_notas", "facturas_remitos"):
        sql_tabla = cur.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tabla,)
        ).fetchone()[0]
        if "remitos_old" in sql_tabla:
            raise RuntimeError(
                f"{tabla} quedo con un FK apuntando a remitos_old -- legacy_alter_table no tuvo "
                f"el efecto esperado. Abortando sin registrar."
            )

    cur.execute(
        "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION),
    )
    conn.commit()
    print(f"[migrate_043] OK — {MIGRATION_ID} aplicada. {despues_remitos} remitos intactos, huerfano_destinos eliminada.")

except sqlite3.OperationalError as e:
    conn.rollback()
    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
        print(f"[migrate_043] SKIP parcial -- {e}. Revisar a mano si la migracion quedo a mitad de camino "
              f"(la tabla remitos_old, si existe, es la senal). No se registro como aplicada.")
    else:
        print(f"[migrate_043] ERROR: {e}")
        raise
except Exception as e:
    conn.rollback()
    print(f"[migrate_043] ERROR: {e}")
    raise
finally:
    conn.close()
