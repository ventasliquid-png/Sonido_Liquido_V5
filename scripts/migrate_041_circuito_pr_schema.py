"""
migrate_041_circuito_pr_schema.py
====================================
Etapa 1 del PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md -- migracion de esquema completa,
dictaminada por Nike (BIBLIOTECA_NIKE.md Modulo 2, tres entradas del 2026-09-23) sobre
INFORME_IMPLEMENTACION_PR_S869.md / DISENO_CIRCUITO_17_S870.md.

Todo lo de abajo es aditivo: columnas nuevas nullable (o con DEFAULT), dos tablas nuevas, y una
relajacion de NOT NULL a nullable en remitos.pedido_id. Cero filas existentes cambian de
significado -- remitos_items.cantidad_declarada se backfillea igual a la cantidad remitida de
siempre, porque hoy no existe ningun "armado" que las distinga (eso es la Etapa 4).

Incluye Pedido.pedido_origen_id / motivo_relacion_oc (paso 5). La contradiccion detectada el
23/09 contra la Doctrina de Linaje de Identidad de Cliente (que dice "nunca NULL,
autorreferencial por default") quedo resuelta por Nike en dialogo socratico el mismo dia:
Cliente es un linaje de identidad inmutable (nunca NULL); Pedido es una relacion causal de
derivacion OPCIONAL (~95% autonomos) -- ahí NULL es el caso normal. Integer, no UUID (Pedido.id
es Integer). Ver BIBLIOTECA_NIKE.md Modulo 2 y PLAN_IMPLEMENTACION_CIRCUITO_PR_2026-09-23.md.

remitos.pedido_id nullable requiere reconstruir la tabla (SQLite no soporta ALTER COLUMN DROP
NOT NULL) -- mismo patron ya usado en migrate_v8_hybrid_client.py (rename a _old, crear tabla
nueva, copiar filas, borrar _old). El FK de domicilio_entrega_id se preserva tal cual esta HOY
en la base real ("domicilios_legacy", verificado por sqlite_master -- el modelo Python declara
"domicilios", ya era drift preexistente, no se toca acá).

MIGRATION_ID = "041_circuito_pr_schema"
NRO_SESION = 871  # continuacion de S870 (2026-09-23), sin ceremonia ALFA/OMEGA completa
"""
import sqlite3
import os

MIGRATION_ID = "041_circuito_pr_schema"
NRO_SESION = 871

DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "pilot_v5x.db"
)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

ya_aplicada = cur.execute(
    "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)
).fetchone()

