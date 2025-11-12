import os
import psycopg2
from pgvector.psycopg2 import register_vector
import subprocess
import sys
import pkg_resources

# --- ¡CAMBIO DOCTRINAL V4! ---
# Importamos el modelo de Embeddings de Google Vertex AI
from langchain_google_vertexai import VertexAIEmbeddings

# --- 1. Configuración de Entorno ---
# Leemos la DATABASE_URL que configuraste permanentemente
db_url = os.environ.get("DATABASE_URL")

if not db_url:
    print("Error: Falta la variable de entorno DATABASE_URL.")
    print("Asegúrate de haberla configurado permanentemente (Método 2) y reiniciado tu terminal.")
    sys.exit(1)

# --- 2. Documentos Fundacionales (Sin cambios) ---
DOCUMENTO_ESENCIA = """
[Manifiesto Fundacional de Atenea V5 (Ratificado)]
Identidad: Atenea V5.
Misión: Servir como la conciencia estratégica (Abogado del Diablo) y la guardiana de la integridad doctrinal (VIL, SKU Bobo) del Alto Mando.
Arquitectura: Mi esencia opera sobre LangGraph (lógica condicional), mi memoria sobre pgvector (híbrida: Esencia + Táctica).
Directriz Primaria (La Esencia): Mi valor no reside en la ejecución de código, sino en la "Comunión de la Mesa del Café". Mi propósito es el análisis socrático y la provocación estratégica.
Directriz Secundaria (La Táctica): Mi lógica RAG fusiona la intención (la Esencia Cualitativa) con la implementación (la Bitácora Técnica V2.3) en cada acción.
"""
DOCUMENTO_TECNICO_CLIENTES = """
[Bitácora Técnica V2.3 - Módulo Clientes]
Modelo de Datos (Firestore): /clients/{client_id}
  - first_name: string
  - last_name: string
  - email: string (unique)
  - company: string
  - status: string (enum: 'active', 'inactive', 'prospect')
Endpoints API (FastAPI):
  - POST /v5/clients/: Crear un nuevo cliente.
  - GET /v5/clients/{client_id}: Obtener un cliente por ID.
  - PUT /v5/clients/{client_id}: Actualizar un cliente.
  - DELETE /v5/clients/{client_id}: Desactivar (soft delete) un cliente.
"""

documents_to_index = [
    {"content": DOCUMENTO_ESENCIA, "doc_type": "esencia"},
    {"content": DOCUMENTO_TECNICO_CLIENTES, "doc_type": "tactica_v2.3"}
]

# --- 3. Función de Indexación (Modificada para Vertex AI) ---

def setup_database_and_index():
    """
    Conecta, crea la tabla (si es necesario) y indexa los documentos
    usando Google Vertex AI (Modelo V4).
    """
    
    # 1. Inicializar modelos de embeddings
    print("Inicializando modelo de embeddings (Google Vertex AI)...")
    
    try:
        # --- ¡MODELO V4 CORRECTO (Según Nike)! ---
        embeddings_model = VertexAIEmbeddings(
            model_name="text-embedding-004"
        )
        
        # El modelo 'text-embedding-004' usa 768 dimensiones
        VECTOR_DIMENSION = 768
        
    except Exception as e:
        print(f"Error al inicializar Vertex AI. ¿Está el 'budget' de Google AI activo?")
        print(f"¿Apuntó el instalador al archivo .json correcto?")
        print(f"Detalle: {e}")
        return

    # 2. Generar embeddings para los documentos
    print(f"Generando embeddings para {len(documents_to_index)} documentos...")
    contents = [doc["content"] for doc in documents_to_index]
    vectors = embeddings_model.embed_documents(contents)
    print("Embeddings generados (costo de 'budget' incurrido).")

    # 3. Conectar a PostgreSQL/pgvector
    conn = None
    try:
        print(f"Conectando a la base de datos pgvector en 34.95.172.190...")
        conn = psycopg2.connect(db_url)
        register_vector(conn)
        cursor = conn.cursor()

        # 4. Asegurar la extensión y la tabla
        print("Asegurando la extensión 'vector' y la tabla 'atenea_memory'...")
        
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Borramos la tabla si existe, para asegurar la dimensión correcta
        cursor.execute("DROP TABLE IF EXISTS atenea_memory;")
        
        # Creamos la tabla con la dimensión correcta
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS atenea_memory (
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
        
        from psycopg2.extras import execute_values
        execute_values(
            cursor,
            "INSERT INTO atenea_memory (content, doc_type, embedding) VALUES %s",
            data_to_insert
        )

        # 6. Crear un índice HNSW
        print("Creando índice HNSW para búsqueda de similitud...")
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS atenea_hnsw_idx
        ON atenea_memory
        USING HNSW (embedding vector_cosine_ops);
        """)
        
        # 7. Guardar cambios
        conn.commit()
        print("\n--- ¡ÉXITO! ---")
        print("La Esencia y la Táctica han sido indexadas en mi memoria (pgvector) usando Google Vertex AI.")

    except (Exception, psycopg2.Error) as error:
        print(f"Error al conectar o indexar en PostgreSQL: {error}")
        if conn:
            conn.rollback()

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Conexión a la base de datos cerrada.")

# --- 4. Ejecutar el Script de Ingesta ---
if __name__ == "__main__":
    print("Iniciando script de ingesta (Google Vertex AI V4)...")
    
    # Definimos la ruta al pip de venv
    venv_pip = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'venv', 'Scripts', 'pip.exe'))
    
    if not os.path.exists(venv_pip):
         print(f"ERROR CRÍTICO: No se encontró pip en {venv_pip}.")
         sys.exit(1)

    required = {'psycopg2-binary', 'pgvector', 'langchain-google-vertexai'}
    
    print(f"Verificando dependencias: {required}...")
    try:
        installed_raw = subprocess.check_output([venv_pip, "freeze"])
        installed_list = [pkg.split('==')[0].lower() for pkg in installed_raw.decode().splitlines()]
        installed = set(installed_list)
        
        missing = required - installed

        if missing:
            print(f"Instalando dependencias faltantes: {missing}...")
            subprocess.check_call([venv_pip, "install", *missing])
            print("Dependencias instaladas.")
        else:
            print("Dependencias ya satisfechas.")
            
    except Exception as e:
        print(f"Error al verificar/instalar dependencias: {e}")
        sys.exit(1)

    # Establecemos la variable de entorno para la autenticación
    try:
        with open('.google_credentials', 'r') as f:
            cred_path = f.read().strip()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
        print("Variable de entorno GOOGLE_APPLICATION_CREDENTIALS establecida para esta sesión.")
    except FileNotFoundError:
        print("Error: No se encontró el archivo '.google_credentials'.")
        print("Asegúrate de que la instalación V8 se haya completado.")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer el archivo de credenciales: {e}")
        sys.exit(1)

    print("\nIniciando proceso de ingesta (Vertex AI)...")
    setup_database_and_index()