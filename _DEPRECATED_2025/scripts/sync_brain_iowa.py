
import os
import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from pgvector.psycopg2 import register_vector
from langchain_google_vertexai import VertexAIEmbeddings
from dotenv import load_dotenv
import uuid

# --- CONFIGURACION ---
load_dotenv()

# IOWA (Destino)
IOWA_HOST = "104.197.57.226"
IOWA_USER = "postgres"
IOWA_PASS = "SonidoV5_2025"
IOWA_DB = "postgres"

# PILOTO (Origen)
LOCAL_DB_PATH = "pilot.db"

# GOOGLE (Embeddings)
GAC_PATH = r"O:\Mi unidad\Sonido-liquido-api\service-account.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GAC_PATH

def sync_brain():
    print("--- 🧠 INICIANDO SINCRONIZACION DE CEREBRO (V5 TÁCTICO) ---")
    
    # 1. Extraer Datos Locales
    if not os.path.exists(LOCAL_DB_PATH):
        print(f"❌ Error: No se encontró {LOCAL_DB_PATH}")
        return

    print("📦 Extrayendo datos de pilot.db...")
    local_conn = sqlite3.connect(LOCAL_DB_PATH)
    cur_local = local_conn.cursor()
    
    # Clientes
    cur_local.execute("""
        SELECT c.razon_social, c.cuit, s.nombre as segmento
        FROM clientes c
        LEFT JOIN segmentos s ON c.segmento_id = s.id
        WHERE c.activo = 1
    """)
    clientes = cur_local.fetchall()
    
    # Productos
    cur_local.execute("""
        SELECT p.nombre, r.nombre as rubro, pc.costo_reposicion, pc.margen_mayorista
        FROM productos p
        LEFT JOIN rubros r ON p.rubro_id = r.id
        LEFT JOIN productos_costos pc ON p.id = pc.producto_id
        WHERE p.activo = 1
    """)
    productos = cur_local.fetchall()
    
    local_conn.close()
    print(f"✅ Encontrados {len(clientes)} clientes y {len(productos)} productos activos.")

    # 2. Preparar Documentos
    docs = []
    for c in clientes:
        content = f"CLIENTE: {c[0]} | CUIT: {c[1]} | SEGMENTO: {c[2] if c[2] else 'GENERAL'}"
        docs.append({"content": content, "doc_type": "tactica_cliente"})
    
    for p in productos:
        costo = p[2] if p[2] else 0
        margen = p[3] if p[3] else 0
        sugerido = costo * (1 + margen/100)
        content = f"PRODUCTO: {p[0]} | RUBRO: {p[1] if p[1] else 'GENERAL'} | COSTO: {costo:.2f} | MARGEN: {margen}% | SUGERIDO: {sugerido:.2f}"
        docs.append({"content": content, "doc_type": "tactica_producto"})

    if not docs:
        print("Empty documentation list. Nothing to sync.")
        return

    # 3. Vectorizar
    print("🚀 Generando Embeddings (Google Vertex AI - text-embedding-004)...")
    try:
        embeddings_model = VertexAIEmbeddings(model_name="text-embedding-004", location="us-central1")
        contents = [d["content"] for d in docs]
        
        # Batching (Vertex AI allows 250 max, we use 100 for safety)
        vectors = []
        batch_size = 100
        for i in range(0, len(contents), batch_size):
            batch = contents[i:i + batch_size]
            print(f"  Procesando lote {i//batch_size + 1}...")
            batch_vectors = embeddings_model.embed_documents(batch)
            vectors.extend(batch_vectors)
            
        print(f"✅ {len(vectors)} vectores generados.")
    except Exception as e:
        print(f"❌ Error en Vertex AI: {e}")
        return

    # 4. Inyectar en IOWA
    print("🔗 Conectando a IOWA Postgres...")
    try:
        remote_conn = psycopg2.connect(
            host=IOWA_HOST,
            user=IOWA_USER,
            password=IOWA_PASS,
            dbname=IOWA_DB,
            sslmode='require'
        )
        register_vector(remote_conn)
        cur_remote = remote_conn.cursor()

        # 4. Asegurar la tabla (Siguiendo estándar ingest_memory.py)
        print("Asegurando la tabla 'atenea_memory'...")
        cur_remote.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        
        # Verificar si existe, si no, crearla
        cur_remote.execute("""
            CREATE TABLE IF NOT EXISTS atenea_memory (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL, 
                doc_type VARCHAR(50),
                embedding VECTOR(768)
            );
        """)
        
        # Limpiar vectores tácticos anteriores
        print("🧹 Limpiando vectores tácticos previos en atenea_memory...")
        cur_remote.execute("DELETE FROM atenea_memory WHERE doc_type LIKE 'tactica_%'")
        
        # Insertar nuevos
        print(f"📥 Insertando {len(docs)} nuevos vectores...")
        data_to_insert = []
        for i, doc in enumerate(docs):
            data_to_insert.append((doc["content"], doc["doc_type"], vectors[i]))
            
        execute_values(
            cur_remote,
            "INSERT INTO atenea_memory (content, doc_type, embedding) VALUES %s",
            data_to_insert
        )
        
        remote_conn.commit()
        cur_remote.close()
        remote_conn.close()
        
        print("\n" + "="*40)
        print("📊 CEREBRO SINCRONIZADO")
        print(f"Se han subido {len(docs)} vectores a IOWA.")
        print("="*40)

    except Exception as e:
        print(f"❌ Error en la inyección IOWA: {e}")

if __name__ == "__main__":
    sync_brain()
