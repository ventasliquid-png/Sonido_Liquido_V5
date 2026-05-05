import sys
import os

# Add V5-LS current backend to path
sys.path.append(r'c:\dev\V5-LS\current')

try:
    from backend.productos import models, schemas
    from backend.core.database import SessionLocal
    
    db = SessionLocal()
    
    # Try to instantiate a Rubro with flags_estado (this should fail if model is not updated)
    try:
        new_rubro = models.Rubro(
            codigo="TST",
            nombre="TEST RUBRO " + os.environ.get("COMPUTERNAME", ""),
            flags_estado=0
        )
        print("Model instantiation: SUCCESS")
        
        # Test if it can be added to session
        db.add(new_rubro)
        print("Session add: SUCCESS")
        
        # Rollback so we don't pollute the DB
        db.rollback()
        print("Test completed successfully (Rollback applied)")
        
    except TypeError as e:
        print(f"Model instantiation: FAILED - {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
        
except Exception as e:
    print(f"Import Error: {e}")
