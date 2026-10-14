"""
Servidor Principal FastAPI (V10.12 - Arquitectura Modular Estable)
"""
import os
from contextlib import asynccontextmanager

# --- [BOOT STRATEGY V11] ---
# Forzar carga de entorno desde el Root del proyecto para evitar errores de contexto.
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # backend/
ROOT_DIR = os.path.dirname(BASE_DIR) # root/
ENV_PATH = os.path.join(ROOT_DIR, ".env")

print(f"--- [BOOT] Cargando variables de entorno desde: {ENV_PATH} ---")
load_dotenv(ENV_PATH, override=True)

# [V5.9 AUDIT] Log the active Database path for the user
db_url = os.environ.get("DATABASE_URL", "NOT_FOUND")
print(f"--- [DATABASE AUDIT]: {db_url} ---")

# [GY-FIX-BOOT] Enforcement of Local SQLite removed. Pulling from .env.
    
# ACTIVATE AI (Vertex AI) - V14.0 Handshake Ready
new_creds_path = os.path.abspath(os.path.join(ROOT_DIR, "Clave-Jason.jason", "sistema-liquid-sound-e6aefd316f1d.json"))
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = new_creds_path
os.environ["ENABLE_AI"] = "True"
print(f"--- [BOOT] Google Credentials: {new_creds_path} ---")

# backend/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Added for SPA
from fastapi.responses import FileResponse # Added for SPA

# --- [INICIO REFACTOR V10.10] ---
# Importaciones modulares (absolutas - sin puntos relativos)
# Compatible con: uvicorn backend.main:app (desde raíz) o uvicorn main:app (desde backend/)
import sys
import os

