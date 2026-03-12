import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv(override=True)

from langchain_google_vertexai import VertexAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.documents import Document
from backend.core import config

def index_dev_memory():
    print("--- [Dev Memory]: Iniciando indexación de bitácora... ---")
    
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
            print(f"🔑 Cargando credenciales desde {creds_path}")
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
        else:
            print("❌ ERROR: No se encontraron credenciales de Google (.google_credentials).")
            return

    embeddings = VertexAIEmbeddings(
        model_name=config.EMBEDDINGS_MODEL_NAME,
        location=config.APP_LOCATION
    )

    # 2. Leer archivos
    files_to_index = ["BITACORA_DEV.md", "MEMORIA_SESIONES.md"]
    documents = []

    for filename in files_to_index:
        if os.path.exists(filename):
            print(f"📄 Leyendo {filename}...")
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()
                # Simple chunking by lines for now, or whole file if small
                # Better: Chunk by headers? Let's keep it simple: chunks of 1000 chars
                chunk_size = 2000
                chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
                
                for i, chunk in enumerate(chunks):
                    doc = Document(
                        page_content=chunk,
                        metadata={"source": filename, "chunk": i}
                    )
                    documents.append(doc)
        else:
            print(f"⚠️ Archivo {filename} no encontrado.")

    if not documents:
        print("⚠️ No hay documentos para indexar.")
        return

    # 3. Indexar en PGVector
    print(f"🧠 Indexando {len(documents)} fragmentos en 'dev_memory_embeddings'...")
    
    # PGVector creates the table if it doesn't exist
    PGVector.from_documents(
        embedding=embeddings,
        documents=documents,
        collection_name="dev_memory_embeddings",
        connection_string=connection_string,
        pre_delete_collection=True # Re-index fresh every time for now
    )
    
    print("✅ Indexación completada exitosamente.")

if __name__ == "__main__":
    index_dev_memory()
