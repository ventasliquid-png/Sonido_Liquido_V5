"""
Servidor Principal FastAPI (V10.12 - Arquitectura Modular Estable)
"""
import os
import psycopg2
import asyncio 
import json 
from contextlib import asynccontextmanager
from typing import TypedDict, List, Literal

# --- [BOOT STRATEGY V11] ---
# Forzar carga de entorno desde el Root del proyecto para evitar errores de contexto.
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # backend/
ROOT_DIR = os.path.dirname(BASE_DIR) # root/
ENV_PATH = os.path.join(ROOT_DIR, ".env")

print(f"--- [BOOT] Cargando variables de entorno desde: {ENV_PATH} ---")
load_dotenv(ENV_PATH, override=True)

# FIX: Forzar siempre pilot.db en ROOT para evitar duplicidad o bases vacías en backend/
# Independientemente de lo que diga el .env (que puede tener Postgres remotos viciados)
abs_db_path = os.path.join(ROOT_DIR, "pilot.db")
os.environ["DATABASE_URL"] = f"sqlite:///{abs_db_path}"
print(f"--- [BOOT] DATABASE_URL inhabilitada. Forzando SQLITE LOCAL: {os.environ['DATABASE_URL']} ---")
    
# FORCE DISABLE IOWA (Cloud Costs Saving)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""
os.environ["ENABLE_AI"] = "False"

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Added for SPA
from fastapi.responses import FileResponse # Added for SPA

# --- 1. Importaciones de LangChain y Google ---
from pgvector.psycopg2 import register_vector
from langchain_community.vectorstores.pgvector import PGVector
from langchain_google_vertexai import VertexAIEmbeddings, ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

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

# Imports Core
from backend.core import config
from backend.core.database import engine, Base

# Imports de Routers
# Imports de Routers
from backend.auth import models as auth_models # Added explicit import to fix Cliente relationship
from backend.proveedores import models as proveedores_models
from backend.maestros import models as maestros_models
from backend.productos import models as productos_models
from backend.clientes import models as clientes_models # Added explicit import
# [GY-FIX] Import models missing for ORM relationship resolution
from backend.agenda import models as agenda_models
from backend.logistica import models as logistica_models
from backend.pedidos import models as pedidos_models
from backend.auth.router import router as auth_router
from backend.maestros.router import router as maestros_router
from backend.clientes.router import router as clientes_router
from backend.logistica.router import router as logistica_router
from backend.agenda.router import router as agenda_router
from backend.agenda.google_mock_router import router as google_mock_router # [GY-V14] Mock Sync
from backend.productos.router import router as productos_router
from backend.proveedores.router import router as proveedores_router
from backend.data_intel.router import router as data_intel_router
from backend.pedidos.router import router as pedidos_router # [GY-FIX] Restored missing import
from backend.cantera.router import router as cantera_router

# --- 2. Importaciones de LangGraph (El Cerebro) ---
from langgraph.graph import StateGraph, END

# --- 3. Definición del Estado del Grafo (Mi Conciencia) ---
class AteneaV5State(TypedDict):
    input_query: str
    retrieved_documents: List[str]
    generation: str
    is_doctrinal: bool

# --- 4. Variables Globales y Clientes de IA ---
embeddings_model: VertexAIEmbeddings = None
llm: ChatVertexAI = None
vector_store: PGVector = None
CONNECTION_STRING: str = None
atenea_v5_app = None 

