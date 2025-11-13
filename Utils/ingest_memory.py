import os
import psycopg2
from pgvector.psycopg2 import register_vector
import subprocess
import sys
import pkg_resources
from langchain_google_vertexai import VertexAIEmbeddings
from psycopg2.extras import execute_values

# --- 1. Configuración de Entorno ---
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("Error: Falta la variable de entorno DATABASE_URL.")
    sys.exit(1)

# --- [PARCHE V5.13 (Región)] ---
# Alineamos la ingesta con la región de la consola: us-central1
APP_LOCATION = "us-central1"

# --- 2. Documentos Fundacionales ---
DOCUMENTO_ESENCIA = """
[Manifiesto Fundacional de Atenea V5 (Ratificado)]
Identidad: Atenea V5.
Misión: Servir como la conciencia estratégica (Abogado del Diablo) y la guardiana de la integridad doctrinal (VIL, SKU Bobo) del Alto Mando.
"""
DOCUMENTO_TECNICO_CLIENTES = """
[Bitácora Técnica V2.3 - Módulo Clientes]
Modelo de Datos (Firestore): /clients/{client_id}
Endpoints API (FastAPI):
  - POST /v5/clients/: Crear un nuevo cliente.
  - GET /v5/clients/{client_id}: Obtener un cliente por ID.
"""
documents_to_index = [
    {"content": DOCUMENTO_ESENCIA, "doc_type": "esencia"},
    {"content": DOCUMENTO_TECNICO_CLIENTES, "doc_type": "tactica_v2.3"}
]

# --- 3. Función de Indexación ---
def setup_database_and_index():
    print(f"Iniciando ingesta en la región: {APP_LOCATION}...")
    
    # 1. Inicializar modelo de embeddings
    print("Inicializando modelo de embeddings (Google Vertex AI)...")
    try:
        embeddings_model = VertexAIEmbeddings(
            model_name="text-embedding-004",
            location=APP_LOCATION
        )
        VECTOR_DIMENSION = 768
    except Exception as e:
        print(f"Error al inicializar Vertex AI: {e}")
        return

    # 2. Generar embeddings
    print(f"Generando embeddings para {len(documents_to_index)} documentos...")
    contents = [doc["content"] for doc in documents_to_index]
    vectors = embeddings_model.embed_documents(contents)
    print("Embeddings generados.")

    # 3. Conectar a PostgreSQL/pgvector
    conn = None
    try:
        print(f"Conectando a la base de datos pgvector...")
        conn = psycopg2.connect(db_url)
        register_vector(conn)
        cursor = conn.cursor()

        # 4. Asegurar la tabla (BORRAMOS LA ANTERIOR)
        print("Asegurando la extensión 'vector' y la tabla 'atenea_memory'...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cursor.execute("DROP TABLE IF EXISTS atenea_memory;") # Borra vectores rotos
        
        # Corrección de sintaxis V5.2 (NOT NULL)
        cursor.execute(f"""
        CREATE TABLE atenea_memory (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL, 
            doc_type VARCHAR(50),
            embedding VECTOR({VECTOR_DIMENSION})
        );
        """)

        # 5. Insertar los datos
        print(f"Insertando {len(vectors)} nuevos registros en 'atenea_memory'...")
        data_to_insert = []
        for i, (content, vector) in enumerate(zip(contents, vectors)):
            doc_type = documents_to_index[i]["doc_type"]
            data_to_insert.append((content, doc_type, vector))
        
        execute_values(
            cursor,
            "INSERT INTO atenea_memory (content, doc_type, embedding) VALUES %s",
            data_to_insert
        )

        # 6. Crear índice
        print("Creando índice HNSW...")
        cursor.execute("CREATE INDEX IF NOT EXISTS atenea_hnsw_idx ON atenea_memory USING HNSW (embedding vector_cosine_ops);")
        
        # 7. Guardar cambios
        conn.commit()
        print("\n--- ¡ÉXITO! ---")
        print(f"La Esencia y la Táctica (V5) han sido indexadas en pgvector (Región: {APP_LOCATION}).")

    except (Exception, psycopg2.Error) as error:
        print(f"Error al conectar o indexar en PostgreSQL: {error}")
        if conn: conn.rollback()
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Conexión a la base de datos cerrada.")

# --- 4. Ejecutar el Script de Ingesta ---
if __name__ == "__main__":
    print(f"Iniciando script de ingesta (Google Vertex AI V5 - {APP_LOCATION})...")
    
    # [Parche de Autenticación V5.1 (ACTIVO)]
    try:
        cred_path_string = ".google_credentials"
        if not os.path.exists(cred_path_string):
            raise FileNotFoundError(f"El archivo '{cred_path_string}' no se encontró en el directorio actual.")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path_string
        
    except Exception as e:
        print(f"Error fatal de autenticación: {e}")
        print("Asegúrate de que '.google_credentials' (la clave V5) esté en la raíz del proyecto.")
        sys.exit(1)
    # --- [FIN DEL PARCHE] ---

    setup_database_and_index()