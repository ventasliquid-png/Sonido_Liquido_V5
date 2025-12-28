import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import text
from backend.core.database import SessionLocal

def add_column():
    db = SessionLocal()
    try:
        print("Checking if column 'tipo_comprobante' exists in 'pedidos' (SQLite Mode)...")
        # SQLite specific check
        result = db.execute(text("PRAGMA table_info(pedidos)")).fetchall()
        # Result columns: cid, name, type, notnull, dflt_value, pk
        
        column_exists = any(row[1] == 'tipo_comprobante' for row in result)
        
        if not column_exists:
            print("Adding 'tipo_comprobante' column...")
            alter_sql = text("ALTER TABLE pedidos ADD COLUMN tipo_comprobante VARCHAR DEFAULT 'FISCAL';")
            db.execute(alter_sql)
            db.commit()
            print("Column added successfully.")
        else:
            print("Column already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_column()