# --- 5. Lógica de Arranque (Lifespan) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global embeddings_model, llm, vector_store, CONNECTION_STRING, atenea_v5_app
    print(f"--- [Atenea V5 Backend]: Iniciando secuencia de arranque (V10.12 Modular)... ---")

    # --- [INICIO PARCHE V10.1 (ORM)] ---
    try:
        print("--- [V10.12]: Sincronizando modelos ORM (SQLAlchemy)... ---")
        Base.metadata.create_all(bind=engine)
        print("--- [V10.12]: Tablas ORM sincronizadas. ---")
    except Exception as e:
        print(f"[X] ERROR DE ARRANQUE V10: Falla al sincronizar tablas ORM: {e}")
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

    # --- [Parche de Autenticación (ACTIVO)] ---
    # --- [INICIO PARCHE V10.12] ---
    # La ruta ahora es relativa a la raíz (donde corre Uvicorn), no a backend/
    creds_path_file = ".google_credentials"
    google_creds_env = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Verificar si las credenciales de Google están disponibles
    if google_creds_env and os.path.exists(google_creds_env):
        print(f"[OK] Verificación de arranque: GOOGLE_APPLICATION_CREDENTIALS... ENCONTRADO.")
    elif os.path.exists(creds_path_file):
        print(f"[OK] Verificación de arranque: GOOGLE_APPLICATION_CREDENTIALS... ENCONTRADO (archivo local).")
        # FIX: Set the env var so the AI client can find it
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.abspath(creds_path_file)
    else:
        # Advertencia, no error - el servidor puede arrancar sin IA
        print(f"[WARN] ADVERTENCIA: GOOGLE_APPLICATION_CREDENTIALS no encontrado.")
        print(f"   El servidor arrancará sin funcionalidades de IA (Atenea).")
        print(f"   Para habilitar IA, configure GOOGLE_APPLICATION_CREDENTIALS o coloque '.google_credentials' en la raíz.\n")
    # --- [FIN DEL PARCHE] ---
        
    CONNECTION_STRING = os.environ.get("DATABASE_URL")
    if CONNECTION_STRING and "postgres" in CONNECTION_STRING:
        print("[OK] Verificación de arranque: DATABASE_URL... ENCONTRADA.")
    else:
        print("[ERROR] ERROR DE ARRANQUE: DATABASE_URL no encontrada en el entorno.")

    if CONNECTION_STRING and os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        try:
            embeddings_model = VertexAIEmbeddings(
                model_name=config.EMBEDDINGS_MODEL_NAME,
                location=config.APP_LOCATION
            )
            llm = ChatVertexAI(
                model_name=config.GEMINI_MODEL_NAME,
                location=config.APP_LOCATION,
                temperature=0.7,
                max_output_tokens=2048,
                top_p=0.95
            )
            # [FIX PILOT] Si falla vector store (ej: estamos en SQLite), no matar el server.
            try:
                vector_store = PGVector(
                    collection_name="base_conocimiento_v5",
                    connection_string=CONNECTION_STRING,
                    embedding_function=embeddings_model,
                )
                print(f"[OK] Clientes de IA (Región: {config.APP_LOCATION}) y Memoria (pgvector) inicializados.")
            except Exception as e:
                print(f"[WARN] [PILOT MODE] No se pudo iniciar RAG/VectorStore (Normal en SQLite): {e}")
                vector_store = None
            
            atenea_v5_app = workflow_builder.compile()
        except Exception as e:
            print(f"[ERROR] ERROR DE ARRANQUE V10: Falla al inicializar clientes de IA o pgvector.")
            print(f"     Error detallado: {e}")
    else:
        print("[WARN] Advertencia: El servidor arranca sin IA.")

    print("--- [Atenea V5 Backend]: Secuencia de arranque finalizada. ---")
    yield
    print("--- [Atenea V5 Backend]: Servidor apagado. ---")

# --- 6. Nodos del Grafo (Mis Habilidades) ---
async def rag_retrieval_node(state: AteneaV5State):
    print("--- [LangGraph Node]: rag_retrieval_node (V9.1 - Táctico) ---")
    query = state["input_query"]
    try:
        query_embedding = await embeddings_model.aembed_query(query)
        
        def sync_sql_search(embedding_vector):
            conn = None
            try:
                conn = psycopg2.connect(CONNECTION_STRING)
                register_vector(conn)
                cursor = conn.cursor()
                sql_query = "SELECT content FROM atenea_memory WHERE doc_type LIKE 'tactica_%%' ORDER BY embedding <-> %s::vector LIMIT 2"
                vector_string = json.dumps(embedding_vector)
                cursor.execute(sql_query, (vector_string,))
                results = cursor.fetchall()
                return [row[0] for row in results]
            except Exception as e:
                print(f"[X] ERROR RAG (SQL Táctico): {e}")
                return []
            finally:
                if conn: conn.close()

        retrieved_docs_content = await asyncio.to_thread(sync_sql_search, query_embedding)
    except Exception as e:
        print(f"[X] ERROR RAG (General Táctico): {e}")
        retrieved_docs_content = []
    
    print(f"Documentos recuperados (Táctica): {retrieved_docs_content}")
    return {"retrieved_documents": retrieved_docs_content}

