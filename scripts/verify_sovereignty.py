import os
import sys

# Add backend to path
sys.path.append(r"c:\dev\Sonido_Liquido_V5")
os.environ["DATABASE_URL"] = r"sqlite:///c:\dev\Sonido_Liquido_V5\pilot_v5x.db"

from backend.clientes.service import ClienteService
from backend.clientes import schemas
from backend.clientes.models import Cliente
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = r"c:\dev\Sonido_Liquido_V5\pilot_v5x.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
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
        
        print(f"Updated Flags: {flags}")
        print(f"Bit 20 (Yellow) Active: {is_yellow}")
        
        if not is_yellow:
            print("✅ SUCCESS: Bit 20 cleared by Escudo Doble!")
        else:
            print("❌ FAILURE: Bit 20 still active.")
            has_iva = db_cliente.condicion_iva_id is not None
            has_lista = db_cliente.lista_precios_id is not None
            has_segmento = db_cliente.segmento_id is not None
            has_fiscal = any(d.es_fiscal and d.activo for d in db_cliente.domicilios)
            print(f"Pillars Check: IVA={has_iva}, Lista={has_lista}, Seg={has_segmento}, Fiscal={has_fiscal}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_fix()
