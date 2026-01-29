
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from backend.core.database import DATABASE_URL
from backend.contactos.models import Contacto
from backend.clientes.models import Cliente
from backend.logistica.models import EmpresaTransporte

def diagnose():
    if not DATABASE_URL:
        print("DATABASE_URL not found")
        return

    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        count = session.query(Contacto).count()
        print(f"Total Contactos: {count}")

        if count > 0:
            print("\n--- Muestra de los primeros 10 contactos ---")
            contactos = session.query(Contacto).limit(10).all()
            for c in contactos:
                print(f"ID: {c.id} | Nombre: '{c.nombre}' | Apellido: '{c.apellido}' | ClienteID: {c.cliente_id} | TransporteID: {c.transporte_id}")
        
            print("\n--- Conteo de vacíos ---")
            empty_names = session.query(Contacto).filter(Contacto.nombre == "").count()
            null_names = session.query(Contacto).filter(Contacto.nombre == None).count()
            print(f"Nombres vacíos ('string'): {empty_names}")
            print(f"Nombres nulos (None): {null_names}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    diagnose()
