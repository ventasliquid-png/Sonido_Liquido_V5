# scripts/migrate_remitos.py
import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.core.database import engine, Base
from backend.remitos import models
# [FIX] Importar modelos referenciados para que SQLAlchemy los detecte en create_all
import backend.logistica.models
import backend.clientes.models
import backend.pedidos.models

def migrate():
    print("Iniciando migración de tablas REMITOS...")
    try:
        # Create tables defined in models
        # check if tables exist first to avoid error if using create_all ? 
        # create_all is safe, it checks existence.
        print("Creando tablas: remitos, remitos_items ...")
        models.Base.metadata.create_all(bind=engine)
        print("✅ Migración exitosa.")
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")

if __name__ == "__main__":
    migrate()
