import os
import sys
import importlib
from datetime import datetime

# 1. FIX: Antes de importar nada del backend, forzamos la ruta de la DB
# para evitar que herede el Postgres del entorno de la shell.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT_DB = os.path.join(BASE_DIR, "pilot_v5x.db") # Target detectado en .env
os.environ["DATABASE_URL"] = f"sqlite:///{PILOT_DB}"

# Añadir el path del backend para importar modelos
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- CARGA DINÁMICA DE MODELOS ---
def import_all_models():
    print(f"   [INFO] Apuntando a: {PILOT_DB}")
    print("   [INFO] Cargando registros Genoma...")
    backend_path = os.path.join(os.getcwd(), "backend")
    for root, dirs, files in os.walk(backend_path):
        if "venv" in root or "node_modules" in root:
            continue
        for file in files:
            if file == "models.py":
                rel_path = os.path.relpath(os.path.join(root, file), os.getcwd())
                module_name = rel_path.replace(os.sep, ".").replace(".py", "")
                try:
                    importlib.import_module(module_name)
                except Exception as e:
                    pass

import_all_models()

from sqlalchemy.orm import configure_mappers
try:
    configure_mappers()
except Exception as e:
    print(f"   [ERR] Error en configure_mappers: {e}")

from backend.clientes.models import Cliente
from backend.pedidos.models import Pedido
from backend.remitos.models import Remito
from backend.clientes.constants import ClientFlags

# Usamos la URL forzada
engine = create_engine(os.environ["DATABASE_URL"])
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def migrate():
    print(f"--- [MIGRACIÓN GENOMA VANGUARD] Iniciando... ---")
    try:
        clientes = db.query(Cliente).all()
    except Exception as e:
        print(f"FATAL: Error al consultar clientes: {e}")
        return

    count = 0
    total = len(clientes)
    print(f"   [INFO] Auditando {total} entidades...")
    
    for c in clientes:
        current_flags = c.flags_estado or 0
        new_flags = current_flags
        
        # 1. Base Vanguard (Existencia + Estructura)
        new_flags |= (ClientFlags.EXISTENCE | ClientFlags.V14_STRUCT)
        
        # 2. Doctrina de Vida (HISTORIA vs VIRGEN)
        has_pedidos = db.query(Pedido).filter(Pedido.cliente_id == c.id).first() is not None
        has_remitos = db.query(Remito).join(Pedido).filter(Pedido.cliente_id == c.id).first() is not None
        
        if has_pedidos or has_remitos:
            new_flags |= ClientFlags.HISTORIA
            new_flags &= ~ClientFlags.VIRGINITY
        else:
            new_flags |= ClientFlags.VIRGINITY
            new_flags &= ~ClientFlags.HISTORIA
            
        # 3. Logística (MULTI_DESTINO)
        active_doms = [d for d in c.domicilios if d.activo]
        if len(active_doms) > 1:
            new_flags |= ClientFlags.MULTI_DESTINO
        else:
            new_flags &= ~ClientFlags.MULTI_DESTINO
            
        # 4. Auditoría (PENDIENTE_REVISION)
        if not c.segmento_id or not c.lista_precios_id:
            new_flags |= ClientFlags.PENDIENTE_REVISION
        else:
            new_flags &= ~ClientFlags.PENDIENTE_REVISION
            
        if new_flags != current_flags:
            c.flags_estado = new_flags
            db.add(c)
            count += 1

    if count > 0:
        db.commit()
        print(f"--- [SÍNCRONIS] Migración exitosa. {count}/{total} mutaciones registradas. ---")
    else:
        print(f"--- [STATUS] ADN persistente. No se requieren cambios en los {total} registros. ---")

if __name__ == "__main__":
    migrate()
