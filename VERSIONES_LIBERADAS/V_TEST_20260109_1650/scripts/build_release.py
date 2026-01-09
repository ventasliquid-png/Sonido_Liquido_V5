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
    
    version_tag = input("Ingrese etiqueta de versión (ej: V1.0): ").strip() or "V_SNAPSHOT"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    release_name = f"{version_tag}_{timestamp}"
    target_dir = OUTPUT_DIR / release_name
    
    print(f"📦 Empaquetando: {release_name}")
    print(f"📂 Destino: {target_dir}")
    
    if target_dir.exists():
        print("❌ Error: La versión ya existe.")
        return

    try:
        # Copiar Todo (con filtros)
        shutil.copytree(BASE_DIR, target_dir, ignore=IGNORE_PATTERNS)
        
        # Post-Processing Manual
        # 1. Crear .env template limpio
        env_example = target_dir / ".env.example"
        if not env_example.exists():
            with open(target_dir / ".env", "w") as f:
                f.write("DATABASE_URL=sqlite:///pilot.db\n")
                f.write("PATH_DRIVE_BACKUP=\n")
                f.write("# GOOGLE_APPLICATION_CREDENTIALS=./.google_credentials\n")
        else:
             shutil.copy(env_example, target_dir / ".env")
        
        # 2. Asegurar pilot.db base (si existe una limpia, o copiar la actual y advertir)
        # Idealmente copiamos pilot.db pero advertimos que debe limpiarse si es DEV
        # (El shutil copytree ya la copió si no estaba en ignore, lo cual es correcto para V1)

        # 3. Renombrar Manual para Visibilidad
        manual_src = target_dir / "MANUAL_INSTALACION.txt"
        manual_dest = target_dir / "LEEME_PRIMERO.txt"
        if manual_src.exists():
            shutil.move(manual_src, manual_dest)
        
        print("\n✅ Versión Generada Exitosamente.")
        print(f"👉 Ubicación: {target_dir}")
        print("⚠️  NOTA: La base de datos 'pilot.db' copiada es la actual. Recuerde limpiarla si contiene datos de prueba.")
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        if target_dir.exists():
            shutil.rmtree(target_dir)

if __name__ == "__main__":
    # Asegurar que existe el dir de versiones
    OUTPUT_DIR.mkdir(exist_ok=True)
    build_release()
