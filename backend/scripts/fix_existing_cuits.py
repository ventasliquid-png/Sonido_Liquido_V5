import sys
import os

# Add project root to path
# Add project root to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'backend'))

from sqlalchemy.orm import Session
from core.database import SessionLocal
from backend.clientes import models
from backend.auth import models as auth_models
from backend.maestros import models as maestros_models
from backend.logistica import models as logistica_models
from backend.agenda import models as agenda_models
from backend.clientes.models import Cliente

def calculate_verifier(cuit_base):
    """Calculates the verifier digit for the first 10 digits of a CUIT."""
    if len(cuit_base) != 10:
        return None
    
    multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    total = 0
    for i in range(10):
        total += int(cuit_base[i]) * multipliers[i]
    
    rest = total % 11
    digit = 11 - rest
    
    if digit == 11:
        digit = 0
    elif digit == 10:
        digit = 9 
        # Note: Strictly speaking, if result is 10, the prefix should change.
        # But for correction purposes regarding user request "modificar digito", 
        # if logic falls here we might have an issue, but usually 9 is used as fallback in some systems 
        # or implies a prefix change. Let's stick to standard alg logic or flag it.
        # Actually, if the remainder is 1 (11-1=10), the algorithm says "cannot computed", usually gender change required.
        # Let's hope none fall here, or we accept 9 potentially invalid for strict AFIP but valid for some algo implementations.
        return None # Return None to indicate prefix change required
        
    return str(digit)

def fix_cuits():
    db = SessionLocal()
    try:
        clientes = db.query(Cliente).all()
        print(f"Checking {len(clientes)} clients...")
        
        for client in clientes:
            original_cuit = client.cuit
            # Strip non-digits
            clean_cuit = "".join(filter(str.isdigit, original_cuit))
            
            if len(clean_cuit) != 11:
                print(f"⚠️  Client {client.razon_social}: CUIT length invalid ({len(clean_cuit)} digits). Skipping.")
                continue
                
            base = clean_cuit[:10]
            current_digit = clean_cuit[10]
            
            calculated = calculate_verifier(base)
            
            if calculated is None:
                 print(f"⚠️  Client {client.razon_social} ({original_cuit}): Cannot fix by just changing verifier digit (Prefix change required).")
                 continue
                 
            if calculated != current_digit:
                # Reconstruct CUIT preserving format if possible, or standardizing
                # Let's verify format. Usually XX-XXXXXXXX-X
                new_cuit_clean = base + calculated
                
                # Simple format reconstruction
                new_cuit_formatted = f"{new_cuit_clean[:2]}-{new_cuit_clean[2:10]}-{new_cuit_clean[10]}"
                
                print(f"🔧 Fixing {client.razon_social}: {original_cuit} -> {new_cuit_formatted}")
                client.cuit = new_cuit_formatted
                db.add(client)
            else:
                print(f"✅ {client.razon_social}: Valid ({original_cuit})")
        
        db.commit()
        print("Done.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_cuits()
