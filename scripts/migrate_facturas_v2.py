"""
migrate_facturas_v2.py
Sonido Líquido V5 — Migración: Creación tabla facturas CANÓNICA
Fusión: Modelo ORM facturacion/ + Diseño Nike Arq 5.5 (Nivel GOLD)
Canonizado: 2026-05-01
"""

import sqlite3
import os
from datetime import datetime

# ── Rutas ─────────────────────────────────────────────────────────────────────
_DEFAULT_DEV  = r"C:\dev\Sonido_Liquido_V5\pilot_v5x.db"
_DEFAULT_PROD = r"C:\dev\v5-ls-Tom\data\V5_LS_MASTER.db"

def get_db_path():
    env = os.environ.get("DATABASE_URL", "")
    if env.startswith("sqlite:///"):
        return env.replace("sqlite:///", "")
    if os.environ.get("V5_ENV") == "prod":
        return _DEFAULT_PROD
    return _DEFAULT_DEV

# ── DDL ───────────────────────────────────────────────────────────────────────
CREATE_FACTURAS = """
CREATE TABLE IF NOT EXISTS facturas (
    -- Identidad
    id                      CHAR(32)    NOT NULL PRIMARY KEY,
    cliente_id              CHAR(32)    NOT NULL,
    pedido_id               CHAR(32),

    -- Dato fiscal historico (no FK - soporta CUIT nulo y Sello Azul)
    cuit_comprador          TEXT,

    -- Clasificacion AFIP
    tipo_comprobante        TEXT        NOT NULL DEFAULT 'PRESUPUESTO_X',
    punto_venta             INTEGER,
    numero_comprobante      INTEGER,
    fecha_emision           DATE,

    -- Estado operativo
    -- BORRADOR | LIQUIDADA_MANUAL | AUTORIZADA_AFIP | ANULADA
    estado                  TEXT        NOT NULL DEFAULT 'BORRADOR',

    -- Archivo original
    pdf_path                TEXT,

    -- Financiero
    neto_gravado            REAL        NOT NULL DEFAULT 0.0,
    iva_21                  REAL        NOT NULL DEFAULT 0.0,
    iva_105                 REAL        NOT NULL DEFAULT 0.0,
    exento                  REAL        NOT NULL DEFAULT 0.0,
    percepciones            REAL        NOT NULL DEFAULT 0.0,
    total                   REAL        NOT NULL DEFAULT 0.0,

    -- Sincronizacion ARCA
    cae                     TEXT,
    cae_vencimiento         DATE,

    -- Auditoria
    created_at              DATETIME    NOT NULL DEFAULT (datetime('now','utc')),

    -- Genoma 64 bits (Nike Arq 5.5 - Nivel GOLD)
    -- Bit  0 (1)     EXISTENCE
    -- Bit  1 (2)     VIRGINITY    - 1=virgen/borrado fisico permitido
    -- Bit  2 (4)     HAS_REMITO   - tiene remito asociado
    -- Bit  3 (8)     ACTIVE       - no anulada
    -- Bit  8 (256)   HAS_PEDIDO   - pedido_id poblado
    -- Bit 10 (1024)  V15_STRUCT   - nacio bajo canon V15 RESERVADO
    -- Bit 11 (2048)  DUPLICATE    - duplicado detectado en ingesta
    -- Bit 12 (4096)  PAID         - cobrada
    -- Bit 13 (8192)  RESERVADO    - no usar, colisiona con LAVIMAR 8205
    -- Bit 14 (16384) CAE_EXPIRED  - cae_vencimiento superado
    flags_estado            INTEGER     NOT NULL DEFAULT 3,

    -- Deduplicacion AFIP blindada (tipo + punto + numero)
    UNIQUE (tipo_comprobante, punto_venta, numero_comprobante),

    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (pedido_id)  REFERENCES pedidos(id)
);
"""

CREATE_FACTURAS_ITEMS = """
CREATE TABLE IF NOT EXISTS facturas_items (
    id                      INTEGER     PRIMARY KEY AUTOINCREMENT,
    factura_id              CHAR(32)    NOT NULL,
    pedido_item_id          INTEGER,
    remito_item_id          INTEGER,
    descripcion             TEXT        NOT NULL,
    cantidad                REAL        NOT NULL DEFAULT 1.0,
    precio_unitario_neto    REAL        NOT NULL DEFAULT 0.0,
    alicuota_iva            REAL        NOT NULL DEFAULT 21.0,
    subtotal_neto           REAL        NOT NULL DEFAULT 0.0,

    FOREIGN KEY (factura_id)     REFERENCES facturas(id),
    FOREIGN KEY (pedido_item_id) REFERENCES pedidos_items(id),
    FOREIGN KEY (remito_item_id) REFERENCES remitos_items(id)
);
"""

CREATE_FACTURAS_REMITOS = """
CREATE TABLE IF NOT EXISTS facturas_remitos (
    factura_id  CHAR(32) NOT NULL,
    remito_id   CHAR(32) NOT NULL,
    PRIMARY KEY (factura_id, remito_id),
    FOREIGN KEY (factura_id) REFERENCES facturas(id),
    FOREIGN KEY (remito_id)  REFERENCES remitos(id)
);
"""

INDICES = [
    ("ix_facturas_cliente_id",      "facturas",       "cliente_id"),
    ("ix_facturas_pedido_id",       "facturas",       "pedido_id"),
    ("ix_facturas_flags_estado",    "facturas",       "flags_estado"),
    ("ix_facturas_cae_vencimiento", "facturas",       "cae_vencimiento"),
    ("ix_facturas_estado",          "facturas",       "estado"),
    ("ix_facturas_items_factura",   "facturas_items", "factura_id"),
]

# ── Migracion ─────────────────────────────────────────────────────────────────
def migrate():
    db_path = get_db_path()
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] migrate_facturas_v2.py")
    print(f"  DB: {db_path}")

    if not os.path.exists(db_path):
        print(f"  ERROR: No se encuentra la base de datos.")
        return False

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    try:
        # Tablas
        cursor.execute(CREATE_FACTURAS)
        print("  [OK] Tabla 'facturas' creada.")

        cursor.execute(CREATE_FACTURAS_ITEMS)
        print("  [OK] Tabla 'facturas_items' creada.")

        cursor.execute(CREATE_FACTURAS_REMITOS)
        print("  [OK] Tabla 'facturas_remitos' (N:M) creada.")

        # Indices
        for idx_name, table, col in INDICES:
            cursor.execute(
                f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({col});"
            )
        print(f"  [OK] {len(INDICES)} indices creados.")

        conn.commit()

        # Verificacion
        for tabla in ("facturas", "facturas_items", "facturas_remitos"):
            cursor.execute(f"SELECT COUNT(*) FROM {tabla};")
            count = cursor.fetchone()[0]
            print(f"  [OK] {tabla}: {count} registros.")

        print(f"  [OK] Migracion v2 completada exitosamente.")
        return True

    except Exception as e:
        conn.rollback()
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    ok = migrate()
    exit(0 if ok else 1)
