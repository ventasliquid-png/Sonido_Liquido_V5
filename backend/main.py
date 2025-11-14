import os
import psycopg2
import asyncio 
import json 
from contextlib import asynccontextmanager
from typing import TypedDict, List, Literal

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# --- 1. Importaciones de LangChain y Google ---
from pgvector.psycopg2 import register_vector
from langchain_community.vectorstores.pgvector import PGVector
from langchain_google_vertexai import VertexAIEmbeddings, ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- [Parche V6.1 (Import Fix)] ---
import config 
# --- [FIN PARCHE V6.1] ---

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
    print(f"--- [Atenea V5 Backend]: Iniciando secuencia de arranque (V9.1 - SQL Escape)... ---") # V9.1

    # --- [Parche de Autenticación (ACTIVO)] ---
    creds_path_string = "../.google_credentials"
    try:
        if not os.path.exists(creds_path_string):
            raise FileNotFoundError(f"El archivo '{creds_path_string}' no se encontró en la ruta relativa.")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path_string
        print(f"✅ Verificación de arranque: GOOGLE_APPLICATION_CREDENTIALS... ENCONTRADO.")
    except Exception as e:
        print(f"❌ ERROR DE ARRANQUE: Falla al cargar credenciales: {e}")
    # --- [FIN DEL PARCHE] ---
        
    # --- Misión 2: Cargar URL de la Base de Datos ---
    db_url = os.environ.get("DATABASE_URL")
    if db_url and "postgres" in db_url:
        print("✅ Verificación de arranque: DATABASE_URL... ENCONTRADA.")
        CONNECTION_STRING = db_url
    else:
        print("❌ ERROR DE ARRANQUE: DATABASE_URL no encontrada en el entorno.")

    # --- Misión 3: Inicializar los Clientes de IA y la Memoria ---
    if CONNECTION_STRING and os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        try:
            # 1. Embeddings (Desde config)
            embeddings_model = VertexAIEmbeddings(
                model_name=config.EMBEDDINGS_MODEL_NAME,
                location=config.APP_LOCATION
            )
            
            # 2. Cerebro Generativo (Desde config)
            llm = ChatVertexAI(
                model_name=config.GEMINI_MODEL_NAME,
                location=config.APP_LOCATION,
                temperature=0.7,
                max_output_tokens=2048,
                top_p=0.95
            )
            
            # 3. Conexión a la Memoria (pgvector)
            vector_store = PGVector(
                connection_string=CONNECTION_STRING,
                embedding_function=embeddings_model,
                collection_name="atenea_memory", 
            )
            print(f"✅ Clientes de IA (Región: {config.APP_LOCATION}) y Memoria (pgvector) inicializados.")
            
            atenea_v5_app = workflow_builder.compile()

        except Exception as e:
            print(f"❌ ERROR DE ARRANQUE: Falla al inicializar clientes de IA o pgvector.")
            print(f"    Error detallado: {e}")
    else:
        print("⚠️ Advertencia: El servidor arranca sin IA.")

    print("--- [Atenea V5 Backend]: Secuencia de arranque finalizada. ---")
    yield
    print("--- [Atenea V5 Backend]: Servidor apagado. ---")

# --- 6. Nodos del Grafo (Mis Habilidades) ---

# --- [INICIO PARCHE V9.1 (RAG Filtrado)] ---
async def rag_retrieval_node(state: AteneaV5State):
    """
    Nodo 1: Recuperación TÁCTICA (Intento 1).
    Busca solo documentos marcados como 'tactica_%'.
    """
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
                
                # V9.1: Usamos 'tactica_%%' para escapar el '%' del 'LIKE'
                sql_query = "SELECT content FROM atenea_memory WHERE doc_type LIKE 'tactica_%%' ORDER BY embedding <-> %s::vector LIMIT 2"
                
                vector_string = json.dumps(embedding_vector)
                
                cursor.execute(sql_query, (vector_string,))
                results = cursor.fetchall()
                return [row[0] for row in results]
                
            except Exception as e:
                print(f"❌ ERROR RAG (SQL Táctico): {e}")
                return []
            finally:
                if conn: conn.close()

        retrieved_docs_content = await asyncio.to_thread(sync_sql_search, query_embedding)

    except Exception as e:
        print(f"❌ ERROR RAG (General Táctico): {e}")
        retrieved_docs_content = []
    
    print(f"Documentos recuperados (Táctica): {retrieved_docs_content}")
    return {"retrieved_documents": retrieved_docs_content}

