from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.core.database import SessionLocal

def nuke_orders():
    print("Iniciando purga de pedidos (Modo SQL Directo)...")
    db = SessionLocal()
    try:
        # Delete items first
        db.execute(text("DELETE FROM pedidos_items;"))
        print("DELETE FROM pedidos_items ejecutado.")
        
        # Delete headers
        db.execute(text("DELETE FROM pedidos;"))
        print("DELETE FROM pedidos ejecutado.")
        
        # Reset SQLite sequences if desired (optional)
        # db.execute(text("DELETE FROM sqlite_sequence WHERE name='pedidos';"))
        
        db.commit()
        print("Purga completada con éxito.")
    except Exception as e:
        print(f"Error durante la purga: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    nuke_orders()
