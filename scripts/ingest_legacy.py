import os
import time
import google.generativeai as genai
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno si existen
load_dotenv()

# --- CONFIGURACIÓN ---
# Asegúrese de tener su API KEY seteada en las variables de entorno o péguela aquí (no recomendado para prod)
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("⚠️  ADVERTENCIA: No se encontró GEMINI_API_KEY en las variables de entorno.")
    print("   Por favor, configure la variable o edite el script para incluirla.")
    # Opcional: input manual
    # api_key = input("Ingrese su API Key de Google AI Studio: ").strip()

if api_key:
    genai.configure(api_key=api_key)

# Nombre de la carpeta donde puso los PDFs descargados
# Ajustamos para que funcione desde la raíz del proyecto
SOURCE_DIR = "./bas_legacy_docs"
# Nombre de la Bóveda en la Nube
STORE_NAME = "BAS_LEGADO_MUSEO_V1"

def upload_to_gemini(path, mime_type=None):
    """Sube el archivo a la API (Capa Física)"""
    try:
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"⬆️ Subido: {file.display_name} as {file.uri}")
        return file
    except Exception as e:
        print(f"❌ Error subiendo {path}: {e}")
        return None

def wait_for_files_active(files):
    """Espera a que Google procese los archivos antes de indexarlos"""
    print("⏳ Esperando procesamiento de archivos...")
    for file in files:
        if not file: continue
        name = file.name
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(5)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            print(f"\n❌ El archivo {file.name} falló al procesarse. Estado: {file.state.name}")
        else:
            print(f"\n✅ {file.display_name} listo.")

def main():
    # 1. Detectar archivos locales
    # Aseguramos que la ruta sea absoluta o correcta relativa al CWD
    source_path = Path(SOURCE_DIR)
    if not source_path.exists():
        print(f"❌ No encontré la carpeta {SOURCE_DIR}. Asegúrese de correr el script desde la raíz del proyecto.")
        return

    file_paths = [p for p in source_path.glob('*') if p.suffix.lower() in ['.pdf', '.txt', '.csv', '.xlsx']]
    if not file_paths:
        print(f"❌ No encontré archivos compatibles en {SOURCE_DIR}.")
        return

    print(f"🔍 Encontrados {len(file_paths)} documentos para ingestión.")

    if not api_key:
        print("❌ No se puede proceder sin API Key.")
        return

    # 2. Crear la Bóveda (Vector Store) - Nota: El código original usaba genai.caching, 
    # pero para File Search simple con la API actual, subimos archivos y obtenemos URIs.
    
    print("🏛️ Iniciando proceso de subida...")
    
    # 1. Subir Archivos
    uploaded_files = []
    for path in file_paths:
        f = upload_to_gemini(path)
        if f:
            uploaded_files.append(f)
    
    if not uploaded_files:
        print("❌ No se subió ningún archivo.")
        return

    # 2. Esperar que estén activos
    wait_for_files_active(uploaded_files)

    # 3. Reporte Final
    print("\n" + "="*40)
    print("✅ MISIÓN CUMPLIDA. COPIE ESTO:")
    print("="*40)
    print(f"Archivos subidos y listos para usar en Antigravity:")
    for f in uploaded_files:
        print(f"- {f.display_name}: {f.uri}")
    
    print("\n⚠️ IMPORTANTE: Guarde estos URIs.")
    print("Para usarlo en el chat, Antigravity debe enviar estos archivos en el history o contexto.")

if __name__ == "__main__":
    main()
