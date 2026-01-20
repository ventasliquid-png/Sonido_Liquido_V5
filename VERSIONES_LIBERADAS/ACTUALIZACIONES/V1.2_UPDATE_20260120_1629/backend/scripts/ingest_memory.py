import os
import psycopg2
    print(f"Asegúrate de que 'backend/config.py' exista.")
    sys.exit(1)
# --- [FIN PARCHE V6.1] ---

# --- 1. Configuración de Entorno ---
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("Error: Falta la variable de entorno DATABASE_URL.")
    sys.exit(1)

# --- [INICIO PARCHE V9 (Refactorización "Biblia")] ---
def load_documents_from_data_directory():
    """
    Lee dinámicamente todos los archivos .txt de la carpeta /data/
    y usa el nombre del archivo como 'doc_type'.
    """
    data_dir = os.path.join(script_dir, '..', 'data')
    print(f"Buscando doctrina en: {data_dir}")
    
    # Busca todos los archivos .txt en el directorio /data/
    files = glob.glob(os.path.join(data_dir, "*.txt"))
    
    if not files:
        print(f"Error fatal: No se encontraron archivos .txt en {data_dir}.")
        print("Por favor, crea los 4 archivos de doctrina V9 (fenix, informe43, clientes, integridad).")
        sys.exit(1)
        
    documents_to_index = []
    for file_path in files:
        # Extrae el nombre del archivo (ej: "tactica_v2_3_clientes")
        doc_type = os.path.splitext(os.path.basename(file_path))[0]
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        documents_to_index.append({
            "content": content,
            "doc_type": doc_type
        })
        print(f"Documento cargado: {doc_type}")
        
    return documents_to_index

# (Se eliminan las variables de string gigantes "DOC_FENIX_001", "DOC_INFORME_43", etc.)
documents_to_index = load_documents_from_data_directory()
# --- [FIN PARCHE V9] ---

# --- 3. Función de Indexación ---
def setup_database_and_index():
    print(f"Iniciando ingesta V9 en la región: {config.APP_LOCATION}...")
    
    # 1. Inicializar modelo de embeddings
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
        print("Purgando doctrina V8 (DROP TABLE)...")
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
        print(f"La nueva doctrina V9 (Archivos Externos) ha sido indexada en pgvector (Región: {config.APP_LOCATION}).")

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
    print(f"Iniciando script de ingesta (Google Vertex AI V9 - {config.APP_LOCATION})...")
    
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