if ya_aplicada:
    print(f"[migrate_041] SKIP — {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_041] Iniciando {MIGRATION_ID}...")
    antes_remitos = cur.execute("SELECT COUNT(*) FROM remitos").fetchone()[0]
    antes_items = cur.execute("SELECT COUNT(*) FROM remitos_items").fetchone()[0]
    antes_pedidos = cur.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]

    # --- 1. remitos_items: cuatro cantidades (INFORME §4.1, dictamen Nike puntos 3/4/6) ---
    print("[1] remitos_items: agregando cantidad_declarada / cantidad_recibida / cantidad_facturada...")
    cur.execute("ALTER TABLE remitos_items ADD COLUMN cantidad_declarada FLOAT NOT NULL DEFAULT 0.0")
    cur.execute("UPDATE remitos_items SET cantidad_declarada = cantidad")
    cur.execute("ALTER TABLE remitos_items ADD COLUMN cantidad_recibida FLOAT")
    cur.execute("ALTER TABLE remitos_items ADD COLUMN cantidad_facturada FLOAT")
    print("   -> Renombrando 'cantidad' a 'cantidad_remitida'...")
    cur.execute("ALTER TABLE remitos_items RENAME COLUMN cantidad TO cantidad_remitida")

    # --- 2. remitos_notas (tabla nueva, INFORME §4.1, dictamen Nike) ---
    print("[2] Creando tabla remitos_notas...")
    cur.execute("""
        CREATE TABLE remitos_notas (
            id INTEGER NOT NULL,
            remito_id CHAR(32) NOT NULL,
            remito_item_id INTEGER,
            fecha DATETIME,
            autor_id INTEGER,
            texto VARCHAR NOT NULL,
            foto_path VARCHAR,
            PRIMARY KEY (id),
            FOREIGN KEY(remito_id) REFERENCES remitos (id),
            FOREIGN KEY(remito_item_id) REFERENCES remitos_items (id),
            FOREIGN KEY(autor_id) REFERENCES usuarios (id)
        )
    """)

    # --- 3. huerfano_destinos (tabla nueva, DISENO_CIRCUITO_17_S870.md §5, dictamen Nike) ---
    print("[3] Creando tabla huerfano_destinos...")
    cur.execute("""
        CREATE TABLE huerfano_destinos (
            id INTEGER NOT NULL,
            huerfano_item_id INTEGER NOT NULL,
            fecha DATETIME,
            tipo VARCHAR NOT NULL,
            cantidad FLOAT NOT NULL,
            referencia INTEGER,
            autor_id INTEGER,
            PRIMARY KEY (id),
            FOREIGN KEY(huerfano_item_id) REFERENCES remitos_items (id),
            FOREIGN KEY(referencia) REFERENCES pedidos (id),
            FOREIGN KEY(autor_id) REFERENCES usuarios (id),
            CHECK (tipo IN ('reingreso', 'perdida', 'comercializado'))
        )
    """)

    # --- 4. remitos: pedido_id nullable + motivo (Circuito 17, DISENO_CIRCUITO_17_S870.md §3/§6) ---
    # SQLite no soporta relajar NOT NULL con ALTER COLUMN -- reconstruir la tabla (mismo patron
    # que migrate_v8_hybrid_client.py). Schema calcado 1:1 del sqlite_master real de HOY, con
    # los dos cambios de esta etapa y nada mas -- el FK de domicilio_entrega_id a
    # "domicilios_legacy" es el que ya tiene la base viva, no el que declara el modelo Python.
    print("[4] remitos: relajando pedido_id a nullable + agregando 'motivo' (reconstruccion de tabla)...")
    cur.execute("PRAGMA foreign_keys=OFF")
    # [Trampa de SQLite, encontrada y corregida en esta migracion] Desde SQLite 3.25,
    # "ALTER TABLE x RENAME TO y" reescribe SOLO EN TEXTO las clausulas FOREIGN KEY de
    # cualquier OTRA tabla que apunte a x, cambiandolas a "y" -- remitos_items y remitos_notas
    # quedarian con "REFERENCES remitos_old(id)" para siempre, aunque el "remitos" nuevo tome
    # ese nombre despues. legacy_alter_table=ON desactiva esa reescritura durante el rename
    # temporal, asi que el texto se queda diciendo "remitos" todo el tiempo -- correcto una vez
    # que la tabla nueva ocupa ese nombre. Verificado con sqlite_master antes y despues.
    cur.execute("PRAGMA legacy_alter_table=ON")

    cur.execute("DROP INDEX IF EXISTS ix_remitos_pedido_id")
    cur.execute("DROP INDEX IF EXISTS ix_remitos_id")
    cur.execute("ALTER TABLE remitos RENAME TO remitos_old")

    cur.execute("""
        CREATE TABLE remitos (
            id CHAR(32) NOT NULL,
            pedido_id INTEGER,
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
            "flags_estado")
    cur.execute(f"INSERT INTO remitos ({cols}) SELECT {cols} FROM remitos_old")

    filas_copiadas = cur.rowcount
    cur.execute("DROP TABLE remitos_old")

    cur.execute("CREATE INDEX ix_remitos_pedido_id ON remitos (pedido_id)")
    cur.execute("CREATE INDEX ix_remitos_id ON remitos (id)")
    cur.execute("PRAGMA legacy_alter_table=OFF")
    cur.execute("PRAGMA foreign_keys=ON")

    # --- 5. pedidos: pedido_origen_id + motivo_relacion_oc (BIBLIOTECA_NIKE.md Modulo 2,
    # resuelto en dialogo socratico 23/09 tras la contradiccion detectada contra la Doctrina de
    # Linaje de Identidad de Cliente -- acá NULL es el caso normal, ~95% de los pedidos son
    # autonomos, a diferencia de Cliente.cliente_origen_id que nunca es NULL) ---
    print("[5] pedidos: agregando pedido_origen_id / motivo_relacion_oc...")
    cur.execute("ALTER TABLE pedidos ADD COLUMN pedido_origen_id INTEGER REFERENCES pedidos(id)")
    cur.execute("ALTER TABLE pedidos ADD COLUMN motivo_relacion_oc VARCHAR")

    # --- 6. Verificacion antes de registrar la migracion como aplicada ---
    despues_remitos = cur.execute("SELECT COUNT(*) FROM remitos").fetchone()[0]
    despues_items = cur.execute("SELECT COUNT(*) FROM remitos_items").fetchone()[0]
    despues_pedidos = cur.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    print(f"   Verificacion: remitos {antes_remitos} -> {despues_remitos} (copiadas: {filas_copiadas}), "
          f"remitos_items {antes_items} -> {despues_items}, pedidos {antes_pedidos} -> {despues_pedidos}")
    if despues_remitos != antes_remitos or despues_items != antes_items or despues_pedidos != antes_pedidos:
        raise RuntimeError(
            f"Conteo de filas no coincide tras la migracion -- remitos {antes_remitos}->{despues_remitos}, "
            f"remitos_items {antes_items}->{despues_items}, pedidos {antes_pedidos}->{despues_pedidos}. "
            f"Abortando sin registrar."
        )

    cur.execute(
        "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (MIGRATION_ID, NRO_SESION),
    )
    conn.commit()
    print(f"[migrate_041] OK — {MIGRATION_ID} aplicada. {despues_remitos} remitos, {despues_items} remitos_items intactos.")

except sqlite3.OperationalError as e:
    conn.rollback()
    if "duplicate column name" in str(e).lower() or "already exists" in str(e).lower():
        print(f"[migrate_041] SKIP parcial -- {e}. Revisar a mano si la migracion quedo a mitad de camino "
              f"(la tabla remitos_old, si existe, es la senal). No se registro como aplicada.")
    else:
        print(f"[migrate_041] ERROR: {e}")
        raise
except Exception as e:
    conn.rollback()
    print(f"[migrate_041] ERROR: {e}")
    raise
finally:
    conn.close()
