import sys
import os
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.productos.models import Producto

try:
    print("Connecting to DB...")
    db = SessionLocal()
    print("Querying Productos...")
    p = db.query(Producto).first()
    if p:
        print(f"Success! Found: {p.nombre}")
    else:
        print("Success! Table exists but is empty.")
except Exception as e:
    print("CRITICAL ERROR:")
    import traceback
    traceback.print_exc()
finally:
    print("Done.")
