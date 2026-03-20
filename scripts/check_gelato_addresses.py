
import os
import sys

# Force Local SQLite
project_root = os.path.abspath(os.curdir)
pilot_db_path = os.path.abspath(os.path.join(project_root, "pilot_v5x.db"))
os.environ["DATABASE_URL"] = f"sqlite:///{pilot_db_path}"

sys.path.append(project_root)

from backend.core.database import SessionLocal
from backend.clientes.models import Cliente, Domicilio
from backend.pedidos.models import Pedido # Load registry
from backend.productos.models import Producto # Load registry

def check_gelato():
    db = SessionLocal()
    try:
        c = db.query(Cliente).filter(Cliente.razon_social.ilike('%GELATO%')).first()
        if not c:
            print("GELATO not found.")
            return
        
        print(f"Cliente: {c.razon_social}")
        print(f"Domicilios ({len(c.domicilios)}):")
        for d in c.domicilios:
            print(f"- {d.calle} {d.numero or ''} ({d.localidad}), Fiscal: {d.es_fiscal}, Activo: {d.activo}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_gelato()
