import sys
import os
sys.path.append(os.getcwd())
from backend.core.database import engine, Base
# IMPORTACIONES COMPLETAS
import backend.auth.models
import backend.clientes.models
import backend.productos.models
import backend.proveedores.models
import backend.maestros.models
import backend.pedidos.models  # <--- CRÍTICO
import backend.logistica.models

print("--- REPARANDO SCHEMA ---")
Base.metadata.create_all(bind=engine)
print("--- LISTO ---")
