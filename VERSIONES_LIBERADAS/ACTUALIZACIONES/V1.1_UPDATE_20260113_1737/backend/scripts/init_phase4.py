# backend/scripts/init_phase4.py
import sys
import os

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from backend.clientes import models as client_models
from backend.maestros import models as maestros_models
from backend.logistica import models as log_models
from backend.agenda import models as agenda_models

def init_db():
    # Create tables
    print("Creating tables for Phase 4...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    db = SessionLocal()
    try:
        # Dependencies
        cond_iva = db.query(maestros_models.CondicionIva).filter_by(nombre="Responsable Inscripto").first()
        lista_precio = db.query(maestros_models.ListaPrecios).filter_by(nombre="Lista Mayorista").first()
        nodo = db.query(log_models.NodoTransporte).filter_by(nombre_nodo="Depósito Pompeya").first()
        persona = db.query(agenda_models.Persona).filter_by(email_personal="juan.perez@gmail.com").first()
        tipo_contacto = db.query(maestros_models.TipoContacto).filter_by(id="COMPRAS").first()
        provincia = db.query(maestros_models.Provincia).filter_by(id="C").first()

        if not all([cond_iva, lista_precio, nodo, persona, tipo_contacto, provincia]):
            print("Missing dependencies. Run Phases 1-3 init first.")
            return

        # Cliente
        cliente_data = {
            "razon_social": "Cliente Ejemplo S.A.",
            "cuit": "30112233445",
            "condicion_iva_id": cond_iva.id,
            "lista_precios_id": lista_precio.id,
            "whatsapp_empresa": "+5491199887766",
            "activo": True
        }
        
        cliente = db.query(client_models.Cliente).filter_by(cuit=cliente_data["cuit"]).first()
        if not cliente:
            cliente = client_models.Cliente(**cliente_data)
            db.add(cliente)
            db.commit() # Commit to get ID
            db.refresh(cliente)
            print(f"Added Cliente: {cliente.razon_social}")
        else:
            print(f"Cliente already exists: {cliente.razon_social}")

        # Domicilio
        domicilio_data = {
            "cliente_id": cliente.id,
            "alias": "Casa Central",
            "calle": "Av. Corrientes",
            "numero": "1234",
            "localidad": "CABA",
            "provincia_id": provincia.id,
            "transporte_habitual_nodo_id": nodo.id,
            "es_fiscal": True,
            "es_entrega": True
        }
        
        existing_dom = db.query(client_models.Domicilio).filter_by(cliente_id=cliente.id, alias=domicilio_data["alias"]).first()
        if not existing_dom:
            db.add(client_models.Domicilio(**domicilio_data))
            print(f"Added Domicilio: {domicilio_data['alias']}")

        # VinculoComercial
        vinculo_data = {
            "cliente_id": cliente.id,
            "persona_id": persona.id,
            "tipo_contacto_id": tipo_contacto.id,
            "email_laboral": "juan.compras@cliente.com",
            "es_principal": True
        }

        existing_vinculo = db.query(agenda_models.VinculoComercial).filter_by(cliente_id=cliente.id, persona_id=persona.id, tipo_contacto_id=tipo_contacto.id).first()
        if not existing_vinculo:
            db.add(agenda_models.VinculoComercial(**vinculo_data))
            print(f"Added VinculoComercial for {persona.nombre_completo}")

        db.commit()
        print("Phase 4 data initialized successfully.")
    except Exception as e:
        print(f"Error initializing Phase 4 data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
