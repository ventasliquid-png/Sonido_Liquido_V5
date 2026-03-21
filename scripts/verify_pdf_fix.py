import sys
import os

# Setup paths
sys.path.append(os.getcwd())
os.environ["DATABASE_URL"] = "sqlite:///c:/dev/Sonido_Liquido_V5/pilot_v5x.db"

# FORCE REGISTRATION OF ALL MODELS
import backend.clientes.models
import backend.pedidos.models
import backend.logistica.models
import backend.remitos.models
import backend.contactos.models
import backend.productos.models

from sqlalchemy.orm import configure_mappers
configure_mappers() # This should resolve all string-based relationships

from backend.core.database import SessionLocal
from backend.remitos import models as remito_models
from backend.remitos.router import get_remito_pdf

def test_pdf_fix():
    db = SessionLocal()
    try:
        # Find a manual remito (0015-)
        print("Testing PDF for Manual Remito (0015-)...")
        remito_m = db.query(remito_models.Remito).filter(remito_models.Remito.numero_legal.like("0015-%")).first()
        if not remito_m:
            print("Warning: No manual remito found to test.")
        else:
            try:
                res = get_remito_pdf(str(remito_m.id), db)
                print(f"SUCCESS: Manual PDF generated. Path: {res.path}")
                # CHECK: In manual remitos, qrcode and cae should be suppressed (my code does this)
            except Exception as e:
                print(f"FAILED: Manual PDF crashed: {e}")
                import traceback
                traceback.print_exc()

        # Find an Ingesta remito (0016-)
        print("\nTesting PDF for Ingesta Remito (0016-)...")
        remito_i = db.query(remito_models.Remito).filter(remito_models.Remito.numero_legal.like("0016-%")).first()
        if not remito_i:
            print("Warning: No ingesta remito found to test.")
        else:
            try:
                res = get_remito_pdf(str(remito_i.id), db)
                print(f"SUCCESS: Ingesta PDF generated. Path: {res.path}")
            except Exception as e:
                print(f"FAILED: Ingesta PDF crashed: {e}")
                import traceback
                traceback.print_exc()

        print("\nVerification Complete.")
    finally:
        db.close()

if __name__ == "__main__":
    test_pdf_fix()
