import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from langchain_google_vertexai import VertexAIEmbeddings, ChatVertexAI
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from backend.core import config

def query_dev_memory(query: str):
    print(f"--- [Dev Memory]: Consultando: '{query}' ---")
    
    # 1. Configuración
    from backend.core.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL
    connection_string = SQLALCHEMY_DATABASE_URL
    
    if not connection_string:
        print("❌ ERROR: DATABASE_URL no encontrada.")
        return

    # Load credentials explicitly if not in env
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        creds_path = os.path.join(os.getcwd(), ".google_credentials")
        if os.path.exists(creds_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        else:
            print("❌ ERROR: No se encontraron credenciales de Google.")
            return

    embeddings = VertexAIEmbeddings(
        model_name=config.EMBEDDINGS_MODEL_NAME,
        location=config.APP_LOCATION
    )

    vector_store = PGVector(
        embedding_function=embeddings,
        collection_name="dev_memory_embeddings",
        connection_string=connection_string
    )

    # 2. Búsqueda Vectorial
    print("🔍 Buscando contexto relevante...")
    docs = vector_store.similarity_search(query, k=3)
    
    if not docs:
        print("⚠️ No se encontró información relevante.")
        return

    context = "\n\n".join([d.page_content for d in docs])
    print(f"📄 Contexto recuperado ({len(docs)} fragmentos).")

    # 3. Generación con LLM
    llm = ChatVertexAI(
        model_name=config.GEMINI_MODEL_NAME,
        location=config.APP_LOCATION,
        temperature=0.3
    )

    template = """
    Eres un asistente de memoria para un proyecto de desarrollo de software.
    Usa el siguiente contexto recuperado de la bitácora del proyecto para responder la pregunta del desarrollador.
    Si no encuentras la respuesta en el contexto, dilo claramente.

    Contexto:
    {context}

    Pregunta: {question}

    Respuesta Concisa:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()

    print("🤖 Generando respuesta...")
    response = chain.invoke({"context": context, "question": query})
    
    print("\n" + "="*50)
    print(response)
    print("="*50 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        query_dev_memory(query)
    else:
        print("Uso: python scripts/query_dev_memory.py 'Tu pregunta aquí'")
