# backend/scripts/init_phase2.py
import sys
import os

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from backend.logistica import models as log_models
from backend.agenda import models as agenda_models

def init_db():
    # Create tables
    print("Creating tables for Phase 2...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    try:
        # EmpresaTransporte
        empresas = [
            {"nombre": "Expreso Cruz del Sur", "web_tracking": "https://cruzdelsur.com/tracking", "requiere_carga_web": True},
            {"nombre": "Vía Cargo", "web_tracking": "https://viacargo.com.ar/tracking", "requiere_carga_web": False},
            {"nombre": "Mercado Envíos", "web_tracking": "https://mercadolibre.com.ar", "requiere_carga_web": False},
        ]
        for e in empresas:
            existing = db.query(log_models.EmpresaTransporte).filter_by(nombre=e["nombre"]).first()
            if not existing:
                db.add(log_models.EmpresaTransporte(**e))
                print(f"Added EmpresaTransporte: {e['nombre']}")

        # Persona
        personas = [
            {"nombre_completo": "Juan Perez", "email_personal": "juan.perez@gmail.com", "celular_personal": "+5491112345678"},
            {"nombre_completo": "Maria Gonzalez", "email_personal": "maria.gonzalez@hotmail.com", "linkedin": "https://linkedin.com/in/mariagonzalez"},
        ]
        for p in personas:
            existing = db.query(agenda_models.Persona).filter_by(email_personal=p["email_personal"]).first()
            if not existing:
                db.add(agenda_models.Persona(**p))
                print(f"Added Persona: {p['nombre_completo']}")

        db.commit()
        print("Phase 2 data initialized successfully.")
    except Exception as e:
        print(f"Error initializing Phase 2 data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
