from sqlalchemy import create_engine, text
import os

# 1. Configuración de conexión (Hardcoded para script one-off)
DATABASE_URL = "sqlite:///./pilot.db"

def migrate():
    print("🔵 Iniciando Migración V7.2: Campos de Entrega...")
    
    if not os.path.exists("./pilot.db"):
        print("❌ Error: pilot.db no encontrado.")
        return

    engine = create_engine(DATABASE_URL)
    
    commands = [
        ("calle_entrega", "ALTER TABLE domicilios ADD COLUMN calle_entrega VARCHAR"),
        ("numero_entrega", "ALTER TABLE domicilios ADD COLUMN numero_entrega VARCHAR"),
        ("piso_entrega", "ALTER TABLE domicilios ADD COLUMN piso_entrega VARCHAR"),
        ("depto_entrega", "ALTER TABLE domicilios ADD COLUMN depto_entrega VARCHAR"),
        ("cp_entrega", "ALTER TABLE domicilios ADD COLUMN cp_entrega VARCHAR"),
        ("localidad_entrega", "ALTER TABLE domicilios ADD COLUMN localidad_entrega VARCHAR"),
        ("provincia_entrega_id", "ALTER TABLE domicilios ADD COLUMN provincia_entrega_id VARCHAR(5) REFERENCES provincias(id)")
    ]
    
    with engine.connect() as conn:
        try:
             # Check columns
            result = conn.execute(text("PRAGMA table_info(domicilios)"))
            existing_columns = [row.name for row in result.fetchall()]
            
            for col_name, cmd in commands:
                if col_name not in existing_columns:
                    print(f"🔹 Adding '{col_name}' column...")
                    conn.execute(text(cmd))
                else:
                    print(f"🔸 Column '{col_name}' already exists.")
            
            conn.commit()
            print("✅ Migration V7.2 Completed Successfully.")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate()
