import os
import sys

# Add backend to path
sys.path.append(r"c:\dev\Sonido_Liquido_V5")
os.environ["DATABASE_URL"] = r"sqlite:///c:\dev\Sonido_Liquido_V5\pilot_v5x.db"

from backend.clientes.service import ClienteService
from backend.clientes.models import Cliente
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DB_PATH = r"c:\dev\Sonido_Liquido_V5\pilot_v5x.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def migrate_v15_1():
    db = SessionLocal()
    try:
        print("🚀 INICIANDO MIGRACIÓN PAZ BINARIA V15.1...")
        
        # 1. Limpiar significado antiguo del Bit 20 (Inversión)
        # Nota: En V14.8, Bit 20 era "Error". En V15.1 es "Éxito". 
        # Para evitar falsos positivos, lo reseteamos antes de re-auditar.
        print("🧹 Reseteando Bits 19 y 20 (Limpieza de Ley Antigua)...")
        db.execute(text("UPDATE clientes SET flags_estado = flags_estado & ~1572864")) # 1572864 = 524288 + 1048576
        db.commit()
        
        # 2. Re-auditoría masiva
        clientes = db.query(Cliente).all()
        print(f"📋 Re-auditando {len(clientes)} clientes...")
        
        stats = {"19": 0, "20": 0, "hybrid": 0, "yellow": 0}
        
        for c in clientes:
            ClienteService._audit_sovereignty(c)
            
            f = c.flags_estado
            has19 = bool(f & 524288)
            has20 = bool(f & 1048576)
            
            if has19 and has20: stats["hybrid"] += 1
            elif has19: stats["19"] += 1
            elif has20: stats["20"] += 1
            else: stats["yellow"] += 1
            
        db.commit()
        
        print("\n📊 CENSO FINAL V15.1:")
        print(f"🌸 Soberanos Rosas (Solo 19): {stats['19']}")
        print(f"⚪ Soberanos Blancos (Solo 20): {stats['20']}")
        print(f"🧬 Híbridos / Evolucionados (19+20): {stats['hybrid']}")
        print(f"🟡 Pendientes (Amarillo): {stats['yellow']}")
        print("\n✅ MIGRACIÓN COMPLETADA CON ÉXITO. PIN 1974.")

    except Exception as e:
        print(f"❌ ERROR EN MIGRACIÓN: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    from sqlalchemy import text
    migrate_v15_1()