# Agregar directorio backend al path para imports absolutos
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# [GY-FIX-BOOT] Agregar directorio RAÍZ (Padre) para permitir 'import backend.x'
# Esto es crítico para evitar duplicidad de módulos (sys.modules['auth'] vs sys.modules['backend.auth'])
# y para que los 65+ archivos restantes funcionen sin cambios masivos.
parent_dir = os.path.dirname(backend_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
# --- [FIN REFACTOR V10.10] ---

# Imports Core y Mapeo Universal (Crítico para SQLAlchemy)
from backend.core import config
from backend.core.database import engine, Base

# [V14.12 GOLD] Mapeo Universal (Crítico para SQLAlchemy)
# El orden aquí es vital para resolver dependencias circulares.
import backend.auth.models as auth_models
import backend.maestros.models as maestros_models
import backend.logistica.models as logistica_models
import backend.contactos.models as contactos_models
import backend.clientes.models as clientes_models
import backend.productos.models as productos_models
import backend.pedidos.models as pedidos_models
import backend.proveedores.models as proveedores_models
import backend.agenda.models as agenda_models
import backend.remitos.models as remitos_models
import backend.facturacion.models as facturacion_models
import backend.ingesta.models as ingesta_models
import backend.core.models as core_models

# [FIX RACE CONDITION V14.12] 
# Forzamos la configuración de mappers inmediatamente después de cargar los modelos.
from sqlalchemy.orm import configure_mappers as _configure_mappers
print("--- [V14.12]: Ejecutando Mapeo Universal de SQLAlchemy... ---")
try:
    _configure_mappers()
    print("--- [OK] Mapeo Universal Finalizado. ---")
except Exception as e:
    print(f"--- [X] ERROR CRÍTICO DE MAPEO: {e} ---")
    import traceback
    traceback.print_exc()

# Imports de Routers
from backend.auth.router import router as auth_router
from backend.maestros.router import router as maestros_router
from backend.clientes.router import router as clientes_router
from backend.logistica.router import router as logistica_router
from backend.agenda.router import router as agenda_router
from backend.agenda.google_mock_router import router as google_mock_router 
from backend.productos.router import router as productos_router
from backend.proveedores.router import router as proveedores_router
from backend.data_intel.router import router as data_intel_router
from backend.pedidos.router import router as pedidos_router 
from backend.cantera.router import router as cantera_router
from backend.remitos.router import router as remitos_router
from backend.informes.router import router as informes_router
from backend.contactos.router import router as contactos_router
from backend.stats.router import router as stats_router
from backend.facturacion.router import router as facturacion_router
from backend.ingesta.router import router as ingesta_router
from backend.sistema.router import router as sistema_router

# --- 5. Lógica de Arranque (Lifespan) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"--- [Atenea V5 Backend]: Iniciando secuencia de arranque (V10.12 Modular)... ---")

    # --- [INICIO PARCHE V10.1 (ORM)] ---
    try:
        # Nota: configure_mappers ya se llamó a nivel de módulo, 
        # aquí lo llamamos de nuevo preventivamente por si hubo carga diferida.
        from sqlalchemy.orm import configure_mappers
        configure_mappers() 
        print("--- [V10.12]: Sincronizando modelos ORM (SQLAlchemy)... ---")
        Base.metadata.create_all(bind=engine)
        print("--- [V10.12]: Tablas ORM sincronizadas. ---")
    except Exception as e:
        print(f"[X] ERROR DE ARRANQUE V10: Falla al sincronizar tablas ORM: {e}")
        import traceback
        traceback.print_exc()
    # --- [FIN PARCHE V10.1] ---

    # --- [PROTOCOLO DE SIEMBRA AUTOMÁTICA] ---
    try:
        from backend.core.seed import seed_all
        print("--- [Atenea V5 Seed]: Protocolo de Siembra Automática activado... ---")
        seed_all()
    except Exception as e:
        print(f"[X] [SEED ERROR]: Falla crítica en siembra automática: {e}")
    # -----------------------------------------

    # --- [CANTERA TÁCTICA]: Sincronización JSON Mirror -> Cantera.db ---
    try:
        from backend.cantera.service import CanteraService
        print("--- [IPL V6.1]: Sincronizando Cantera.db (JSON Mirror)... ---")
        CanteraService.sync_from_json()
    except Exception as e:
        print(f"[X] [CANTERA ERROR]: Falla en sincronización de cantera: {e}")
    # ------------------------------------------------------------------

    # --- [RULE 4/6 SEGURO]: Session Counter & Backup ---
    try:
        from backend.tools.backup_system import SessionCounter
        triggered, count = SessionCounter.check_and_increment()
        print(f"--- [SESIÓN #{count}]: Contador verificado. Backup disparado: {triggered} ---")
    except Exception as e:
        print(f"[X] [BACKUP ERROR]: Falla en lógica de sesión 4/6: {e}")
        # ---------------------------------------------------

    print("--- [Atenea V5 Backend]: Secuencia de arranque finalizada. ---")
    yield
    print("--- [Atenea V5 Backend]: Servidor apagado. ---")

app = FastAPI(
    title="Sonido Líquido V5 - Atenea API",
    lifespan=lifespan
)


# --- 2. CORS Config (V11.5 - Permissive Debug Mode) ---
# [GY-FIX] Allow ALL origins to prevent local dev blocking
origins = ["*"]
# origins = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
#     "http://localhost:8000",
#     "http://10.0.0.11:5173" # LAN Dev
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Estado"])
async def get_root_status():
    return {
        "estado_servidor": "OK",
        "arquitectura": "Atenea V10.12 (DEBUG-FASE-4-FINAL)",
    }

# --- 3. Endpoints y Routers ---

# Inclusiones (Ordenadas)
app.include_router(auth_router)
app.include_router(maestros_router)
app.include_router(clientes_router)
app.include_router(logistica_router)
app.include_router(agenda_router) 
app.include_router(productos_router)
app.include_router(proveedores_router) 
app.include_router(data_intel_router)
app.include_router(pedidos_router) 
app.include_router(cantera_router)
app.include_router(remitos_router) # [GY-V7] PDF Ingestion
app.include_router(informes_router) # [S875] Módulo Informes
app.include_router(google_mock_router) # [GY-V14] Mock Sync
app.include_router(stats_router)
app.include_router(contactos_router)
app.include_router(facturacion_router)
app.include_router(ingesta_router)
app.include_router(sistema_router)

# --- [SPA / STATIC FILES SUPPORT] ---
# Sirve los archivos estáticos compilados de Vue (JS, CSS, Img)
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
if os.path.exists(static_dir):
    print(f"--- [SPA] Montando archivos estáticos desde: {static_dir} ---")
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    # app.mount("/static", StaticFiles(directory=static_dir), name="static") # Generic Mount if needed

# Catch-all para Vue Router (HTML5 History Mode)
# Cualquier ruta que no sea API (ver api_prefixes) devuelve index.html
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    # Ignorar rutas de API (ya manejadas arriba por include_router)
    # Ignorar rutas de API (ya manejadas arriba por include_router)
    api_prefixes = ["api", "docs", "openapi", "clientes", "pedidos", "productos", "maestros", "logistica", "agenda", "proveedores", "auth", "bypass", "contactos", "stats", "remitos", "facturacion", "sistema", "ingesta"]
    # Check if the path (normalized) starts with any API prefix
    clean_path = full_path.strip("/")
    if any(clean_path.startswith(prefix) for prefix in api_prefixes):
         from fastapi import HTTPException
         # Si llegamos aquí es porque ningún router de arriba capturó la petición
         raise HTTPException(status_code=404, detail=f"API Endpoint '{full_path}' not found")

    # [P24 S879] index.html referencia los bundles por nombre con hash (/assets/index-XXXX.js): si el navegador
    # lo guarda en cache despues de un deploy sigue pidiendo el bundle viejo y el operador ve la pantalla
    # anterior (le paso a Tomy el 02/10: Ctrl+Mayus+R). `no-cache` NO impide guardarlo: obliga a revalidar
    # con el servidor en cada carga; index.html pesa ~1 KB, asi que reenviarlo entero no cuesta nada.
    headers_spa = {"Cache-Control": "no-cache"}

    # Si existe archivo físico (ej: favicon.ico), servirlo
    posible_archivo = os.path.join(static_dir, full_path)
    if os.path.exists(posible_archivo) and os.path.isfile(posible_archivo):
        es_index = os.path.basename(posible_archivo).lower() == "index.html"
        return FileResponse(posible_archivo, headers=headers_spa if es_index else None)

    # Si no, servir index.html (SPA)
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, headers=headers_spa)
    
    return {"error": "SPA no compilada. Ejecute 'npm run build' y copie a 'static'."}
