from sqlalchemy import create_engine, text
import os

# 1. Configuración de conexión (Hardcoded para script one-off)
DATABASE_URL = "sqlite:///./pilot.db"

def migrate():
    print("🔵 Iniciando Migración V7.1: Add Observaciones to Domicilios...")
    
    if not os.path.exists("./pilot.db"):
        print("❌ Error: pilot.db no encontrado.")
        return

    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("PRAGMA table_info(domicilios)"))
            columns = [row.name for row in result.fetchall()]
            
            if 'observaciones' not in columns:
                print("🔹 Adding 'observaciones' column...")
                conn.execute(text("ALTER TABLE domicilios ADD COLUMN observaciones TEXT"))
                print("✅ Column added.")
            else:
                print("🔸 Column 'observaciones' already exists.")
                
            conn.commit()
            print("✅ Migration V7.1 Completed Successfully.")
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            conn.rollback()

if __name__ == "__main__":
    migrate()
