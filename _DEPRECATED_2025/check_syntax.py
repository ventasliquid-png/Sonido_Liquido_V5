import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("Checking backend.clientes.models...")
    import backend.clientes.models
    print("✅ backend.clientes.models imported.")

    print("Checking backend.clientes.schemas...")
    import backend.clientes.schemas
    print("✅ backend.clientes.schemas imported.")

    print("Checking backend.clientes.service...")
    import backend.clientes.service
    print("✅ backend.clientes.service imported.")

except Exception as e:
    print(f"❌ ERROR IMPORTING MODULES: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