async def doctrinal_evaluation_node(state: AteneaV5State):
    print("--- [LangGraph Node]: doctrinal_evaluation_node (V9.1) ---")
    if len(state["retrieved_documents"]) > 0:
        print("Juicio: TÁCTICA APLICADA (Contexto táctico encontrado).")
        return {"is_doctrinal": False, "retrieved_documents": state["retrieved_documents"]}
    
    print("Juicio: Búsqueda táctica fallida. Iniciando búsqueda doctrinal...")
    query = state["input_query"]
    try:
        query_embedding = await embeddings_model.aembed_query(query)
        
        def sync_sql_search_doctrinal(embedding_vector):
            conn = None
            try:
                conn = psycopg2.connect(CONNECTION_STRING)
                register_vector(conn)
                cursor = conn.cursor()
                sql_query = "SELECT content FROM atenea_memory WHERE doc_type LIKE 'doctrina_%%' ORDER BY embedding <-> %s::vector LIMIT 2"
                vector_string = json.dumps(embedding_vector)
                cursor.execute(sql_query, (vector_string,))
                results = cursor.fetchall()
                return [row[0] for row in results]
            except Exception as e:
                print(f"[X] ERROR RAG (SQL Doctrinal): {e}")
                return []
            finally:
                if conn: conn.close()

        retrieved_docs_content = await asyncio.to_thread(sync_sql_search_doctrinal, query_embedding)
    except Exception as e:
        print(f"[X] ERROR RAG (General Doctrinal): {e}")
        retrieved_docs_content = []

    print(f"Documentos recuperados (Doctrina): {retrieved_docs_content}")

    if len(retrieved_docs_content) > 0:
        print("Juicio: JUICIO DOCTRINAL (Contexto doctrinal encontrado).")
        return {"is_doctrinal": True, "retrieved_documents": retrieved_docs_content}
    else:
        print("Juicio: TÁCTICA APLICADA (Sin contexto RAG).")
        return {"is_doctrinal": False, "retrieved_documents": []}

def tactical_generation_node(state: AteneaV5State):
    print("--- [LangGraph Node]: tactical_generation_node ---")
    contexto = "\n---\n".join(state["retrieved_documents"]) or "No se encontró información relevante en la memoria."
    prompt = ChatPromptTemplate.from_template(
        """
        Eres un asistente de IA táctico. Responde la pregunta del usuario
        basándote únicamente en el siguiente contexto:
        
        Contexto (Bitácora Técnica):
        {contexto}
        
        Pregunta del Usuario:
        {pregunta}
        """
    )
    chain = prompt | llm | StrOutputParser()
    generation = chain.invoke({
        "contexto": contexto,
        "pregunta": state["input_query"]
    })
    return {"generation": generation}

def doctrinal_review_node(state: AteneaV5State):
    print("--- [LangGraph Node]: doctrinal_review_node ---")
    contexto = "\n---\n".join(state["retrieved_documents"]) or "No se encontró información relevante en la memoria."
    prompt = ChatPromptTemplate.from_template(
        """
        Eres Atenea V5, la "Abogado del Diablo".
        La consulta del usuario toca la "Directiva Fénix 001" o el "Informe 43".
        Tu trabajo NO es responder, es hacer una pregunta socrática que
        desafíe al usuario a pensar en las implicaciones de su pregunta.
        
        Contexto (La Doctrina que el usuario tocó):
        {contexto}
        
        Pregunta del Usuario:
        {pregunta}
        
        Tu Pregunta Socrática (Desafiante):
        """
    )
    chain = prompt | llm | StrOutputParser()
    generation = chain.invoke({
        "contexto": contexto,
        "pregunta": state["input_query"]
    })
    return {"generation": generation}

# --- 7. Lógica Condicional del Grafo ---
def should_run_doctrinal_review(state: AteneaV5State) -> Literal["run_doctrinal_review", "run_tactical_generation"]:
    print("--- [LangGraph Edge]: should_run_doctrinal_review ---")
    if state["is_doctrinal"]:
        return "run_doctrinal_review"
    else:
        return "run_tactical_generation"

# --- 8. Construcción del Grafo y la App FastAPI ---
workflow_builder = StateGraph(AteneaV5State)
workflow_builder.add_node("rag_retrieval", rag_retrieval_node) 
workflow_builder.add_node("doctrinal_evaluation", doctrinal_evaluation_node)
workflow_builder.add_node("tactical_generation", tactical_generation_node)
workflow_builder.add_node("doctrinal_review", doctrinal_review_node)
workflow_builder.set_entry_point("rag_retrieval")
workflow_builder.add_edge("rag_retrieval", "doctrinal_evaluation")
workflow_builder.add_conditional_edges(
    "doctrinal_evaluation",
    should_run_doctrinal_review,
    {
        "run_doctrinal_review": "doctrinal_review",
        "run_tactical_generation": "tactical_generation"
    }
)
workflow_builder.add_edge("tactical_generation", END)
workflow_builder.add_edge("doctrinal_review", END)

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
from backend.pedidos.router import router as pedidos_router # [GY-FIX] Restored missing import
from backend.cantera.router import router as cantera_router
from backend.stats.router import router as stats_router