# ------------------------------------

# --- 9. Endpoints (Rutas de la API) ---
# --- Bypass Endpoint for Rubro Dependencies ---
from backend.productos import models as prod_models
from backend.core.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException

@app.get("/bypass/check_rubro_deps", tags=["Bypass"])
def check_rubro_dependencies_bypass(rubro_id: int, db: Session = Depends(get_db)):
    print(f"DEBUG: Checking dependencies for Rubro {rubro_id} in MAIN BYPASS")
    try:
        rubro = db.query(prod_models.Rubro).get(rubro_id)
        if not rubro:
            raise HTTPException(status_code=404, detail="Rubro no encontrado")
            
        hijos = db.query(prod_models.Rubro).filter(prod_models.Rubro.padre_id == rubro_id, prod_models.Rubro.activo == True).all()
        
        hijos_data = [{
            "id": h.id, 
            "nombre": h.nombre, 
            "codigo": h.codigo,
            "activo": h.activo
        } for h in hijos]

        productos = db.query(prod_models.Producto).filter(prod_models.Producto.rubro_id == rubro_id, prod_models.Producto.activo == True).all()

        productos_data = [{
            "id": p.id,
            "nombre": p.nombre,
            "rubro_id": p.rubro_id,
            "activo": p.activo
        } for p in productos]

        return {
            "rubros_hijos": hijos_data,
            "productos": productos_data,
            "cantidad_hijos": len(hijos),
            "cantidad_productos": len(productos)
        }
    except Exception as e:
        print(f"ERROR IN BYPASS: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# ----------------------------------------------


print("--- [Atenea V5 Backend]: Módulo 'main.py' V10.16 (Modular Estable) cargado y listo. ---")
# Reload trigger for V5.1 schema update



if __name__ == "__main__":
    import uvicorn
    # [GY-LAN-FIX] Binding to 0.0.0.0 to allow LAN access and bypass localhost IPv4/v6 issues
    # [GY-STABILITY] Disable reload only in production entry point to prevent double-loading
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)
