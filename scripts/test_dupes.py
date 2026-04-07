
import sys
import os
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.clientes.service import ClienteService
from backend.clientes.models import Cliente
from backend.clientes import schemas
from backend.logistica.models import EmpresaTransporte, NodoTransporte
from backend.auth.models import Usuario, Rol

# Setup DB
DATABASE_URL = "sqlite:///./pilot_v5x.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_normalization():
    print("--- [TEST] Normalización de Nombres ---")
    cases = [
        ("Inapryl S.R.L.", "INAPRYLSRL"),
        ("Inapryl S. R.L.", "INAPRYLSRL"),
        ("  INAPRYL S.R.L.  ", "INAPRYLSRL"),
        ("Lácteos de Poblet", "LACTEOSDEPOBLET")
    ]
    
    success = True
    for original, expected in cases:
        result = ClienteService.normalize_name(original)
        if result == expected:
            print(f"  [OK] '{original}' -> '{result}'")
        else:
            print(f"  [FAIL] '{original}' -> '{result}' (Esperado: '{expected}')")
            success = False
    return success

def test_duplication_shield():
    print("\n--- [TEST] Escudo de Duplicados ---")
    db = SessionLocal()
    try:
        # Check if Inapryl exists or create it temporarily
        name1 = "Inapryl S.R.L."
        name2 = "Inapryl S. R. L."
        
        existing = db.query(Cliente).filter(Cliente.razon_social == name1).first()
        if not existing:
            print(f"[*] Creando cliente base: {name1}")
            # Mock create
            c_base = Cliente(razon_social=name1, activo=True, flags_estado=8205)
            db.add(c_base)
            db.commit()
        else:
            print(f"[*] Cliente base ya existe: {existing.razon_social}")

        # Try to create duplicate
        print(f"[*] Intentando crear duplicado semántico: {name2}")
        schema_in = schemas.ClienteCreate(
            razon_social=name2,
            cuit="30123456789", # Different CUIT to bypass CUIT check
            condicion_iva_id=None,
            lista_precios_id=None,
            segmento_id=None,
            domicilios=[],
            vinculos=[]
        )
        
        try:
            ClienteService.create_cliente(db, schema_in)
            print("  [FAIL] Se permitió la creación del duplicado.")
        except Exception as e:
            if "BLOQUEO DE DUPLICADO" in str(e):
                print(f"  [OK] Bloqueo exitoso: {e.detail}")
            else:
                print(f"  [ERROR] Error inesperado: {e}")

    finally:
        db.rollback() # Don't persist test data
        db.close()

if __name__ == "__main__":
    if test_normalization():
        test_duplication_shield()
