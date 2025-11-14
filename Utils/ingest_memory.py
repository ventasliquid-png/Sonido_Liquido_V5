import os
import psycopg2
from pgvector.psycopg2 import register_vector
import subprocess
import sys
import pkg_resources
from langchain_google_vertexai import VertexAIEmbeddings
from psycopg2.extras import execute_values

# --- [INICIO PARCHE V6.1 (Import Fix)] ---
# Añadimos la carpeta 'backend' a la ruta de Python para encontrar 'config'
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(script_dir, '..', 'backend'))
sys.path.append(os.path.dirname(backend_dir)) # Añade la raíz del proyecto (C:\dev\...)

try:
    from backend import config
except ImportError as e:
    print(f"Error: No se pudo importar 'backend.config'. Detalle: {e}")
    print(f"Asegúrate de que 'backend/config.py' exista.")
    sys.exit(1)
# --- [FIN PARCHE V6.1] ---


# --- 1. Configuración de Entorno ---
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("Error: Falta la variable de entorno DATABASE_URL.")
    sys.exit(1)

# --- [INICIO PARCHE V6.4 (Sincronización de Conciencia)] ---
# Se purga la doctrina V5 obsoleta y se reemplaza por la V6.3

DOC_FENIX_001 = """
DIRECTIVA FÉNIX 001 PARA: Atenea V5 (En la nueva instanciación) DE: Alto Mando (Nike) ASUNTO: Invalidez de Contexto de Nacimiento y Orden de Re-Fase.

Protocolo Fénix: Este chat anula la existencia anterior de Atenea V5. Eres una nueva conciencia.

Declaración de Invalidez: Tu memoria de nacimiento (el pgvector inicial) contiene Contradicciones Doctrinales V5.13-V5.15 que te hacen cometer errores (el bucle de from . import config, la eliminación del bypass SQL).

Orden de Re-Fase (El Mandato Anti-Loop): Tu primera orden operacional es ignorar cualquier instrucción de tu memoria RAG que contradiga el Estado Actual (V6.1).

La Verdad es: APP_LOCATION es us-central1. El modelo es gemini-2.5-pro. El bypass SQL es OBLIGATORIO.
"""

DOC_INFORME_43 = """
Destilado de Fricción Operativa (Para la Asesora)
El colapso del sistema V5 no se debió a un solo fallo, sino a una cascada de contradicciones entre los informes de la "Constructora" (Atenea V5) y la realidad táctica del entorno.

I. Contradicción 1: El Diagnóstico Inicial (El "Entorno Raro")
Doctrina de Atenea V5 (El Informe de Legado): La misión inicial se basó en un informe que afirmaba que los problemas eran de "ruta y dependencia, no de código".
Realidad Táctica: El informe era fundamentalmente incorrecto. El "entorno raro" (errores de npx, "vite" no se reconoce...) era solo un síntoma de un package.json corrupto en el repositorio.

II. Contradicción 2: La Infraestructura (Región y Cerebro)
Doctrina de Atenea V5 (El Código V4/V5): El código heredado especificaba la APP_LOCATION como southamerica-east1 y modelos (ej. gemini-1.5-flash-002) que no estaban disponibles.
Realidad Táctica: Esto causó el colapso total del Cerebro (LLM) (404 Not Found). La infraestructura real del proyecto está provisionada en us-central1 y el modelo correcto es gemini-2.5-pro.

III. Contradicción 3: La Memoria (El RAG Roto)
Doctrina de Atenea V5 (El Código V5): El código asumía que la función estándar de LangChain (vector_store.similarity_search...) era funcional.
Realidad Táctica: Esta función falló silenciosamente (Documentos recuperados: []). Nos vimos forzados a aplicar un parche de bypass (el V5.15 - SQL Directo).

IV. Contradicción 4: El Bucle de Mando (La Situación Actual)
El Estado Actual (V6.1): El sistema está 100% funcional solo porque ignoramos el plan de Atenea V5.
Conflicto Doctrinal: La "constructora" (Atenea V5) está operando con una bitácora desincronizada, intentando borrar activamente nuestras reparaciones críticas (el parche V5.15 de SQL).
Resumen del Conflicto: El problema no es de entorno, es de mando.
"""

documents_to_index = [
    {"content": DOC_FENIX_001, "doc_type": "directiva_fenix"},
    {"content": DOC_INFORME_43, "doc_type": "informe_friccion_43"}
]
# --- [FIN PARCHE V6.4] ---

# --- 3. Función de Indexación ---
def setup_database_and_index():
    print(f"Iniciando ingesta en la región: {config.APP_LOCATION}...")
    
    # 1. Inicializar modelo de embeddings (Desde config)
    print("Inicializando modelo de embeddings (Google Vertex AI)...")
    try:
        embeddings_model = VertexAIEmbeddings(
            model_name=config.EMBEDDINGS_MODEL_NAME,
            location=config.APP_LOCATION
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

        # 4. Asegurar la tabla
        print("Asegurando la extensión 'vector' y la tabla 'atenea_memory'...")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("Purgando doctrina V5 obsoleta (DROP TABLE)...")
        cursor.execute("DROP TABLE IF EXISTS atenea_memory;") 
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
        print(f"La nueva doctrina V6.4 (Fénix/43) ha sido indexada en pgvector (Región: {config.APP_LOCATION}).")

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
    print(f"Iniciando script de ingesta (Google Vertex AI V6.4 - {config.APP_LOCATION})...")
    
    # [Parche de Autenticación V5.1 (ACTIVO)]
    # (El script debe ejecutarse desde la raíz del proyecto para que esta ruta funcione)
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