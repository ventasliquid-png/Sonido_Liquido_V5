import os
import zipfile
import datetime
from pathlib import Path

def main():
    """
    Script para realizar un respaldo en frío (ZIP) del proyecto Sonido Liquido V5.
    Excluye node_modules, venv, __pycache__ y .git.
    Detecta o solicita la ruta de Google Drive.
    """
    # 1. Configuración de Rutas
    root_dir = Path("C:/dev/Sonido_Liquido_V5")
    project_name = "V5_Respaldo_OFICINA"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    zip_filename = f"{project_name}_{timestamp}.zip"

    # 2. Carpetas a Excluir
    exclude_dirs = {
        'node_modules',
        'venv',
        '__pycache__',
        '.git'
    }

    # 3. Detección de Google Drive
    possible_drives = ['G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    drive_path = None

    print("🔍 Buscando Google Drive...")
    for drive in possible_drives:
        path = Path(f"{drive}:/Mi unidad")
        if path.exists():
            drive_path = path
            print(f"✅ Google Drive detectado en: {drive_path}")
            break
        
    if not drive_path:
        print("⚠️  No se detectó Google Drive automáticamente.")
        manual_path = input("👉 Por favor, ingresa la ruta de destino (Ej: G:/Mi unidad): ").strip()
        if manual_path:
            drive_path = Path(manual_path)
        else:
            drive_path = Path("C:/dev/_BACKUPS_IOWA") # Fallback local
            print(f"📂 Usando fallback local: {drive_path}")

    if not drive_path.exists():
        print(f"❌ Error: La ruta {drive_path} no existe. Se aborta la misión.")
        return

    target_zip = drive_path / zip_filename

    # 4. Creación del ZIP
    print(f"🚀 Iniciando compresión en: {target_zip}")
    print("📦 Procesando archivos (esto puede tardar unos segundos)...")

    count_files = 0
    try:
        with zipfile.ZipFile(target_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(root_dir):
                # Aplicar exclusiones de directorios
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    file_path = Path(root) / file
                    # Relativa al root del proyecto para el interior del ZIP
                    arcname = file_path.relative_to(root_dir)
                    zipf.write(file_path, arcname)
                    count_files += 1

        print(f"✅ Respaldo completado exitosamente.")
        print(f"📊 Archivos comprimidos: {count_files}")
        print(f"📂 Destino: {target_zip}")

    except Exception as e:
        print(f"❌ Error durante el respaldo: {e}")

    # 5. Verificación de Memoria Vectorial (Informativo)
    vector_dirs = ['chroma_db', 'vector_store', 'chroma']
    found_vector = False
    for v_dir in vector_dirs:
        if (root_dir / v_dir).exists():
            print(f"🧠 Memoria local '{v_dir}' incluida en el respaldo.")
            found_vector = True
            break
    
    if not found_vector:
        print("ℹ️  Aviso: No se halló memoria vectorial local para respaldar.")

if __name__ == "__main__":
    main()
