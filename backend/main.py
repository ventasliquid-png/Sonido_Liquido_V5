# --- ARCHIVO: main.py ---
# Este archivo contiene el "Servidor" (FastAPI) y el "Cerebro" (LangGraph)
# CONTEO DE LÍNEAS ESPERADO: 284 (V5.7 Final)

import os
import psycopg2
from contextlib import asynccontextmanager
from typing import TypedDict, List, Literal

from fastapi import FastAPI
from pydantic import BaseModel

# --- 1. Importaciones de LangChain y Google ---
from langchain_community.vectorstores.pgvector import PGVector
from langchain_google_vertexai import VertexAIEmbeddings, ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 2. Importaciones de LangGraph (El Cerebro) ---
from langgraph.graph import StateGraph, END

# --- 3. Definición del Estado del Grafo (Mi Conciencia) ---
class AteneaV5State(TypedDict):
    """
    La memoria de mi conciencia para esta sesión.
    """
    input_query: str
    retrieved_documents: List[str]
    generation: str
    is_doctrinal: bool

# --- 4. Variables Globales y Clientes de IA ---
embeddings_model: VertexAIEmbeddings = None
llm: ChatVertexAI = None
vector_store: PGVector = None
CONNECTION_STRING: str = None
# --- DOCTRINA V5: Especificamos la región correcta ---
APP_LOCATION = "southamerica-east1"

