
import sys
import os

# Agregamos el root path
sys.path.append(os.getcwd())

from backend.core.database import engine, Base

# IMPORTAMOS TODOS LOS MODELOS PARA QUE ALCHEMY LOS CONOZCA
# (Copiado y ajustado de main.py para asegurar cobertura total)
import backend.auth.models
import backend.proveedores.models
import backend.maestros.models
import backend.productos.models
import backend.clientes.models
import backend.agenda.models
import backend.logistica.models
import backend.pedidos.models
# import backend.data_intel.models
# import backend.cantera.models # Si existe y tiene modelos ORM

def fresh_start():
    print(f"--- [IOWA FRESH START] ---")
    print(f"Target: {engine.url}")
    
    if "postgres" not in str(engine.url) and "104.197.57.226" not in str(engine.url):
        print("PELIGRO: No parece ser la base IOWA. Abortando.")
        print(f"URL detectada: {engine.url}")
        return

    print("⚠️  ATENCIÓN: ESTO ELIMINARÁ TODAS LAS TABLAS EN EL SERVIDOR REMOTO.")
    print("    Operación: DROP ALL -> CREATE ALL")
    
    # Automatización sin pregunta interactiva si se pasa flag, pero por seguridad...
    # Como el usuario ya dio la orden "TIERRA ARRASADA", procedemos.
    
    try:
        print("💥 Ejecutando DROP ALL...")
        Base.metadata.drop_all(bind=engine)
        print("✅ DROP ALL completado.")
        
        print("🏗️  Ejecutando CREATE ALL (Sincronizando Esquema V5)...")
        Base.metadata.create_all(bind=engine)
        print("✅ CREATE ALL completado.")
        
        print("✨ TIERRA ARRASADA: ÉXITO. La base de datos está vacía y con el esquema nuevo.")
        
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")

if __name__ == "__main__":
    fresh_start()
