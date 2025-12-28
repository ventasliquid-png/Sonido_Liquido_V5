import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY no encontrada.")
    exit(1)

genai.configure(api_key=api_key)

# URIs obtenidos de la ingestión previa
FILES = [
    {"name": "MANUAL BAS.pdf", "uri": "https://generativelanguage.googleapis.com/v1beta/files/2gf8e262kxe4"},
    {"name": "INTRODUCCION BAS.pdf", "uri": "https://generativelanguage.googleapis.com/v1beta/files/u8330k3pq90c"}
]

def analyze_clients():
    print("🕵️ UNIDAD FORENSE-1: Iniciando análisis de documentos legado...")
    
    # Preparar los archivos para el modelo (usando los URIs ya subidos)
    # La API de python permite pasar objetos con 'file_uri' y 'mime_type' o simplemente buscar el archivo
    
    # Listar modelos para debug si falla
    print("--- MODELOS DISPONIBLES ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
    print("---------------------------")

    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = """
    ACTÚA COMO: UNIDAD FORENSE-1 (Especialista en Recuperación de Legado).
    
    TU OBJETIVO: Analizar la estructura de datos de la entidad "CLIENTES" basándote estrictamente en los manuales PDF proporcionados.
    
    INSTRUCCIONES:
    1. Busca referencias a "Ficha de Clientes", "Alta de Clientes" o "Maestro de Clientes".
    2. Extrae TODOS los campos de datos solicitados por el sistema viejo (BAS) para un cliente.
    3. Detecta reglas de negocio implícitas.
    
    FORMATO DE SALIDA (Markdown):
    Genera una tabla comparativa con 3 columnas:
    | CAMPO DETECTADO (BAS) | ¿PARA QUÉ SERVÍA? | PROPUESTA MIGRACIÓN V5 (Tu sugerencia) |
    
    Si encuentras capturas de pantalla, infiere los campos.
    """
    
    # Recuperar objetos de archivo
    content_parts = [prompt]
    for f_info in FILES:
        print(f"   - Cargando referencia a: {f_info['name']}...")
        # Nota: En la SDK actual, podemos pasar el URI directamente o recuperar el objeto file
        # Intentaremos recuperar el objeto file para asegurar contexto
        try:
            # Creamos un objeto que la API entienda, o usamos el URI string si la versión lo soporta
            # La forma estándar es genai.get_file(name) pero el name interno es diferente al URI.
            # El URI tiene formato https://.../files/NAME
            # Extraemos el nombre interno del URI
            file_name = f_info['uri'].split("/files/")[-1]
            file_obj = genai.get_file(file_name)
            content_parts.append(file_obj)
        except Exception as e:
            print(f"⚠️ Error recuperando archivo {f_info['name']}: {e}")

    print("🧠 Procesando con Gemini 2.0 Flash...")
    response = model.generate_content(content_parts)
    
    report_content = "\n" + "="*20 + " REPORTE FORENSE " + "="*20 + "\n\n" + response.text
    
    print(report_content)
    
    with open("analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("✅ Reporte guardado en analysis_report.md")

if __name__ == "__main__":
    analyze_clients()
