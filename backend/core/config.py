"""
Módulo Core (V10.10): Configuración y Constantes de IA.
Contiene las variables de configuración para los modelos de IA.

--- [ACTUALIZADO A V10.E (SEGURIDAD)] ---
Añadidas constantes para la generación de Tokens JWT.
"""
import os

# --- Configuración de IA y Región ---
APP_LOCATION = "us-central1"
EMBEDDINGS_MODEL_NAME = "text-embedding-004"
GEMINI_MODEL_NAME = "gemini-pro"

# --- [INICIO FASE 10.E (SEGURIDAD)] ---

# 1. Clave secreta para firmar los JWT.
#    (En un sistema en producción, esto NUNCA debe estar en el código,
#     se carga desde una variable de entorno o un 'secrets manager')
#    Para V10.E, usaremos una clave de desarrollo generada (openssl rand -hex 32):
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

# 2. Algoritmo de encriptación
ALGORITHM = "HS256"

# 3. Duración del Token (en minutos)
ACCESS_TOKEN_EXPIRE_MINUTES = 1500 # 1500 minutos (25 horas)

# --- [FIN FASE 10.E] ---

print("--- [Atenea V10.E]: Core/Config (IA y Seguridad JWT) cargado. ---")
