from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.clientes.models import Cliente
from backend.maestros import models as m_models
from backend.pedidos.models import Pedido
# Import other dependencies to ensure mappers are configured
import backend.agenda.models
import backend.auth.models
import backend.logistica.models
import backend.productos.models
import backend.proveedores.models
import uuid

def seed_consumidor_final():
    db = SessionLocal()
    try:
        # Check by CUIT generic
        cuit_cf = "00-00000000-0"
        existing = db.query(Cliente).filter(Cliente.cuit == cuit_cf).first()
        
        if not existing:
            # Debug: List what we have
            all_clients = db.query(Cliente).filter(Cliente.razon_social.like("%CONSUMIDOR%")).all()
            print(f"DEBUG: Clients matching 'CONSUMIDOR': {[c.cuit for c in all_clients]}")
            
            print("Creating CONSUMIDOR FINAL...")
            cf = Cliente(
                razon_social="CONSUMIDOR FINAL",
                cuit=cuit_cf,
                direccion="Retiro en Local",
                telefono="",
                email="",
                activo=True
                # Add other mandatory fields with defaults if necessary
            )
            db.add(cf)
            try:
                db.flush()
                print(f"Flushed. ID: {cf.id}")
                db.commit()
                print("Committed successfully.")
            except Exception as e:
                print(f"ORM Commit failed: {e}")
                db.rollback()
                # Fallback RAW SQL
                print("Attempting RAW SQL Insert...")
                try:
                    query = "INSERT INTO clientes (id, razon_social, cuit, activo, direccion) VALUES (?, ?, ?, ?, ?)"
                    # Generate UUID
                    new_id = str(uuid.uuid4())
                    db.execute(query, (new_id, "CONSUMIDOR FINAL", cuit_cf, 1, "Retiro en Local"))
                    db.commit()
                    print("RAW SQL Insert success.")
                except Exception as e2:
                    print(f"RAW SQL Failed: {e2}")

            # Verify immediately
            check = db.query(Cliente).filter(Cliente.cuit == cuit_cf).first()
            if check:
                print(f"SUCCESS: Found in DB with ID {check.id}")
            else:
                print("ERROR: Not found immediately after commit!")
                
            print("CONSUMIDOR FINAL created successfully.")
        else:
            print("CONSUMIDOR FINAL already exists.")
            
    except Exception as e:
        print(f"Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_consumidor_final()
