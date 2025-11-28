from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Database connection
DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_transports():
    db = SessionLocal()
    try:
        # Count transport usage in Domicilios
        query = text("""
            SELECT t.nombre, COUNT(d.id) as count
            FROM domicilios d
            LEFT JOIN transportes t ON d.transporte_id = t.id
            GROUP BY t.nombre
            ORDER BY count DESC
        """)
        result = db.execute(query).fetchall()
        
        print("\n--- Distribución de Transportes en Domicilios ---")
        if not result:
            print("No hay domicilios con transporte asignado.")
        for row in result:
            transport_name = row[0] if row[0] else "Sin Transporte (NULL)"
            print(f"{transport_name}: {row[1]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_transports()
