
import sys
import os
import uuid
from sqlalchemy import create_engine, text

# Adjust path
sys.path.append(r"c:\dev\Sonido_Liquido_V5")
sys.path.append(r"c:\dev\Sonido_Liquido_V5\backend")

from backend.core.database import SessionLocal
# Assuming model is defined in backend.maestros.models or generic
# We will use raw SQL or SQLAlchemy Core to avoid detailed model imports if possible, 
# but models is safer.
from backend.maestros.models import TipoContacto

def seed_roles():
    db = SessionLocal()
    try:
        current = db.query(TipoContacto).count()
        if current > 0:
            print(f"Roles already exist: {current}")
            return

        roles = [
            "Propietario / Dueño",
            "Cuentas a Pagar / Pagos",
            "Compras / Abastecimiento",
            "Logística / Depósito",
            "Vendedor / Mostrador",
            "Encargado de Local",
            "Administración General",
            "Otro"
        ]
        
        print("Seeding Roles...")
        for r_name in roles:
            # Generate UUID specifically if needed, otherwise default
            # Check model definition for ID type. Usually UUID default.
            new_role = TipoContacto(nombre=r_name)
            db.add(new_role)
        
        db.commit()
        print("Roles seeded successfully.")
        
    except Exception as e:
        print(f"Error seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_roles()