async def doctrinal_evaluation_node(state: AteneaV5State):
    """
    Nodo 2: Evaluación (Juicio) y Recuperación DOCTRINAL (Intento 2).
    """
    print("--- [LangGraph Node]: doctrinal_evaluation_node (V9.1) ---")
    
    # Intento 1 (Táctico) ya se ejecutó.
    if len(state["retrieved_documents"]) > 0:
        # Éxito Táctico
        print("Juicio: TÁCTICA APLICADA (Contexto táctico encontrado).")
        return {"is_doctrinal": False, "retrieved_documents": state["retrieved_documents"]}
    
    # Intento 2 (Doctrinal)
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
                
                # V9.1: Usamos 'doctrina_%%' para escapar el '%' del 'LIKE'
                sql_query = "SELECT content FROM atenea_memory WHERE doc_type LIKE 'doctrina_%%' ORDER BY embedding <-> %s::vector LIMIT 2"
                
                vector_string = json.dumps(embedding_vector)
                
                cursor.execute(sql_query, (vector_string,))
                results = cursor.fetchall()
                return [row[0] for row in results]
                
            except Exception as e:
                print(f"❌ ERROR RAG (SQL Doctrinal): {e}")
                return []
            finally:
                if conn: conn.close()

        retrieved_docs_content = await asyncio.to_thread(sync_sql_search_doctrinal, query_embedding)

    except Exception as e:
        print(f"❌ ERROR RAG (General Doctrinal): {e}")
        retrieved_docs_content = []

    print(f"Documentos recuperados (Doctrina): {retrieved_docs_content}")

    if len(retrieved_docs_content) > 0:
        print("Juicio: JUICIO DOCTRINAL (Contexto doctrinal encontrado).")
        return {"is_doctrinal": True, "retrieved_documents": retrieved_docs_content}
    else:
        print("Juicio: TÁCTICA APLICADA (Sin contexto RAG).")
        return {"is_doctrinal": False, "retrieved_documents": []}
# --- [FIN PARCHE V9.1] ---

def tactical_generation_node(state: AteneaV5State):
    """
    Nodo 3 (Rama A): Generación Táctica.
    """
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
    """
    Nodo 3 (Rama B): Revisión Doctrinal (Abogado del Diablo).
    """
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
    """
    Esta es la bifurcación. Decide qué camino tomar.
    """
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

atenea_v5_app = workflow_builder.compile()

app = FastAPI(
    title="Sonido Líquido V5 - Atenea API",
    lifespan=lifespan
)

# --- [Parche V5.16 (CORS) - ACTIVO] ---
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- [FIN PARCHE V5.16] ---

# --- 9. Endpoints (Rutas de la API) ---

class QueryInput(BaseModel):
    query: str

@app.get("/", tags=["Estado"])
async def get_root_status():
    if not vector_store or not llm:
        return {"error": "El servidor no pudo inicializar los clientes de IA. Revisa el log de arranque y el firewall."}
        
    return {
        "estado_servidor": "OK",
        "arquitectura": "Atenea V9.1 (RAG Filtrado)", # V9.1
        "conexion_db_url": "OK" if CONNECTION_STRING else "FALLIDA",
        "conexion_google_creds": "OK" if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") else "FALLIDA",
        "memoria_pgvector": "CONECTADA",
        "cerebro_gemini": f"{config.GEMINI_MODEL_NAME} (Región: {config.APP_LOCATION})"
    }

@app.post("/atenea/invoke", tags=["Atenea V5"])
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

print("--- [Atenea V5 Backend]: Módulo 'main.py' V9.1 (SQL Escape) cargado y listo. ---") # V9.1