# backend/scripts/init_phase3.py
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
from backend.maestros import models as maestros_models

def init_db():
    # Create tables
    print("Creating tables for Phase 3...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    try:
        # Get Empresa
        empresa = db.query(log_models.EmpresaTransporte).filter_by(nombre="Expreso Cruz del Sur").first()
        if not empresa:
            print("Empresa 'Expreso Cruz del Sur' not found. Run Phase 2 init first.")
            return

        # Get Provincia
        provincia = db.query(maestros_models.Provincia).filter_by(id="C").first()
        if not provincia:
            print("Provincia 'C' not found. Run Phase 1 init first.")
            return

        # NodoTransporte
        nodos = [
            {
                "nombre_nodo": "Depósito Pompeya",
                "direccion_completa": "Av. Saenz 1234, CABA",
                "provincia_id": "C",
                "empresa_id": empresa.id,
                "es_punto_despacho": True,
                "horario_operativo": "Lunes a Viernes 8-17hs"
            },
            {
                "nombre_nodo": "Sucursal Bariloche",
                "direccion_completa": "Mitre 500, Bariloche",
                "provincia_id": "X", # Using X (Cordoba) as stub for Rio Negro if not exists, or just X. Wait, I loaded X as Cordoba. I should use what I loaded.
                "empresa_id": empresa.id,
                "es_punto_retiro": True
            }
        ]
        
        # Fix province for Bariloche if 'R' (Rio Negro) not loaded. I loaded C, B, X, S, M.
        # I'll use 'M' (Mendoza) for the second node just to be safe with FKs.
        nodos[1]["provincia_id"] = "M" 
        nodos[1]["nombre_nodo"] = "Sucursal Mendoza"

        for n in nodos:
            existing = db.query(log_models.NodoTransporte).filter_by(nombre_nodo=n["nombre_nodo"]).first()
            if not existing:
                db.add(log_models.NodoTransporte(**n))
                print(f"Added NodoTransporte: {n['nombre_nodo']}")

        db.commit()
        print("Phase 3 data initialized successfully.")
    except Exception as e:
        print(f"Error initializing Phase 3 data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
