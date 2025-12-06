import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, Base, engine

# Importar TODOS los modelos para asegurar que SQLAlchemy los registre correctamente
from backend.auth.models import Usuario
from backend.maestros.models import Provincia, CondicionIva, ListaPrecios, Segmento
from backend.logistica.models import EmpresaTransporte, NodoTransporte
from backend.agenda.models import VinculoComercial
from backend.clientes.models import Cliente, Domicilio

def fix_missing_fiscal():
    db = SessionLocal()
    try:
        print("🔍 Buscando clientes sin domicilio fiscal...")
        
        # Obtener todos los clientes
        clientes = db.query(Cliente).all()
        fixed_count = 0
        
        # Buscar provincia por defecto (CABA o Buenos Aires)
        provincia = db.query(Provincia).filter(
            (Provincia.nombre.ilike('%CAPITAL%')) | 
            (Provincia.nombre.ilike('%BUENOS AIRES%'))
        ).first()
        
        if not provincia:
            print("⚠️ No se encontró provincia por defecto. Creando 'Provincia Genérica'...")
            # Usar 'X' como código para Desconocida/Genérica, asegurando que sea un solo caracter
            provincia = db.query(Provincia).filter(Provincia.id == 'X').first()
            if not provincia:
                provincia = Provincia(id="X", nombre="PROVINCIA GENERICA")
                db.add(provincia)
                db.commit()
                db.refresh(provincia)

        for cliente in clientes:
            has_fiscal = False
            if cliente.domicilios:
                for d in cliente.domicilios:
                    if d.es_fiscal:
                        has_fiscal = True
                        break
            
            if not has_fiscal:
                print(f"🔧 Arreglando Cliente: {cliente.razon_social} ({cliente.cuit})")
                
                # Crear domicilio fiscal dummy
                dummy_fiscal = Domicilio(
                    cliente_id=cliente.id,
                    calle="CALLE FALSA (Fiscal Faltante)",
                    numero="123",
                    localidad="REVISAR",
                    provincia_id=provincia.id,
                    es_fiscal=True,
                    es_entrega=True,
                    activo=True,
                    alias="DOMICILIO FISCAL",
                    cp="0000"
                )
                db.add(dummy_fiscal)
                fixed_count += 1
        
        if fixed_count > 0:
            db.commit()
            print(f"✅ Se han remediado {fixed_count} clientes.")
        else:
            print("✅ Todos los clientes tienen domicilio fiscal.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_missing_fiscal()
