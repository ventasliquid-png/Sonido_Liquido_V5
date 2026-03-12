
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

# FORCE SQLITE LOCAL
DATABASE_URL = "sqlite:///pilot.db"

# Import Models
import backend.clientes.models # Clientes (Critical for VinculoComercial)
import backend.logistica.models # Logistica (Critical for Domicilio -> NodoTransporte)
import backend.agenda.models # Legacy dependency
import backend.auth.models # Users
import backend.pedidos.models # Orders
import backend.productos.models # Products
from backend.contactos import service, schemas, models

def run_search_test():
    print("🧪 INICIO TEST QA: SEARCH & LINK (BUSQUEDA)")
    
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 1. Búsqueda por Nombre (Pedro)
        print("\n🔍 Buscando por Nombre 'Pedro'...")
        res = service.get_contactos(db, q="Pedro")
        print(f"   Encontrados: {len(res)}")
        for p in res:
            print(f"   - {p.nombre} {p.apellido}")
        
        # 2. Búsqueda por Apellido (Polivalente)
        print("\n🔍 Buscando por Apellido 'Polivalente'...")
        res = service.get_contactos(db, q="Polivalente")
        print(f"   Encontrados: {len(res)}")
        
        # 3. Búsqueda por Email/Teléfono Personal (JSON Search)
        # Asumiendo que Pedro tiene un celular tipo "+54911..."
        print("\n🔍 Buscando por JSON (Celular) '+549'...")
        res = service.get_contactos(db, q="+549")
        print(f"   Encontrados: {len(res)}")
        for p in res:
            print(f"   - {p.nombre} {p.canales_personales}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_search_test()