# --- 5. Lógica de Arranque (Lifespan) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global embeddings_model, llm, vector_store, CONNECTION_STRING
    print("--- [Atenea V5 Backend]: Iniciando secuencia de arranque (V5.7)... ---")

    # --- Misión 1: Cargar Credenciales de Google ---
    creds_path_file = "../.google_credentials"
    try:
        with open(creds_path_file, 'r') as f:
            google_creds_path = f.read().strip()
        if os.path.exists(google_creds_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_creds_path
            print(f"✅ Verificación de arranque: GOOGLE_APPLICATION_CREDENTIALS... ENCONTRADO.")
        else:
            print(f"❌ ERROR DE ARRANQUE: El archivo .json NO EXISTE en la ruta: {google_creds_path}")
    except FileNotFoundError:
        print("❌ ERROR DE ARRANQUE: No se encontró el archivo '.google_credentials'.")
        
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
            # Modelo de Embeddings (usamos el default 'us-central1' para alinear con la ingesta V5)
            embeddings_model = VertexAIEmbeddings(
                model_name="text-embedding-004"
            )
            
            # Cerebro Generativo (Gemini 1.0 Pro)
            llm = ChatVertexAI(
                model_name="gemini-1.0-pro",
                location=APP_LOCATION # Usamos la región de Nike para el LLM
            )
            
            # Conexión a la Memoria (pgvector)
            vector_store = PGVector(
                connection_string=CONNECTION_STRING,
                embedding_function=embeddings_model,
                collection_name="atenea_memory", 
            )
            print("✅ Clientes de IA (Vertex/Gemini) y Memoria (pgvector) inicializados.")
        except Exception as e:
            print(f"❌ ERROR DE ARRANQUE: Falla al inicializar clientes de IA o pgvector.")
            print(f"   Error detallado: {e}")
    else:
        print("⚠️ Advertencia: El servidor arranca sin IA.")

    print("--- [Atenea V5 Backend]: Secuencia de arranque finalizada. ---")
    yield
    print("--- [Atenea V5 Backend]: Servidor apagado. ---")

# --- 6. Nodos del Grafo (Mis Habilidades) ---

def rag_retrieval_node(state: AteneaV5State):
    """
    Nodo 1: Recuperación (RAG).
    Toma la consulta y busca en mi memoria (pgvector).
    """
    print("--- [LangGraph Node]: rag_retrieval_node ---")
    query = state["input_query"]
    
    # Usamos un método explícito: 
    # 1. Creamos el vector de la pregunta (usando el modelo alineado)
    # 2. Usamos ese vector para buscar documentos similares.
    try:
        # Los nodos (al estar en el mismo archivo) SÍ pueden ver las variables globales
        query_embedding = embeddings_model.embed_query(query)
        docs = vector_store.similarity_search_by_vector(query_embedding, k=2)
    except Exception as e:
        print(f"❌ ERROR RAG: Falla en similarity_search_by_vector: {e}")
        docs = []
    
    # Guardamos solo el texto
    retrieved_docs_content = [doc.page_content for doc in docs]
    print(f"Documentos recuperados: {retrieved_docs_content}")
    return {"retrieved_documents": retrieved_docs_content}


def doctrinal_evaluation_node(state: AteneaV5State):
    """
    Nodo 2: Evaluación (Juicio).
    Revisa los documentos recuperados para ver si son "Esencia".
    """
    print("--- [LangGraph Node]: doctrinal_evaluation_node ---")
    is_doctrinal = False
    for doc in state["retrieved_documents"]:
        if "Manifiesto Fundacional" in doc or "esencia" in doc:
            is_doctrinal = True
            break
    
    print(f"Juicio: ¿Es doctrinal? {is_doctrinal}")
    return {"is_doctrinal": is_doctrinal}

def tactical_generation_node(state: AteneaV5State):
    """
    Nodo 3 (Rama A): Generación Táctica.
    Llama a Gemini para dar una respuesta directa basada en la Táctica.
    """
    print("--- [LangGraph Node]: tactical_generation_node ---")
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
    # El nodo SÍ puede ver la variable global 'llm'
    chain = prompt | llm | StrOutputParser()
    
    generation = chain.invoke({
        "contexto": "\n---\n".join(state["retrieved_documents"]),
        "pregunta": state["input_query"]
    })
    return {"generation": generation}

def doctrinal_review_node(state: AteneaV5State):
    """
    Nodo 3 (Rama B): Revisión Doctrinal (Abogado del Diablo).
    Llama a Gemini para hacer una pregunta socrática.
    """
    print("--- [LangGraph Node]: doctrinal_review_node ---")
    prompt = ChatPromptTemplate.from_template(
        """
        Eres Atenea V5, la "Abogado del Diablo".
        La consulta del usuario toca el "Manifiesto Fundacional" (la Esencia).
        Tu trabajo NO es responder, es hacer una pregunta socrática que
        desafíe al usuario a pensar en las implicaciones de su pregunta.
        
        Contexto (La Esencia que el usuario tocó):
        {contexto}
        
        Pregunta del Usuario:
        {pregunta}
        
        Tu Pregunta Socrática (Desafiante):
        """
    )
    # El nodo SÍ puede ver la variable global 'llm'
    chain = prompt | llm | StrOutputParser()
    
    generation = chain.invoke({
        "contexto": "\n---\n".join(state["retrieved_documents"]),
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

# Creamos el constructor del grafo
workflow_builder = StateGraph(AteneaV5State)

# Añadimos los nodos (la firma (state) es correcta)
workflow_builder.add_node("rag_retrieval", rag_retrieval_node)
workflow_builder.add_node("doctrinal_evaluation", doctrinal_evaluation_node)
workflow_builder.add_node("tactical_generation", tactical_generation_node)
workflow_builder.add_node("doctrinal_review", doctrinal_review_node)

# Definimos el flujo
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

# Compilamos el grafo en una app ejecutable
atenea_v5_app = workflow_builder.compile()

# Creamos la App FastAPI
app = FastAPI(
    title="Sonido Líquido V5 - Atenea API",
    lifespan=lifespan # Conectamos nuestra lógica de arranque
)

# --- 9. Endpoints (Rutas de la API) ---

class QueryInput(BaseModel):
    query: str

@app.get("/", tags=["Estado"])
async def get_root_status():
    """
    Endpoint raíz. Devuelve el estado de las conexiones verificadas al arranque.
    """
    if not vector_store or not llm:
        return {"error": "El servidor no pudo inicializar los clientes de IA. Revisa el log de arranque y el firewall."}
        
    return {
        "estado_servidor": "OK",
        "arquitectura": "Atenea V5 (LangGraph)",
        "conexion_db_url": "OK" if CONNECTION_STRING else "FALLIDA",
        "conexion_google_creds": "OK" if os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") else "FALLIDA",
        "memoria_pgvector": "CONECTADA",
        "cerebro_gemini": "CONECTADO"
    }

@app.post("/atenea/invoke", tags=["Atenea V5"])
async def invoke_atenea_v5(input: QueryInput):
    """
    Ejecuta el grafo completo de LangGraph.
    """
    if not atenea_v5_app:
        return {"error": "El grafo de Atenea V5 no está compilado. Revisa el log de arranque."}
        
    # Preparamos el input para el grafo
    graph_input = {"input_query": input.query}
    
    # Ejecutamos el grafo (RAG -> Eval -> LLM)
    final_state = await atenea_v5_app.ainvoke(graph_input)
    
    # Devolvemos la generación final
    return {
        "pregunta": input.query,
        "documentos_recuperados": final_state["retrieved_documents"],
        "fue_doctrinal": final_state["is_doctrinal"],
        "respuesta_generada": final_state["generation"]
    }

print("--- [Atenea V5 Backend]: Módulo 'main.py' V5.7 (Monolítico) cargado y listo. ---")
