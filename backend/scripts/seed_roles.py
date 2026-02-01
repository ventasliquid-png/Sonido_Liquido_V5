
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from maestros import models

def seed_roles():
    # FORCE LOCAL PILOT DB - BYPASSING ENV VARS
    SQLALCHEMY_DATABASE_URL = "sqlite:///pilot.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Note: TipoContacto model has 'id' and 'nombre' only. No 'activo'.
        roles = [
            {"id": "GERENTE", "nombre": "Gerente / Director"},
            {"id": "COMPRAS", "nombre": "Encargado de Compras"},
            {"id": "PAGOS", "nombre": "Tesorería / Pagos"},
            {"id": "VENDEDOR", "nombre": "Vendedor / Comercial"},
            {"id": "LOGISTICA", "nombre": "Logística / Depósito"},
            {"id": "ADMIN", "nombre": "Administrativo"},
            {"id": "OTRO", "nombre": "Otro"},
        ]

        print("--- Sembrando Roles (Tipos de Contacto) [LOCAL SQLITE] ---")
        for r in roles:
            try:
                exists = db.query(models.TipoContacto).filter(models.TipoContacto.id == r["id"]).first()
                if not exists:
                    print(f"Creando: {r['nombre']}")
                    nuevo = models.TipoContacto(**r)
                    db.add(nuevo)
                else:
                    print(f"Ya existe: {r['nombre']}")
            except Exception as e:
                print(f"Error checking {r['id']}: {e}")
        
        db.commit()
        print("--- Fin de Sembrado ---")

    except Exception as e:
        print(f"Error General: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_roles()
