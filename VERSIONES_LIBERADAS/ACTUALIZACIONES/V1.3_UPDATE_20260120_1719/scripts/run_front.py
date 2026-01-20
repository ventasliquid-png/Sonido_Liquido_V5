
import subprocess
import sys
import shutil
from pathlib import Path

def main():
    """
    Script universal para iniciar el servidor de desarrollo del Frontend.
    Reemplaza a activar_frontend.bat.
    """
    # Definir rutas
    base_dir = Path(__file__).resolve().parent.parent
    frontend_dir = base_dir / "frontend"
    
    print(f"🎨 Iniciando Frontend V5 en: {frontend_dir}")

    # Verificar si npx está instalado
    npx_cmd = shutil.which("npx")
    if not npx_cmd:
        print("❌ Error: No se encontró 'npx' en el sistema. Asegúrate de tener Node.js instalado.")
        sys.exit(1)

    # Comando para iniciar vite a través de npx (para evitar problemas de ruta)
    cmd = [npx_cmd, "vite"]

    print(f"⚡ Ejecutando: {' '.join(cmd)}")
    
    try:
        # Ejecutar desde el directorio frontend
        subprocess.run(cmd, cwd=frontend_dir, check=True, shell=True if sys.platform == "win32" else False)
    except KeyboardInterrupt:
        print("\n🛑 Frontend detenido por el usuario.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al ejecutar el frontend: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
