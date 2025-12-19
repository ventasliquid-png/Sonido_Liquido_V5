import subprocess
import sys
import shutil
import socket
import os
from pathlib import Path

def get_local_ip():
    """Obtiene la IP local de la máquina."""
    try:
        # Crea un socket para obtener la IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def main():
    """
    Script universal para lanzar HAWE V5 en modo LAN (Acceso Remoto).
    Reemplaza a run_lan.ps1.
    """
    base_dir = Path(__file__).resolve().parent.parent
    frontend_dir = base_dir / "frontend"
    
    ip = get_local_ip()
    print(f"--- HAWE V5 MODO LAN ---")
    print(f"🌍 Tu IP Local es: {ip}")

    # 1. Configurar .env.local para el Frontend (Modo Proxy Relativo)
    # Esto permite que el browser remoto le pida todo al server del frontend (5173)
    # y este lo redireccione internamente al backend.
    env_local_path = frontend_dir / ".env.local"
    try:
        with open(env_local_path, "w") as f:
            f.write("VITE_API_URL=\n")
        print(f"✅ Configuración PROXY guardada en {env_local_path.name}")
    except Exception as e:
        print(f"❌ Error al escribir .env.local: {e}")

    # 2. Instrucciones
    print(f"\n🚀 Iniciando servicios...")
    print(f"📱 Para acceder desde otra PC, ve a: http://{ip}:5173")
    print(f"--------------------------------------------------\n")

    # 3. Lanzar Backend (en segundo plano / paralelo si fuera posible, 
    # pero mejor instruir al usuario a usar ventanas separadas o lanzar uno tras otro)
    # Dado que subprocess.run es bloqueante, lanzaremos el backend en un subproceso 
    # y el frontend en otro si estamos en un script de orquestación, 
    # o simplemente lanzar el comando de backend.
    
    print("💡 TIP: Para MODO LAN completo, el backend debe escuchar en 0.0.0.0")
    
    # Preparamos el entorno para el backend (PYTHONPATH)
    backend_env = os.environ.copy()
    backend_env["PYTHONPATH"] = str(base_dir) + os.pathsep + backend_env.get("PYTHONPATH", "")

    # Comando Backend
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    
    # Comando Frontend
    npx_cmd = shutil.which("npx")
    if not npx_cmd:
        print("❌ Error: 'npx' no encontrado. No se puede iniciar el frontend.")
        sys.exit(1)
    frontend_cmd = [npx_cmd, "vite", "--host"]

    print(f"📡 Backend escuchando en: http://0.0.0.0:8000")
    print(f"🖥️  Frontend escuchando en: http://0.0.0.0:5173")

    # Intentamos lanzar ambos. En Python es mejor usar Popen para no bloquear.
    try:
        print("\n🔥 Lanzando Backend...")
        p_backend = subprocess.Popen(backend_cmd, cwd=base_dir, env=backend_env)
        
        print("🌈 Lanzando Frontend...")
        p_frontend = subprocess.Popen(frontend_cmd, cwd=frontend_dir, shell=True if sys.platform == "win32" else False)
        
        print("\n✅ Ambos servicios están corriendo. Presiona Ctrl+C para detener ambos.")
        
        # Esperar a que terminen (o que el usuario interrumpa)
        p_backend.wait()
        p_frontend.wait()

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servicios...")
        p_backend.terminate()
        p_frontend.terminate()
    except Exception as e:
        print(f"❌ Error al lanzar servicios: {e}")

if __name__ == "__main__":
    main()
