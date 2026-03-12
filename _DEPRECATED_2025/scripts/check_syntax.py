import sys
import os

# Add root to path
sys.path.append(os.getcwd())

try:
    print("Attempting to import backend.pedidos.router...")
    from backend.pedidos import router
    print("Import router success.")

    print("Attempting to import backend.pedidos.models...")
    from backend.pedidos import models
    print("Import models success.")

    print("Attempting to import backend.pedidos.schemas...")
    from backend.pedidos import schemas
    print("Import schemas success.")
    
    print("Attempting to import backend.main...")
    from backend import main
    print("Import main success. Syntax looks good.")

except Exception as e:
    print(f"SYNTAX/IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
