"""
Módulo Core (V10.10): Configuración y Constantes de IA.
Contiene las variables de configuración para los modelos de IA.

--- [ACTUALIZADO A V10.E (SEGURIDAD)] ---
Añadidas constantes para la generación de Tokens JWT.
"""
import os

# --- Configuración de IA (Autonomía Local) ---
EMBEDDINGS_MODEL_NAME = "text-embedding-004"
GEMINI_MODEL_NAME = "gemini-3.1-pro"

# --- [INICIO FASE 10.E (SEGURIDAD)] ---

# 1. Clave secreta para firmar los JWT.
#    (En un sistema en producción, esto NUNCA debe estar en el código,
#     se carga desde una variable de entorno o un 'secrets manager')
#    Para V10.E, usaremos una clave de desarrollo generada (openssl rand -hex 32):
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

# 2. Algoritmo de encriptación
ALGORITHM = "HS256"

# 3. Duración del Token (en minutos)
# [Card #183, S888, decisión de Carlos 19/10] 7 días SIN USO: la pantalla renueva la sesión sola mientras se usa (POST /auth/refresh, como mucho
# una vez por hora), así que solo vence si el sistema quedó 7 días sin tocar. Antes eran 25 h fijas: una sesión abierta ayer vencía hoy a
# cualquier hora y las acciones que firman con el usuario (no comercial, liberar despacho, conciliar facturas...) fallaban sin explicar por qué.
ACCESS_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # 10080 minutos (7 días)

# --- [FIN FASE 10.E] ---

# --- 4. CORS Config ---
CORS_ORIGINS = ["*"]

# --- Versión del Sistema ---
VERSION = "v5.9.000G"

print("--- [Atenea V10.E]: Core/Config (IA, Seguridad JWT, CORS) cargado. ---")
