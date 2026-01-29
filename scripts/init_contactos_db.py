# Script para crear tablas nuevas sin alterar las existentes
import sys
import os

# Agregamos el root path para poder importar backend
sys.path.append(os.getcwd())

from backend.core.database import engine, Base
from backend.contactos.models import Contacto

def create_tables():
    print("🚀 Iniciando creación de tablas nuevas...")
    # Solo crea las tablas que no existen. No migra cambios en tablas existentes.
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas verificadas/creadas con éxito.")

if __name__ == "__main__":
    create_tables()
