import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "pilot.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

sys.path.append(BASE_DIR)

print(f"🚀 INICIANDO MIGRACIÓN V8: CLIENTE HÍBRIDO (V5-X)")
print(f"📂 Base de Datos: {DB_PATH}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def run_migration():
    try:
        # 1. Agregar columna flags_estado
        print("1️⃣  Agregando columna 'flags_estado'...")
        try:
            session.execute(text("ALTER TABLE clientes ADD COLUMN flags_estado INTEGER NOT NULL DEFAULT 0"))
            print("   ✅ Columna agregada.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("   ⚠️ La columna ya existe.")
            else:
                raise e

        # 2. Relajar restricción de CUIT (SQLite no soporta ALTER COLUMN DROP NOT NULL fácilmente)
        # SQLite requiere recrear la tabla para cambiar constraints, pero podemos intentar un hack
        # O simplemente aceptar que las nuevas filas pueden tener NULL si el schema lo permite en código (SQLAlchemy)
        # y la base vieja tenía NOT NULL.
        # WAIT: SQLite legacy tables might enforce NOT NULL if created that way.
        # Strategy: "The SQLite Way" -> Create new table, copy data, swap.
        
        print("2️⃣  Aplicando NULLABLE a columna 'CUIT' (Strategy: Rebuild Table)...")
        # Verificar si 'cuit' es nulo
        # En SQLite, si la tabla original tiene "cuit TEXT NOT NULL", fallará al insertar NULL.
        # No podemos hacer "ALTER COLUMN" en SQLite estándar.
        
        # Check if we really need to rebuild. 
        # If we can't alter column, we might just leave it as is physically but insert dummy data?
        # NO. The requirement is nullable=True.
        # Let's check table info first.
        
        # PRAGMA table_info(clientes); (cid, name, type, notnull, dflt_value, pk)
        
        # HACK: If we are in development, we can rename table and recreate.
        # But keeping data is critical.
        
        # TRANSACTION START
        session.execute(text("PRAGMA foreign_keys=OFF"))
        
        # A. Rename current table
        print("   -> Renombrando tabla actual a 'clientes_old'...")
        try:
             # Drop indices from old table to free up names
             # Note: In SQLite, indices are attached to table. We try to drop them if they exist.
             # But if we rename table, indices move with it.
             # If we want to reuse names 'ix_clientes_id', we must drop them from 'clientes_old'.
             # However, we don't know if they exist for sure.
             indices = ["ix_clientes_id", "ix_clientes_razon_social", "ix_clientes_cuit", "ix_clientes_codigo_interno"]
             for idx in indices:
                 session.execute(text(f"DROP INDEX IF EXISTS {idx}"))
             
             session.execute(text("ALTER TABLE clientes RENAME TO clientes_old"))
        except Exception as e:
            if "no such table: clientes" in str(e).lower():
                # Maybe already renamed?
                pass
            else:
               # If it fails, maybe clientes_old exists?
               session.execute(text("DROP TABLE IF EXISTS clientes_old"))
               session.execute(text("ALTER TABLE clientes RENAME TO clientes_old"))

        # B. Create new table with strict schema (From models definition)
        print("   -> Creando nueva tabla 'clientes' con Schema V5-X...")
        
        # Definition extracted from models.py (Manual SQL to ensure precision)
        create_table_sql = """
        CREATE TABLE clientes (
            id CHAR(32) NOT NULL, 
            razon_social VARCHAR NOT NULL, 
            nombre_fantasia VARCHAR, 
            cuit VARCHAR, 
            codigo_interno INTEGER, 
            legacy_id_bas VARCHAR, 
            flags_estado INTEGER NOT NULL DEFAULT 0,
            whatsapp_empresa VARCHAR, 
            web_portal_pagos VARCHAR, 
            datos_acceso_pagos TEXT, 
            observaciones TEXT, 
            condicion_iva_id CHAR(32), 
            lista_precios_id CHAR(32), 
            segmento_id CHAR(32), 
            vendedor_id INTEGER, 
            estrategia_precio VARCHAR DEFAULT 'MAYORISTA_FISCAL', 
            saldo_actual NUMERIC(18, 2) DEFAULT 0.00, 
            activo BOOLEAN NOT NULL DEFAULT 1, 
            requiere_auditoria BOOLEAN DEFAULT 0, 
            contador_uso INTEGER DEFAULT 0, 
            historial_cache JSON, 
            estado_arca VARCHAR NOT NULL DEFAULT 'PENDIENTE', 
            datos_arca_last_update DATETIME, 
            created_at DATETIME, 
            updated_at DATETIME, 
            PRIMARY KEY (id), 
            FOREIGN KEY(condicion_iva_id) REFERENCES condiciones_iva (id), 
            FOREIGN KEY(lista_precios_id) REFERENCES listas_precios (id), 
            FOREIGN KEY(segmento_id) REFERENCES segmentos (id), 
            FOREIGN KEY(vendedor_id) REFERENCES usuarios (id)
        )
        """
        session.execute(text(create_table_sql))
        
        # Indices
        print("   -> Recreando índices...")
        session.execute(text("CREATE INDEX ix_clientes_id ON clientes (id)"))
        session.execute(text("CREATE INDEX ix_clientes_razon_social ON clientes (razon_social)"))
        session.execute(text("CREATE INDEX ix_clientes_cuit ON clientes (cuit)"))
        session.execute(text("CREATE UNIQUE INDEX ix_clientes_codigo_interno ON clientes (codigo_interno)"))

        # C. Copy Data
        print("   -> Migrando datos de 'clientes_old' a 'clientes'...")
        # Note: We map flags_estado manually if needed, but it's new. 
        # But wait, we added flags_estado to clientes (old) in step 1?
        # Yes, so clientes_old has it.
        
        # We need to list columns to assume order or explicit mapping.
        # Explicit is better.
        
        columns_common = [
            "id", "razon_social", "nombre_fantasia", "cuit", "codigo_interno", "legacy_id_bas", 
            "whatsapp_empresa", "web_portal_pagos", "datos_acceso_pagos", 
            "observaciones", "condicion_iva_id", "lista_precios_id", "segmento_id", "vendedor_id", 
            "estrategia_precio", "saldo_actual", "activo", "requiere_auditoria", "contador_uso", 
            "historial_cache", "estado_arca", "datos_arca_last_update", "created_at", "updated_at",
            "flags_estado"
        ]
        
        cols_str = ", ".join(columns_common)
        
        insert_sql = f"INSERT INTO clientes ({cols_str}) SELECT {cols_str} FROM clientes_old"
        session.execute(text(insert_sql))
        
        # D. Migration Logic: Set Initial Flags based on legacy 'activo'
        print("   -> Calculando Flags iniciales (Legacy Conversion)...")
        # IS_ACTIVE (Bit 0) = 1 if activo=True
        # IS_VIRGIN (Bit 1) = 0 (Assume all migrated are used)
        # FISCAL_REQUIRED (Bit 2) = 1 (Assume all legacy are Gold/Silver)
        
        # UPDATE clientes SET flags_estado = flags_estado | 1 WHERE activo = 1
        session.execute(text("UPDATE clientes SET flags_estado = flags_estado | 1 WHERE activo = 1"))
        
        # UPDATE clientes SET flags_estado = flags_estado | 4  (FISCAL_REQUIRED for all legacy)
        session.execute(text("UPDATE clientes SET flags_estado = flags_estado | 4"))
        
        
        # Cleanup
        print("   -> Eliminando tabla temporal 'clientes_old'...")
        session.execute(text("DROP TABLE clientes_old"))
        
        session.execute(text("PRAGMA foreign_keys=ON"))
        session.commit()
        
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE.")
        
    except Exception as e:
        session.rollback()
        print(f"❌ ERROR FATAL EN MIGRACIÓN: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    run_migration()
