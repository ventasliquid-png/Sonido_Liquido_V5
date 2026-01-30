
from sqlalchemy import create_engine, text
import json

DATABASE_URL = "sqlite:///pilot.db"

def migrate():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        try:
            print("Agregando columna 'roles' a tabla 'vinculos'...")
            conn.execute(text("ALTER TABLE vinculos ADD COLUMN roles JSON DEFAULT '[]'"))
            print("✅ Columna agregada.")
        except Exception as e:
            print(f"⚠️ Error (quizás ya existe): {e}")

if __name__ == "__main__":
    migrate()
