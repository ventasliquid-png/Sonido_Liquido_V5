import sys
import os

# Ajustar PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from backend.core.database import Base, DATABASE_URL
from backend.agenda.models import VinculoComercial, Persona
from backend.maestros.models import TipoContacto
from backend.clientes.models import Cliente # Necesario para FK

def fix_missing_tables():
    print(f"🔧 Reparando tablas en: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    # Crear tablas específicas del módulo Agenda si faltan
    try:
        VinculoComercial.__table__.create(bind=engine, checkfirst=True)
        Persona.__table__.create(bind=engine, checkfirst=True)
        TipoContacto.__table__.create(bind=engine, checkfirst=True)
        print("✅ Tablas de Agenda (VinculoComercial) verificadas/creadas.")
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")

if __name__ == "__main__":
    fix_missing_tables()
