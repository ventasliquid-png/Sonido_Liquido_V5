import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from google.cloud import aiplatform
from backend.core import config

def list_models():
    print(f"--- Consultando modelos disponibles en {config.APP_LOCATION} ---")
    
    # Load credentials explicitly
    if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
        creds_path = os.path.join(os.getcwd(), ".google_credentials")
        if os.path.exists(creds_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
    
    try:
        aiplatform.init(location=config.APP_LOCATION)
        models = aiplatform.Model.list()
        
        print(f"Encontrados {len(models)} modelos personalizados.")
        for model in models:
            print(f"- {model.display_name} ({model.resource_name})")
            
        print("\nNota: Los modelos 'Publisher' (como Gemini) no siempre aparecen en esta lista básica.")
        print("Intentando listar Publisher Models...")
        
        # This is a bit more complex via SDK, usually we just guess the name.
        # But let's try to verify if we can access the API at all.
        from vertexai.preview.generative_models import GenerativeModel
        
        test_models = ["gemini-1.5-flash-001", "gemini-1.5-pro-001", "gemini-1.0-pro", "gemini-pro"]
        
        for m in test_models:
            try:
                print(f"Probando acceso a '{m}'...", end=" ")
                model = GenerativeModel(m)
                response = model.generate_content("Hola")
                print(f"✅ OK")
                print(f"   Respuesta: {response.text}")
                return # Found one!
            except Exception as e:
                print(f"❌ Falló ({e})")

    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    list_models()
