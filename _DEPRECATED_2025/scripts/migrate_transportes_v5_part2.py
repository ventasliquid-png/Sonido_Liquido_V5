import sys
import os

# Agrega el directorio raíz al path para poder importar backend
sys.path.append(os.getcwd())

from sqlalchemy import text
from backend.core.database import engine

def migrate_v5_part2():
    print("🚀 Iniciando migración de Transportes V5 Parte 2 (SYNC Mode)...")
    
    with engine.begin() as conn:
        # 1. Tabla empresas_transporte
        print("Actualizando empresas_transporte...")
        
        # Check and add 'servicio_retiro_domicilio'
        conn.execute(text("ALTER TABLE empresas_transporte ADD COLUMN IF NOT EXISTS servicio_retiro_domicilio BOOLEAN DEFAULT FALSE"))
        
    print("✅ Migración Parte 2 completada con éxito.")

if __name__ == "__main__":
    migrate_v5_part2()
