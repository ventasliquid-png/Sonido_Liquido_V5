import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, engine, Base
from backend.maestros import models as m_models
import uuid

def seed_maestros():
    db = SessionLocal()
    try:
        # 1. Condiciones IVA
        condiciones = [
            "Responsable Inscripto",
            "Monotributo",
            "Consumidor Final",
            "Exento",
            "No Responsable",
            "Sujeto No Categorizado"
        ]
        
        print("--- Seeding Condiciones IVA ---")
        for nombre in condiciones:
            existing = db.query(m_models.CondicionIva).filter_by(nombre=nombre).first()
            if not existing:
                db.add(m_models.CondicionIva(nombre=nombre))
                print(f"Created: {nombre}")
            else:
                print(f"Exists: {nombre}")

        # 2. Segmentos (Rubros/Ramos) - UPDATED with User Feedback
        segmentos_correctos = [
            "Industria",
            "Medicina",
            "Laboratorios Varios",
            "Gastronomía",
            "Gobierno",
            "Instituciones",
            "General"
        ]
        
        segmentos_incorrectos = [
            "Mayorista", "Minorista", "Distribuidor", "Kiosco/Almacén", "Supermercado", "Corporativo"
        ]

        print("\n--- Cleaning up Incorrect Segmentos ---")
        for nombre in segmentos_incorrectos:
            existing = db.query(m_models.Segmento).filter_by(nombre=nombre).first()
            if existing:
                try:
                    db.delete(existing)
                    print(f"Deleted incorrect: {nombre}")
                except Exception:
                    print(f"Could not delete (used?): {nombre}")

        print("\n--- Seeding Correct Segmentos ---")
        for nombre in segmentos_correctos:
            existing = db.query(m_models.Segmento).filter_by(nombre=nombre).first()
            if not existing:
                db.add(m_models.Segmento(nombre=nombre))
                print(f"Created: {nombre}")
            else:
                print(f"Exists: {nombre}")

        # 3. Provincias (Standard Argentina)
        provincias = [
            ("C", "Ciudad Autónoma de Buenos Aires"),
            ("B", "Buenos Aires"),
            ("X", "Córdoba"),
            ("S", "Santa Fe"),
            ("M", "Mendoza"),
            ("E", "Entre Ríos"),
            ("T", "Tucumán"),
            ("Q", "Neuquén"),
            ("R", "Río Negro"),
            ("V", "Tierra del Fuego")
        ]
        
        print("\n--- Seeding Provincias ---")
        for codigo, nombre in provincias:
            existing = db.query(m_models.Provincia).filter_by(id=codigo).first()
            if not existing:
                db.add(m_models.Provincia(id=codigo, nombre=nombre))
                print(f"Created: {nombre}")
            else:
                print(f"Exists: {nombre}")
        
        db.commit()
        print("\n✅ Seeding Complete.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_maestros()
