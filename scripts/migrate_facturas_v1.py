"""
migrate_facturas_v1.py
Sonido Líquido V5 — Migración: Creación tabla facturas
Canonizado: 2026-05-01
Aprobado: Nike Arq 5.5 — Nivel GOLD
"""

import sqlite3
import os
from datetime import datetime

# ── Rutas ────────────────────────────────────────────────────────────────────
# Lee DATABASE_URL del entorno si existe, sino usa el path por defecto del repo
_DEFAULT_DEV  = r"C:\dev\Sonido_Liquido_V5\pilot_v5x.db"
_DEFAULT_PROD = r"C:\dev\v5-ls-Tom\data\V5_LS_MASTER.db"

def get_db_path():
    env = os.environ.get("DATABASE_URL", "")
    if env.startswith("sqlite:///"):
        return env.replace("sqlite:///", "")
    # Detectar por variable de entorno V5_ENV
    if os.environ.get("V5_ENV") == "prod":
        return _DEFAULT_PROD
    return _DEFAULT_DEV

# ── DDL ──────────────────────────────────────────────────────────────────────
CREATE_FACTURAS = """
CREATE TABLE IF NOT EXISTS facturas (
    id                  CHAR(32)    NOT NULL PRIMARY KEY,
    cliente_id          CHAR(32)    NOT NULL,
    cuit_comprador      TEXT,
    tipo_comprobante    TEXT        NOT NULL,
    punto_de_venta      INTEGER     NOT NULL,
    numero_factura      TEXT        NOT NULL,
    fecha               DATE        NOT NULL,
    pdf_path            TEXT,
    cae                 TEXT,
    cae_vencimiento     DATE,
    pedido_id           CHAR(32),
    flags_estado        INTEGER     NOT NULL DEFAULT 3,

    UNIQUE (tipo_comprobante, punto_de_venta, numero_factura),
    FOREIGN KEY (cliente_id)  REFERENCES clientes(id),
    FOREIGN KEY (pedido_id)   REFERENCES pedidos(id)
);
"""

CREATE_IDX_CLIENTE = """
CREATE INDEX IF NOT EXISTS ix_facturas_cliente_id
ON facturas (cliente_id);
"""

CREATE_IDX_PEDIDO = """
CREATE INDEX IF NOT EXISTS ix_facturas_pedido_id
ON facturas (pedido_id);
"""

CREATE_IDX_FLAGS = """
CREATE INDEX IF NOT EXISTS ix_facturas_flags_estado
ON facturas (flags_estado);
"""

CREATE_IDX_CAE_VTO = """
CREATE INDEX IF NOT EXISTS ix_facturas_cae_vencimiento
ON facturas (cae_vencimiento);
"""

# ── Migración ─────────────────────────────────────────────────────────────────
def migrate():
    db_path = get_db_path()
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] migrate_facturas_v1.py")
    print(f"  DB: {db_path}")

    if not os.path.exists(db_path):
        print(f"  ERROR: No se encuentra la base de datos.")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Tabla principal
        cursor.execute(CREATE_FACTURAS)
        print("  [OK] Tabla 'facturas' creada (o ya existia).")

        # Índices
        cursor.execute(CREATE_IDX_CLIENTE)
        cursor.execute(CREATE_IDX_PEDIDO)
        cursor.execute(CREATE_IDX_FLAGS)
        cursor.execute(CREATE_IDX_CAE_VTO)
        print("  [OK] Indices creados.")

        conn.commit()

        # Verificación
        cursor.execute("SELECT COUNT(*) FROM facturas;")
        count = cursor.fetchone()[0]
        print(f"  [OK] Verificacion OK -- registros en tabla: {count}")
        print(f"  [OK] Migracion completada exitosamente.")
        return True

    except Exception as e:
        conn.rollback()
        print(f"  ERROR: {e}")
        return False

    finally:
        conn.close()


if __name__ == "__main__":
    ok = migrate()
    exit(0 if ok else 1)
