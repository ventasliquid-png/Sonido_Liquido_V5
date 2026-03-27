import os
import sys

# Simular carga de entorno como main.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.core import config
from langchain_google_vertexai import VertexAIEmbeddings

def test_handshake():
    print("========================================================")
    print("       TEST DE CONEXIÓN REAL - GOOGLE VERTEX AI")
    print("========================================================")
    
    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    print(f"[*] Credenciales: {creds}")
    
    if not creds or not os.path.exists(creds):
        print("[!] ERROR: No se encuentran las credenciales.")
        return False
        
    print(f"[*] Inicializando VertexAIEmbeddings (Region: {config.APP_LOCATION})...")
    try:
        embeddings = VertexAIEmbeddings(
            model_name=config.EMBEDDINGS_MODEL_NAME,
            location=config.APP_LOCATION
        )
        
        print("[*] Ejecutando Handshake (Generando embedding de prueba)...")
        test_text = "Handshake test for Sonido Liquido V5"
        vector = embeddings.embed_query(test_text)
        
        print(f"[OK] HANDSHAKE EXITOSO. Vector dim: {len(vector)}")
        print(f" [+] Primeros 5 valores: {vector[:5]}")
        return True
    except Exception as e:
        print(f"[!] FALLO EN HANDSHAKE: {e}")
        return False

if __name__ == "__main__":
    # Aseguro que las variables estén seteadas como en main.py (para el test directo)
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        # Si corremos el script solo, buscamos la ruta manualmente
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        new_creds = os.path.join(root_dir, ".google_credentials_nueva.json", "sistema-liquid-sound-dea230ca8250.json")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = new_creds

    success = test_handshake()
    if success:
        print("\n[+] CERTIFICADO: Conexión a Google Services Activa.")
    else:
        print("\n[!] ERROR CRÍTICO: No se pudo establecer conexión.")
        sys.exit(1)
