import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import engine

def add_rubro_codigo():
    print("--- Agregando columna 'codigo' a tabla 'rubros' ---")
    
    with engine.connect() as connection:
        try:
            # Check if column exists first (to be safe)
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='rubros' AND column_name='codigo'"))
            if result.fetchone():
                print("⚠️ La columna 'codigo' ya existe.")
            else:
                print("🛠️ Agregando columna 'codigo'...")
                # Add column as nullable first, then populate or leave nullable?
                # Model says nullable=False. We need to provide a default or handle it.
                # Let's add it as nullable first.
                connection.execute(text("ALTER TABLE rubros ADD COLUMN codigo VARCHAR(3)"))
                connection.execute(text("CREATE UNIQUE INDEX ix_rubros_codigo ON rubros (codigo)"))
                connection.commit()
                print("✅ Columna 'codigo' agregada exitosamente.")
        except Exception as e:
            print(f"❌ Error modificando tabla: {e}")

if __name__ == "__main__":
    add_rubro_codigo()
