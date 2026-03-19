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

def final_trigger():
    db = SessionLocal()
    try:
        jofre = db.query(Cliente).filter(Cliente.razon_social.like('%Jofre%')).first()
        if not jofre:
            print("Sergio Jofre not found.")
            return
            
        print(f"Triggering audit for {jofre.razon_social}...")
        # Llama al nuevo método de auditoría centralizado
        ClienteService._audit_sovereignty(jofre)
        db.add(jofre)
        db.commit()
        db.refresh(jofre)
        
        flags = jofre.flags_estado
        is_yellow = bool(flags & (1 << 20))
        print(f"Final Flags: {flags}")
        print(f"Bit 20 Active: {is_yellow}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    final_trigger()
