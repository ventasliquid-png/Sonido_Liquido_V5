# scripts/migrate_stock_columns.py
import sys
import os
from sqlalchemy import text

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.core.database import engine

def migrate():
    print("Iniciando migración de columnas STOCK en PRODUCTOS...")
    try:
        with engine.connect() as conn:
            # Postgres specific add column if not exists logic or simple add with try/catch
            # Since we are in controlled environment, we can try adding.
            try:
                print("Agregando columna stock_fisico...")
                conn.execute(text("ALTER TABLE productos ADD COLUMN stock_fisico NUMERIC(10, 2) DEFAULT 0.0"))
            except Exception as e:
                print(f"⚠️ Alerta (stock_fisico): {e}")
                
            try:
                print("Agregando columna stock_reservado...")
                conn.execute(text("ALTER TABLE productos ADD COLUMN stock_reservado NUMERIC(10, 2) DEFAULT 0.0"))
            except Exception as e:
                print(f"⚠️ Alerta (stock_reservado): {e}")

            conn.commit()
        print("✅ Migración de Stock finalizada.")
    except Exception as e:
        print(f"❌ Error General: {e}")

if __name__ == "__main__":
    migrate()
