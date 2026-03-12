# backend/scripts/init_maestros.py
import sys
import os

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from backend.maestros import models

def init_db():
    # Create tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    try:
        # Provincias
        provincias = [
            {"id": "C", "nombre": "Ciudad Autónoma de Buenos Aires"},
            {"id": "B", "nombre": "Buenos Aires"},
            {"id": "X", "nombre": "Córdoba"},
            {"id": "S", "nombre": "Santa Fe"},
            {"id": "M", "nombre": "Mendoza"},
        ]
        for p in provincias:
            existing = db.query(models.Provincia).filter_by(id=p["id"]).first()
            if not existing:
                db.add(models.Provincia(**p))
                print(f"Added Provincia: {p['nombre']}")
        
        # TipoContacto
        tipos = [
            {"id": "COMPRAS", "nombre": "Responsable de Compras"},
            {"id": "PAGOS", "nombre": "Responsable de Pagos"},
            {"id": "DUEÑO", "nombre": "Dueño / Socio"},
            {"id": "CALIDAD", "nombre": "Control de Calidad"},
        ]
        for t in tipos:
            existing = db.query(models.TipoContacto).filter_by(id=t["id"]).first()
            if not existing:
                db.add(models.TipoContacto(**t))
                print(f"Added TipoContacto: {t['nombre']}")

        # CondicionIva (Stub data)
        condiciones = ["Responsable Inscripto", "Monotributista", "Exento", "Consumidor Final"]
        for c_name in condiciones:
            existing = db.query(models.CondicionIva).filter_by(nombre=c_name).first()
            if not existing:
                db.add(models.CondicionIva(nombre=c_name))
                print(f"Added CondicionIva: {c_name}")

        # ListaPrecios (Stub data)
        listas = ["Lista Mayorista", "Lista Minorista", "Lista Distribuidor"]
        for l_name in listas:
            existing = db.query(models.ListaPrecios).filter_by(nombre=l_name).first()
            if not existing:
                db.add(models.ListaPrecios(nombre=l_name))
                print(f"Added ListaPrecios: {l_name}")

        db.commit()
        print("Master data initialized successfully.")
    except Exception as e:
        print(f"Error initializing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
