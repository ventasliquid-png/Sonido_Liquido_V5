
# Script: fix_client_codes.py
import sys
import os
from sqlalchemy import text

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.database import SessionLocal

def main():
    db = SessionLocal()
    try:
        # Get all clients ordered by creation date (using implicit order if created_at not avail, or name)
        # Assuming created_at might not be reliable or present in model view previously shared, lets use name or just random constant order
        # Actually I saw models.py, it inherits Base, but I don't recall created_at. Let's order by razon_social.
        
        # Check current codes
        result = db.execute(text("SELECT id, razon_social, codigo_interno FROM clientes ORDER BY razon_social"))
        clients = result.fetchall()
        
        print(f"Found {len(clients)} clients.")
        
        # Update loop
        next_code = 1
        updates = []
        
        for client in clients:
            c_id, name, code = client
            if code is None or code == 0:
                print(f"Assigning Code {next_code} to {name}")
                # We simply update. Assuming no conflict for now as there are few.
                db.execute(text("UPDATE clientes SET codigo_interno = :code WHERE id = :id"), {"code": next_code, "id": c_id})
                updates.append(name)
            else:
                print(f"Client {name} already has code {code}")
                # Ensure next_code is higher than any existing
                if code >= next_code:
                    next_code = code 
            
            next_code += 1
            
        db.commit()
        print(f"Updated {len(updates)} clients: {', '.join(updates)}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
