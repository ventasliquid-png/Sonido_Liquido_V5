# --- backend/config.py ---
# CONFIGURACION CANONICA DEL ENTORNO V6 (Única Fuente de Verdad)

# --- 1. CONFIGURACIÓN DE INFRAESTRUCTURA (Nike/TAX-6) ---
# Región donde están aprovisionados todos los servicios de Google Cloud (Cloud SQL, Vertex AI).
# Esta es la verdad empírica que descubrimos:
APP_LOCATION = "us-central1"

# --- 2. CONFIGURACIÓN DE CEREBRO (LLM) ---
# Modelo de mayor potencia y disponibilidad verificada en la región us-central1.
# (Lo ponemos aquí para no tener que parchearlo en main.py si cambia)
GEMINI_MODEL_NAME = "gemini-2.5-pro"

# --- 3. CONFIGURACIÓN DE MEMORIA (RAG) ---
# Modelo de Embeddings usado tanto para la ingesta como para la consulta.
EMBEDDINGS_MODEL_NAME = "text-embedding-004"