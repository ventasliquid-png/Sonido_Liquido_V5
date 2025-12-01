import sys
import os
import random

# Add the project root to the python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import Base, DATABASE_URL
from logistica.models import EmpresaTransporte
import maestros.models # Required for relationship resolution

def seed_transportes():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("Seeding 25 dummy transports...")
        for i in range(1, 26):
            nombre = f"Transporte T{i}"
            # Check if exists
            existing = db.query(EmpresaTransporte).filter(EmpresaTransporte.nombre == nombre).first()
            if existing:
                print(f"Skipping {nombre} (already exists)")
                continue

            transporte = EmpresaTransporte(
                nombre=nombre,
                telefono_reclamos=f"+54 9 11 {random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                web_tracking=f"https://tracking.t{i}.com",
                activo=random.choice([True, True, True, False]), # Mostly active
                requiere_carga_web=random.choice([True, False]),
                formato_etiqueta=random.choice(['PROPIA', 'EXTERNA_PDF'])
            )
            db.add(transporte)
        
        db.commit()
        print("Successfully seeded 25 transports.")
    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_transportes()
