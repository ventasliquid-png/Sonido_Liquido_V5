
import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 1. Force Local DB
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # scripts/
ROOT_DIR = os.path.dirname(BASE_DIR) # root/
pilot_db_path = os.path.join(ROOT_DIR, "pilot.db")
DATABASE_URL = f"sqlite:///{pilot_db_path}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def inspect_client():
    print(f"--- INSPECTING CLIENTS ON {DATABASE_URL} ---")
    
    # Try to find "Cliente2" or listing recent/all
    query_clients = text("SELECT id, razon_social, activo FROM clientes WHERE razon_social LIKE '%Cliente%' OR razon_social LIKE '%2%' LIMIT 10")
    
    with engine.connect() as conn:
        clients = conn.execute(query_clients).fetchall()
        
        if not clients:
            print("No clients found matching 'Cliente' or '2'. Listing top 5 active:")
            clients = conn.execute(text("SELECT id, razon_social, activo FROM clientes WHERE activo = true LIMIT 5")).fetchall()
            
        for c in clients:
            print(f"\nCLIENT: {c.razon_social} (ID: {c.id}) [Active: {c.activo}]")
            
            # Fetch Domicilios
            doms = conn.execute(text(f"SELECT * FROM domicilios WHERE cliente_id = '{c.id}'")).fetchall()
            print(f"  Total Domicilios: {len(doms)}")
            for d in doms:
                print(f"    - ID: {d.id}")
                print(f"      Calle: {d.calle} {d.numero}")
                print(f"      Fiscal: {d.es_fiscal} | Entrega: {d.es_entrega}")
                print(f"      Activo: {d.activo}")

if __name__ == "__main__":
    inspect_client()
