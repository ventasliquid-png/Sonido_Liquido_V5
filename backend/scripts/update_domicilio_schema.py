
from sqlalchemy import text
from backend.core.database import SessionLocal, engine

def update_schema():
    print("Updating Domicilio schema...")
    try:
        with engine.connect() as connection:
            # Metodo Entrega
            print("Adding metodo_entrega...")
            connection.execute(text("ALTER TABLE domicilios ADD COLUMN IF NOT EXISTS metodo_entrega VARCHAR;"))
            
            # Modalidad Envio
            print("Adding modalidad_envio...")
            connection.execute(text("ALTER TABLE domicilios ADD COLUMN IF NOT EXISTS modalidad_envio VARCHAR;"))
            
            # Origen Logistico
            print("Adding origen_logistico...")
            connection.execute(text("ALTER TABLE domicilios ADD COLUMN IF NOT EXISTS origen_logistico VARCHAR;"))
            
            connection.commit()
            print("Schema updated successfully!")
    except Exception as e:
        print(f"Error updating schema: {e}")

if __name__ == "__main__":
    update_schema()
