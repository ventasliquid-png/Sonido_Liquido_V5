from sqlalchemy.orm import Session
from backend.core.database import SessionLocal, GUID
from backend.clientes.models import Cliente, Domicilio
from backend.pedidos.models import Pedido
from backend.auth.models import Usuario, Rol
from backend.maestros.models import CondicionIva, ListaPrecios, Segmento, Vendedor
from backend.productos.models import Producto, Rubro
from backend.agenda.models import Persona, VinculoComercial
from backend.logistica.models import EmpresaTransporte, NodoTransporte
from backend.proveedores.models import Proveedor
import uuid

def clean_clients():
    db = SessionLocal()
    try:
        print("🧼 Iniciando limpieza de clientes...")
        clients = db.query(Cliente).all()
        cleaned_count = 0
        
        for client in clients:
            original_name = client.razon_social
            if original_name and original_name != original_name.strip():
                clean_name = original_name.strip()
                print(f"✨ Limpiando: '{original_name}' -> '{clean_name}'")
                client.razon_social = clean_name
                cleaned_count += 1
        
        if cleaned_count > 0:
            db.commit()
            print(f"✅ Se limpiaron {cleaned_count} nombres de clientes.")
        else:
            print("👍 No se encontraron nombres con espacios innecesarios.")
            
        # Verificación de IDs (GELATO)
        print("\n🔍 Verificando caso Gelato...")
        gelatos = db.query(Cliente).filter(Cliente.razon_social.like("%Gelato%")).all()
        for g in gelatos:
            print(f"ID: {g.id} ({type(g.id)}) | Nombre: '{g.razon_social}' | Activo: {g.activo}")
            
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_clients()
