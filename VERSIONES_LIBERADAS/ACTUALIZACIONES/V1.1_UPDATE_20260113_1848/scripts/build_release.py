import shutil
import os
import sys
from datetime import datetime
from pathlib import Path

# Configuración
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "VERSIONES_LIBERADAS"

# Carpetas/Archivos a ignorar en el release
IGNORE_PATTERNS = shutil.ignore_patterns(
    "__pycache__", 
    "node_modules", 
    ".git", 
    ".vscode", 
    "*.log", 
    "dist", 
    ".env", # No copiar credenciales de DEV
    "pilot_dev.db",
    "venv",
    ".pytest_cache",
    "backups",
    "_DEPRECATED_2025",
    "VERSIONES_LIBERADAS"
)

def build_release():
    print("--- CONSTRUCTOR DE VERSIONES V5 ---")
    
    if len(sys.argv) > 1:
        version_tag = sys.argv[1]
        mode = sys.argv[2] if len(sys.argv) > 2 else "A"
        print(f"🤖 Modo Automático: Ver={version_tag}, Mode={mode}")
    else:
        version_tag = input("Ingrese etiqueta de versión (ej: V1.0): ").strip() or "V_SNAPSHOT"
        mode = input("¿Tipo de Paquete? [I]nstalación Completa / [A]ctualización (Código solo): ").strip().upper()
    
    is_update = mode == "A"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
    # Definir Subcarpeta según modo
    subdir_name = "ACTUALIZACIONES" if is_update else "INSTALADORES"
    final_output_dir = OUTPUT_DIR / subdir_name
    
    # Nombre del release
    release_name = f"{version_tag}_{'UPDATE' if is_update else 'FULL'}_{timestamp}"
    target_dir = final_output_dir / release_name
    
    # Configurar filtros dinámicos
    global IGNORE_PATTERNS
    ignore_list = [
        "__pycache__", "node_modules", ".git", ".vscode", "*.log", 
        "dist", "venv", ".pytest_cache", "backups", 
        "_DEPRECATED_2025", "VERSIONES_LIBERADAS"
    ]
    
    # En modo UPDATE, ignoramos datos críticos y configs locales
    if is_update:
        ignore_list.extend(["pilot.db", "pilot_dev.db", ".env", "*.sqlite", "data", ".google_credentials*"])
        print(f"🛡️  MODO ACTUALIZACIÓN: Destino -> {subdir_name}/")
        print("    Se excluirán BDs personales (pilot.db) pero se incluirá CANTERA si existe.")
    else:
        # En modo FULL, solo ignoramos cosas de dev, pero llevamos la DB y env template
        ignore_list.extend(["pilot_dev.db", ".env"]) # .env se recrea manual, pilot.db pasa
        print(f"💿 MODO INSTALACIÓN: Destino -> {subdir_name}/") 
        print("    Se incluye pilot.db base.")

    print(f"📦 Empaquetando: {release_name}")
    print(f"📂 Ruta Final: {target_dir}")
    
    if target_dir.exists():
        print("❌ Error: La versión ya existe.")
        return

    try:
        # Copiar Todo
        shutil.copytree(BASE_DIR, target_dir, ignore=shutil.ignore_patterns(*ignore_list))
        
        # Post-Processing
        if not is_update:
            # Solo en FULL creamos el .env nuevo y renombramos manuales de instalacion
            env_example = target_dir / ".env.example"
            if not env_example.exists():
                with open(target_dir / ".env", "w") as f:
                    f.write("DATABASE_URL=sqlite:///pilot.db\n")
                    f.write("PATH_DRIVE_BACKUP=\n")
            else:
                 shutil.copy(env_example, target_dir / ".env")

            manual_src = target_dir / "MANUAL_INSTALACION.txt"
            manual_dest = target_dir / "LEEME_PRIMERO.txt"
            if manual_src.exists():
                shutil.move(manual_src, manual_dest)
        else:
            # En UPDATE, podríamos poner un LEEME de actualización
            readme_upd = target_dir / "INSTRUCCIONES_UPDATE.txt"
            with open(readme_upd, "w") as f:
                f.write("PARA ACTUALIZAR:\n1. Copie todo el contenido de esta carpeta.\n2. Péguelo en su carpeta de sistema reemplazando los archivos.\n3. NO SE PERDERÁN SUS DATOS (pilot.db no está aquí).")

        print("\n✅ Versión Generada Exitosamente.")
        print(f"👉 Ubicación: {target_dir}")
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        if target_dir.exists():
            shutil.rmtree(target_dir)

if __name__ == "__main__":
    # Asegurar que existe el dir de versiones
    OUTPUT_DIR.mkdir(exist_ok=True)
    build_release()
