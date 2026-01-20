import sys
import os
from dotenv import dotenv_values

# FORCE LOAD backend/.env
# We do this BEFORE importing backend.core.database because that module reads os.environ at import time.
env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
config = dotenv_values(env_path)

if "DATABASE_URL" in config:
    print(f"🔌 OVERRIDING DATABASE_URL from {env_path}")
    os.environ["DATABASE_URL"] = config["DATABASE_URL"]
if "DB_PASSWORD" in config:
    os.environ["DB_PASSWORD"] = config["DB_PASSWORD"]

# Ensure backend modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.core.database import engine, Base
from backend.maestros.models import *
from backend.clientes.models import *
from backend.productos.models import *
from backend.pedidos.models import *
from backend.agenda.models import *
from backend.logistica.models import *
from backend.auth.models import *
from backend.proveedores.models import *

def init_db():
    print("🚀 INICIANDO CREACIÓN DE ESQUEMA EN IOWA...")
    print(f"🎯 Target URL: {os.environ.get('DATABASE_URL').split('@')[-1]}") # Log host/port only for safety
    
    print("📋 Tablas en Metadata:", list(Base.metadata.tables.keys()))
    
    try:
        # Drop all tables first (Clean Slate)
        print("🔥 Dropping all tables (Metadata)...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("🔨 Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente.")
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")

if __name__ == "__main__":
    init_db()
