import sys
import os
import uuid
from sqlalchemy import text

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from core.database import engine

def seed_transporte_virtual():
    print("--- [SEED] Seeding Virtual Transport ---")
    
    # UUID fijo para "RETIRO EN LOCAL" (ID 1 virtual)
    # Usamos un UUID que termine en 1 para fácil identificación: 00000000-0000-0000-0000-000000000001
    VIRTUAL_ID = "00000000-0000-0000-0000-000000000001"
    NOMBRE = "RETIRO EN LOCAL"
    
    with engine.connect() as connection:
        trans = connection.begin()
        try:
            # Check if exists
            result = connection.execute(text("SELECT id FROM empresas_transporte WHERE id = :id"), {"id": VIRTUAL_ID}).fetchone()
            
            if result:
                print(f"   -> Transport '{NOMBRE}' already exists (ID: {VIRTUAL_ID}).")
            else:
                print(f"   -> Creating '{NOMBRE}'...")
                connection.execute(text("""
                    INSERT INTO empresas_transporte (id, nombre, activo, requiere_carga_web, formato_etiqueta)
                    VALUES (:id, :nombre, TRUE, FALSE, 'PROPIA')
                """), {"id": VIRTUAL_ID, "nombre": NOMBRE})
                trans.commit()
                print("   -> Created successfully.")
                
        except Exception as e:
            trans.rollback()
            print("   -> Error seeding transport:", e)

    print("--- [SEED] Completed ---")

if __name__ == "__main__":
    seed_transporte_virtual()
