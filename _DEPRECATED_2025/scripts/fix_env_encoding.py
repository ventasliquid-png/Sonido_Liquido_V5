
import os

ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

def fix_encoding():
    if not os.path.exists(ENV_PATH):
        print(f"❌ No se encontró el archivo: {ENV_PATH}")
        return

    print(f"🔍 Analizando archivo: {ENV_PATH}")
    
    content = None
    
    # Intentar leer como UTF-16 (Little Endian es el sospechoso por 0xff)
    try:
        with open(ENV_PATH, 'r', encoding='utf-16') as f:
            content = f.read()
        print("✅ Leído exitosamente como UTF-16")
    except Exception as e:
        print(f"⚠️  No es UTF-16: {e}")
        
    # Si falló, intentar UTF-16BE
    if content is None:
        try:
            with open(ENV_PATH, 'r', encoding='utf-16-be') as f:
                content = f.read()
            print("✅ Leído exitosamente como UTF-16-BE")
        except Exception:
            pass

    # Si falló, intentar leer como binario y decodificar a la fuerza ignorando errores o cp1252
    if content is None:
        try:
            with open(ENV_PATH, 'rb') as f:
                raw = f.read()
            # Si empieza con FF FE
            if raw.startswith(b'\xff\xfe'):
                 content = raw.decode('utf-16')
                 print("✅ Detectado BOM UTF-16 LE")
            else:
                 # Fallback
                 print("⚠️  Intentando decodificación forzada clean...")
                 content = raw.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"❌ Error fatal leyendo archivo: {e}")
            return

    # Escribir como UTF-8 estándar
    try:
        with open(ENV_PATH, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"✨ Archivo guardado correctamente como UTF-8 en: {ENV_PATH}")
        
        # Verificar lectura
        with open(ENV_PATH, 'r', encoding='utf-8') as f:
            print("📖 Contenido (Preview):")
            print(f.read()[:100] + "...")
            
    except Exception as e:
        print(f"❌ Error escribiendo archivo: {e}")

if __name__ == "__main__":
    fix_encoding()
