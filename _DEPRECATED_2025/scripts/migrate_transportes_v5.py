import sys
import os

# Agrega el directorio raíz al path para poder importar backend
sys.path.append(os.getcwd())

from sqlalchemy import text
from backend.core.database import engine

def migrate_v5():
    print("🚀 Iniciando migración de Transportes V5 (SYNC Mode)...")
    
    with engine.begin() as conn:
        # 1. Tabla empresas_transporte
        print("Actualizando empresas_transporte...")
        
        # Check and add 'direccion'
        conn.execute(text("ALTER TABLE empresas_transporte ADD COLUMN IF NOT EXISTS direccion VARCHAR"))
        # Check and add 'whatsapp'
        conn.execute(text("ALTER TABLE empresas_transporte ADD COLUMN IF NOT EXISTS whatsapp VARCHAR"))
        # Check and add 'email'
        conn.execute(text("ALTER TABLE empresas_transporte ADD COLUMN IF NOT EXISTS email VARCHAR"))
        # Check and add 'observaciones'
        conn.execute(text("ALTER TABLE empresas_transporte ADD COLUMN IF NOT EXISTS observaciones TEXT"))

        # 2. Tabla nodos_transporte
        print("Actualizando nodos_transporte...")
        
        # Check and add 'localidad'
        conn.execute(text("ALTER TABLE nodos_transporte ADD COLUMN IF NOT EXISTS localidad VARCHAR"))
        # Check and add 'telefono'
        conn.execute(text("ALTER TABLE nodos_transporte ADD COLUMN IF NOT EXISTS telefono VARCHAR"))
        # Check and add 'email'
        conn.execute(text("ALTER TABLE nodos_transporte ADD COLUMN IF NOT EXISTS email VARCHAR"))
        
    print("✅ Migración completada con éxito.")

if __name__ == "__main__":
    migrate_v5()
