import sys
import os

# Agregar directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import engine, Base
from backend.productos import models

def init_db():
    print("--- Inicializando Tablas de Productos ---")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente:")
        print("   - rubros")
        print("   - productos")
        print("   - productos_costos")
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")

if __name__ == "__main__":
    init_db()
