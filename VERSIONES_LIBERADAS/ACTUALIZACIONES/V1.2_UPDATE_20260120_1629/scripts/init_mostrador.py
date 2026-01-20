
import sys
import os
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.clientes.models import Cliente, Domicilio
from backend.agenda.models import VinculoComercial
from backend.maestros.models import CondicionIva, ListaPrecios, Provincia, Segmento
from backend.core.database import SessionLocal
from backend.clientes.models import Cliente, Domicilio
from backend.agenda.models import VinculoComercial
from backend.maestros.models import CondicionIva, ListaPrecios, Provincia, Segmento
from backend.logistica.models import EmpresaTransporte
from backend.core.database import SessionLocal
from backend.clientes.models import Cliente, Domicilio
from backend.agenda.models import VinculoComercial
from backend.maestros.models import CondicionIva, ListaPrecios, Provincia, Segmento
from backend.logistica.models import EmpresaTransporte
from backend.auth.models import Usuario
from backend.pedidos.models import Pedido
from backend.productos.models import Producto

def init_mostrador():
    db = SessionLocal()
    try:
        # 1. Buscar Condicion IVA Consumidor Final
        cf = db.query(CondicionIva).filter(CondicionIva.nombre.ilike('%Consumidor%')).first()
        if not cf:
            print("⚠️ ADVERTENCIA: No se encontró Condición IVA 'Consumidor Final'. Usando la primera disponible.")
            cf = db.query(CondicionIva).first()
        
        # 2. Buscar Lista Precios Default
        lp = db.query(ListaPrecios).first()

        # 3. Buscar o Crear PROSPECTO
        # Buscamos por CUIT viejo (00-00000000-0) o por nombre "MOSTRADOR" para migrarlo
        mostrador = db.query(Cliente).filter((Cliente.cuit == "00-00000000-0") | (Cliente.razon_social == "MOSTRADOR")).first()
        
        NEW_NAME = "PROSPECTO / PRESUPUESTOS"
        NEW_CUIT = "11-11111111-9"

        if not mostrador:
            print("🔨 Creando cliente PROSPECTO...")
            # Obtener ID para codigo_interno
            from sqlalchemy import func
            max_code = db.query(func.max(Cliente.codigo_interno)).scalar() or 0
            
            mostrador = Cliente(
                razon_social=NEW_NAME,
                cuit=NEW_CUIT,
                condicion_iva_id=cf.id if cf else None,
                lista_precios_id=lp.id if lp else None,
                codigo_interno=max_code + 1,
                es_prospecto=True, # Si existiera el flag
                activo=True
            )
            db.add(mostrador)
            db.commit()
            db.refresh(mostrador)
            print(f"✅ Cliente {NEW_NAME} creado con éxito. ID: {mostrador.id} (Código: {mostrador.codigo_interno})")
        else:
            # Actualizar datos si existen y están viejos
            if mostrador.razon_social != NEW_NAME or mostrador.cuit != NEW_CUIT:
                print(f"🔄 Actualizando cliente existente {mostrador.razon_social} a {NEW_NAME}...")
                mostrador.razon_social = NEW_NAME
                mostrador.cuit = NEW_CUIT
                db.commit()
                print("✅ Cliente actualizado.")
            else:
                print(f"ℹ️ Cliente {NEW_NAME} ya existe y está actualizado. ID: {mostrador.id}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    init_mostrador()
