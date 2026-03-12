import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, engine, Base
from backend.maestros import models

def init_provincias_full():
    print("🇦🇷 Inicializando Maestro de Provincias (Full Argentina)...")
    
    db = SessionLocal()
    try:
        # ISO 3166-2:AR
        provincias = [
            {"id": "C", "nombre": "Ciudad Autónoma de Buenos Aires"},
            {"id": "B", "nombre": "Buenos Aires"},
            {"id": "K", "nombre": "Catamarca"},
            {"id": "H", "nombre": "Chaco"},
            {"id": "U", "nombre": "Chubut"},
            {"id": "X", "nombre": "Córdoba"},
            {"id": "W", "nombre": "Corrientes"},
            {"id": "E", "nombre": "Entre Ríos"},
            {"id": "P", "nombre": "Formosa"},
            {"id": "Y", "nombre": "Jujuy"},
            {"id": "L", "nombre": "La Pampa"},
            {"id": "F", "nombre": "La Rioja"},
            {"id": "M", "nombre": "Mendoza"},
            {"id": "N", "nombre": "Misiones"},
            {"id": "Q", "nombre": "Neuquén"},
            {"id": "R", "nombre": "Río Negro"},
            {"id": "A", "nombre": "Salta"},
            {"id": "J", "nombre": "San Juan"},
            {"id": "D", "nombre": "San Luis"},
            {"id": "Z", "nombre": "Santa Cruz"},
            {"id": "S", "nombre": "Santa Fe"},
            {"id": "G", "nombre": "Santiago del Estero"},
            {"id": "V", "nombre": "Tierra del Fuego"},
            {"id": "T", "nombre": "Tucumán"},
        ]
        
        count = 0
        for p in provincias:
            existing = db.query(models.Provincia).filter_by(id=p["id"]).first()
            if not existing:
                db.add(models.Provincia(**p))
                count += 1
            else:
                # Update name just in case
                if existing.nombre != p["nombre"]:
                    existing.nombre = p["nombre"]
                    count += 1
        
        db.commit()
        print(f"✅ Se actualizaron/insertaron {count} provincias.")
        
        # Verificar total
        total = db.query(models.Provincia).count()
        print(f"📊 Total en base de datos: {total} provincias.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_provincias_full()
