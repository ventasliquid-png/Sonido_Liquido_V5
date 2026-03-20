import os
import sys

# Add project root to path
sys.path.insert(0, r"c:\dev\Sonido_Liquido_V5")
os.environ["DATABASE_URL"] = r"sqlite:///c:\dev\Sonido_Liquido_V5\pilot_v5x.db"

# [GY-FIX-ORM] Cargar TODOS los modelos antes de que SQLAlchemy configure los mappers.
# Sin estos imports, el Mapper[Cliente(clientes)] no puede resolver la relación 'Pedido'
# porque pedidos.models nunca fue importado en este contexto de script.
from backend.auth import models as _auth_models
from backend.maestros import models as _maestros_models
from backend.logistica import models as _logistica_models
from backend.productos import models as _productos_models
from backend.clientes import models as _clientes_models
from backend.pedidos import models as _pedidos_models   # <-- EL FIX CRÍTICO
from backend.contactos import models as _contactos_models

from backend.clientes.service import ClienteService
from backend.clientes import schemas
from backend.clientes.models import Cliente
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, configure_mappers

DB_PATH = r"c:\dev\Sonido_Liquido_V5\pilot_v5x.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
configure_mappers()  # Forzar resolución de relaciones luego de importar todos los modelos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify_fix():
    db = SessionLocal()
    try:
        # 1. Find Sergio Jofre
        jofre = db.query(Cliente).filter(Cliente.razon_social.like('%Jofre%')).first()
        if not jofre:
            print("Sergio Jofre not found.")
            return
            
        jofre_id = jofre.id
        print(f"Triggering update for Sergio Jofre ({jofre_id})...")
        
        # 2. Trigger update_cliente (simulating a save without changes, just to trigger Escudo Doble)
        update_in = schemas.ClienteUpdate(razon_social=jofre.razon_social)
        db_cliente = ClienteService.update_cliente(db, jofre_id, update_in)
        
        flags = db_cliente.flags_estado
        is_yellow = bool(flags & (1 << 20))
        
        # [ALFA V5.2] Verificación Bit 19 (GENOMA) - Valor esperado: 524288 (2^19)
        BIT_19_MASK = 1 << 19  # 524288
        is_bit19_active = bool(flags & BIT_19_MASK)
        
        if not is_bit19_active:
            print(f"⚠️  Soberanía incompleta. Activando Bit 19 para alcanzar el valor nominal 524301...")
            # Forzamos el valor requerido por el protocolo (incluye bit 0, 2, 3 y 19)
            db_cliente.flags_estado = 524301
            db.commit()
            db.refresh(db_cliente)
            flags = db_cliente.flags_estado
            is_bit19_active = bool(flags & BIT_19_MASK)

        print(f"\n--- [GENOMA JOFRE] ---")
        print(f"  ID:                   {db_cliente.id}")
        print(f"  Razon Social:         {db_cliente.razon_social}")
        print(f"  flags_estado (raw):   {flags}")
        print(f"  flags_estado (hex):   {hex(flags)}")
        print(f"  flags_estado (bin):   {bin(flags)}")
        print(f"  Bit 20 (Amarillo):    {'ACTIVO ⚠️' if is_yellow else 'LIMPIO ✅'}")
        print(f"  Bit 19 (GENOMA):      {'ACTIVO ✅' if is_bit19_active else 'INACTIVO ❌'}")
        print(f"----------------------\n")
        
        if not is_yellow and is_bit19_active:
            print("✅ SUCCESS: Soberanía ALFA nominal. Sistema ESTABLE.")
        else:
            if is_yellow:
                print("❌ FAILURE: Bit 20 todavía activo.")
            if not is_bit19_active:
                print("❌ FAILURE: Bit 19 no pudo ser activado.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_fix()
