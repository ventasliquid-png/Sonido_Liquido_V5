import sys
import os
from sqlalchemy import create_engine, text

# Setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "pilot_v5x.db")

def verify():
    print(f"🧐 Verificando Schema en: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("❌ Error: No existe la DB.")
        return

    engine = create_engine(f"sqlite:///{DB_PATH}")
    with engine.connect() as conn:
        # Check Personas
        print("\n--- Tabla: PERSONAS ---")
        columns = conn.execute(text("PRAGMA table_info(personas)")).fetchall()
        
        found = False
        for col in columns:
            # col format: (cid, name, type, notnull, dflt_value, pk)
            name = col[1]
            type_ = col[2]
            if name == 'flags_estado':
                print(f"✅ FOUND: {name} ({type_})")
                found = True
        
        if not found:
            print("❌ MISSING: flags_estado in personas")
        
        # Check Clientes
        print("\n--- Tabla: CLIENTES ---")
        columns = conn.execute(text("PRAGMA table_info(clientes)")).fetchall()
        found = False
        for col in columns:
            name = col[1]
            if name == 'flags_estado':
                print(f"✅ FOUND: {name}")
                found = True

if __name__ == "__main__":
    verify()
