# backend/scripts/check_phase4.py
import sys
import os

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from core.database import SessionLocal
from backend.clientes import models as client_models
from backend.agenda import models as agenda_models
from backend.maestros import models as maestros_models
from backend.logistica import models as log_models
from backend.auth import models as auth_models

def check_db():
    db = SessionLocal()
    try:
        cliente = db.query(client_models.Cliente).filter_by(cuit="30112233445").first()
        if cliente:
            print(f"✅ Cliente found: {cliente.razon_social}")
            print(f"   - Condicion IVA: {cliente.condicion_iva.nombre if cliente.condicion_iva else 'None'}")
            print(f"   - Lista Precios: {cliente.lista_precios.nombre if cliente.lista_precios else 'None'}")
            
            domicilio = db.query(client_models.Domicilio).filter_by(cliente_id=cliente.id).first()
            if domicilio:
                print(f"✅ Domicilio found: {domicilio.alias}")
                print(f"   - Nodo: {domicilio.transporte_habitual_nodo.nombre_nodo if domicilio.transporte_habitual_nodo else 'None'}")
            else:
                print("❌ Domicilio NOT found")

            vinculo = db.query(agenda_models.VinculoComercial).filter_by(cliente_id=cliente.id).first()
            if vinculo:
                print(f"✅ Vinculo found for: {vinculo.persona.nombre_completo if vinculo.persona else 'None'}")
                print(f"   - Role: {vinculo.tipo_contacto.nombre if vinculo.tipo_contacto else 'None'}")
            else:
                print("❌ Vinculo NOT found")
        else:
            print("❌ Cliente NOT found")

    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    try:
        check_db()
    except Exception as e:
        import traceback
        traceback.print_exc()
