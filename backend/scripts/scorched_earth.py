# backend/scripts/scorched_earth.py
import sys
import os

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from backend.maestros import models as maestros_models
from backend.logistica import models as log_models
from backend.agenda import models as agenda_models
from backend.clientes import models as client_models
from backend.auth import models as auth_models

def scorched_earth():
    print("🔥 INICIANDO PROTOCOLO TIERRA QUEMADA 🔥")
    
    print("🗑️  Eliminando todas las tablas (DROP SCHEMA CASCADE)...")
    # Base.metadata.drop_all(bind=engine) # Fails with dependencies
    with engine.connect() as connection:
        from sqlalchemy import text
        connection.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO postgres;"))
        connection.commit()
    print("✅ Tablas eliminadas y esquema reiniciado.")

    print("🏗️  Creando nueva estructura de base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Estructura creada.")

    print("🌱 Sembrando datos maestros (Fase 1)...")
    # Run Phase 1 logic inline or call script? Inline is safer for batch.
    db = SessionLocal()
    try:
        # Provincias
        provincias = [
            {"id": "C", "nombre": "Ciudad Autónoma de Buenos Aires"},
            {"id": "B", "nombre": "Buenos Aires"},
            {"id": "X", "nombre": "Córdoba"},
            {"id": "S", "nombre": "Santa Fe"},
            {"id": "M", "nombre": "Mendoza"},
        ]
        for p in provincias:
            db.add(maestros_models.Provincia(**p))
        
        # TipoContacto
        tipos = [
            {"id": "COMPRAS", "nombre": "Responsable de Compras"},
            {"id": "PAGOS", "nombre": "Responsable de Pagos"},
            {"id": "DUEÑO", "nombre": "Dueño / Socio"},
            {"id": "CALIDAD", "nombre": "Control de Calidad"},
        ]
        for t in tipos:
            db.add(maestros_models.TipoContacto(**t))

        # CondicionIva
        condiciones = ["Responsable Inscripto", "Monotributista", "Exento", "Consumidor Final"]
        for c_name in condiciones:
            db.add(maestros_models.CondicionIva(nombre=c_name))

        # ListaPrecios
        listas = ["Lista Mayorista", "Lista Minorista", "Lista Distribuidor"]
        for l_name in listas:
            db.add(maestros_models.ListaPrecios(nombre=l_name))
        
        db.commit()
        print("✅ Fase 1 completada.")

        print("🌱 Sembrando entidades autónomas (Fase 2)...")
        # EmpresaTransporte
        empresas = [
            {"nombre": "Expreso Cruz del Sur", "web_tracking": "https://cruzdelsur.com/tracking", "requiere_carga_web": True},
            {"nombre": "Vía Cargo", "web_tracking": "https://viacargo.com.ar/tracking", "requiere_carga_web": False},
            {"nombre": "Mercado Envíos", "web_tracking": "https://mercadolibre.com.ar", "requiere_carga_web": False},
        ]
        for e in empresas:
            db.add(log_models.EmpresaTransporte(**e))

        # Persona
        personas = [
            {"nombre_completo": "Juan Perez", "email_personal": "juan.perez@gmail.com", "celular_personal": "+5491112345678"},
            {"nombre_completo": "Maria Gonzalez", "email_personal": "maria.gonzalez@hotmail.com", "linkedin": "https://linkedin.com/in/mariagonzalez"},
        ]
        for p in personas:
            db.add(agenda_models.Persona(**p))
        
        db.commit()
        print("✅ Fase 2 completada.")

        print("🌱 Sembrando estructura de soporte (Fase 3)...")
        empresa = db.query(log_models.EmpresaTransporte).filter_by(nombre="Expreso Cruz del Sur").first()
        
        nodos = [
            {
                "nombre_nodo": "Depósito Pompeya",
                "direccion_completa": "Av. Saenz 1234, CABA",
                "provincia_id": "C",
                "empresa_id": empresa.id,
                "es_punto_despacho": True,
                "horario_operativo": "Lunes a Viernes 8-17hs"
            },
            {
                "nombre_nodo": "Sucursal Mendoza",
                "direccion_completa": "San Martin 500, Mendoza",
                "provincia_id": "M",
                "empresa_id": empresa.id,
                "es_punto_retiro": True
            }
        ]
        for n in nodos:
            db.add(log_models.NodoTransporte(**n))
        
        db.commit()
        print("✅ Fase 3 completada.")

        print("🌱 Sembrando núcleo comercial (Fase 4)...")
        cond_iva = db.query(maestros_models.CondicionIva).filter_by(nombre="Responsable Inscripto").first()
        lista_precio = db.query(maestros_models.ListaPrecios).filter_by(nombre="Lista Mayorista").first()
        nodo = db.query(log_models.NodoTransporte).filter_by(nombre_nodo="Depósito Pompeya").first()
        persona = db.query(agenda_models.Persona).filter_by(email_personal="juan.perez@gmail.com").first()
        tipo_contacto = db.query(maestros_models.TipoContacto).filter_by(id="COMPRAS").first()
        provincia = db.query(maestros_models.Provincia).filter_by(id="C").first()

        # Cliente
        cliente = client_models.Cliente(
            razon_social="Cliente Ejemplo S.A.",
            cuit="30112233445",
            condicion_iva_id=cond_iva.id,
            lista_precios_id=lista_precio.id,
            whatsapp_empresa="+5491199887766",
            activo=True
        )
        db.add(cliente)
        db.commit()
        db.refresh(cliente)

        # Domicilio
        domicilio = client_models.Domicilio(
            cliente_id=cliente.id,
            alias="Casa Central",
            calle="Av. Corrientes",
            numero="1234",
            localidad="CABA",
            provincia_id=provincia.id,
            transporte_habitual_nodo_id=nodo.id,
            es_fiscal=True,
            es_entrega=True
        )
        db.add(domicilio)

        # VinculoComercial
        vinculo = agenda_models.VinculoComercial(
            cliente_id=cliente.id,
            persona_id=persona.id,
            tipo_contacto_id=tipo_contacto.id,
            email_laboral="juan.compras@cliente.com",
            es_principal=True
        )
        db.add(vinculo)
        
        db.commit()
        print("✅ Fase 4 completada.")
        print("🚀 PROTOCOLO TIERRA QUEMADA FINALIZADO CON ÉXITO.")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    scorched_earth()
