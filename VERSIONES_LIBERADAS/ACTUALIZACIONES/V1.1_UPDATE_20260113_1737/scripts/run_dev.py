import subprocess
import sys
import shutil
import os
from pathlib import Path

def main():
    """
    Script universal para iniciar el servidor de desarrollo (backend).
    Reemplaza a run_dev.ps1 y start_backend.ps1.
    """
    # Definir rutas
    base_dir = Path(__file__).resolve().parent.parent
    backend_dir = base_dir / "backend"
    
    print(f"🚀 Iniciando Sistema V5 en: {base_dir}")
    print(f"📂 Directorio Backend: {backend_dir}")

    # Verificar si uvicorn está instalado/accesible
    uvicorn_cmd = shutil.which("uvicorn")
    
    # Intentar ejecutar como modulo si el binario no está en path
    if not uvicorn_cmd:
        cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    else:
        cmd = ["uvicorn", "backend.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

    print(f"⚡ Ejecutando: {' '.join(cmd)}")
    
    # Añadir el directorio base al PYTHONPATH para que 'backend' sea reconocido como módulo
    env = os.environ.copy()
    env["PYTHONPATH"] = str(base_dir) + os.pathsep + env.get("PYTHONPATH", "")

    try:
        # Ejecutar uvicorn desde el directorio raíz
        subprocess.run(cmd, cwd=base_dir, env=env, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error al ejecutar el servidor: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