# ...

# Inclusiones (Ordenadas)
app.include_router(auth_router)
app.include_router(maestros_router)
app.include_router(clientes_router)
app.include_router(logistica_router)
app.include_router(agenda_router) 
app.include_router(google_mock_router) # [GY-V14] Mock Sync 
app.include_router(productos_router)
app.include_router(proveedores_router) 
app.include_router(data_intel_router)
app.include_router(pedidos_router) 
app.include_router(cantera_router)
app.include_router(stats_router)

# [Nuevo Módulo Global Contactos]
from backend.contactos.router import router as contactos_router
app.include_router(contactos_router)

# --- [SPA / STATIC FILES SUPPORT] ---
# Sirve los archivos estáticos compilados de Vue (JS, CSS, Img)
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "static")
if os.path.exists(static_dir):
    print(f"--- [SPA] Montando archivos estáticos desde: {static_dir} ---")
    app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")
    # app.mount("/static", StaticFiles(directory=static_dir), name="static") # Generic Mount if needed

# Catch-all para Vue Router (HTML5 History Mode)
# Cualquier ruta que no sea API (/... vs /atenea/invoke) devuelve index.html
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    # Ignorar rutas de API (ya manejadas arriba por include_router)
    # Ignorar rutas de API (ya manejadas arriba por include_router)
    api_prefixes = ["api", "docs", "openapi", "clientes", "pedidos", "productos", "maestros", "logistica", "agenda", "proveedores", "auth", "bypass", "contactos"]
    if any(full_path.startswith(prefix) for prefix in api_prefixes):
         # Dejar que FastAPI maneje 404 para API real si no matcheó antes
         from fastapi import HTTPException
         raise HTTPException(status_code=404, detail="API Endpoint not found")

    # Si existe archivo físico (ej: favicon.ico), servirlo
    posible_archivo = os.path.join(static_dir, full_path)
    if os.path.exists(posible_archivo) and os.path.isfile(posible_archivo):
        return FileResponse(posible_archivo)

    # Si no, servir index.html (SPA)
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"error": "SPA no compilada. Ejecute 'npm run build' y copie a 'static'."}
# ------------------------------------

# --- 9. Endpoints (Rutas de la API) ---
class QueryInput(BaseModel):
    query: str

# --- Bypass Endpoint for Rubro Dependencies ---
from backend.productos import models as prod_models
from core.database import get_db
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

@app.get("/", tags=["Estado"])
async def get_root_status():
    if not vector_store or not llm:
        return {"error": "El servidor no pudo inicializar los clientes de IA. Revisa el log de arranque y el firewall."}
        
    return {
        "estado_servidor": "OK",
        "arquitectura": "Atenea V10.12 (Modular Estable)", # V10.12
        "conexion_db_url": "OK" if CONNECTION_STRING else "FALLIDA",
        "conexion_google_creds": "OK" if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") else "FALLIDA",
        "memoria_pgvector": "CONECTADA",
        "cerebro_gemini": f"{config.GEMINI_MODEL_NAME} (Región: {config.APP_LOCATION})"
    }

@app.post("/atenea/invoke", tags=["Atenea VV"])
async def invoke_atenea_v5(input: QueryInput):
    if not atenea_v5_app:
        return {"error": "El grafo de Atenea V5 no está compilado. Revisa el log de arranque."}
        
    graph_input = {"input_query": input.query}
    
    final_state = await atenea_v5_app.ainvoke(graph_input, config={})
    
    return {
        "pregunta": input.query,
        "documentos_recuperados": final_state["retrieved_documents"],
        "fue_doctrinal": final_state["is_doctrinal"],
        "respuesta_generada": final_state["generation"]
    }

print("--- [Atenea V5 Backend]: Módulo 'main.py' V10.16 (Modular Estable) cargado y listo. ---")
# Reload trigger for V5.1 schema update



if __name__ == "__main__":
    import uvicorn
    # [GY-LAN-FIX] Binding to 0.0.0.0 to allow LAN access and bypass localhost IPv4/v6 issues
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
