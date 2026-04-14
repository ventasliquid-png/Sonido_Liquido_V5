import subprocess
import webbrowser
import time
import os
import signal
import sys
import threading
import urllib.request

def stream_reader(pipe, prefix):
    """Lee la salida de un proceso y la imprime con un prefijo."""
    try:
        for line in iter(pipe.readline, ''):
            if line:
                print(f"[{prefix}] {line.strip()}")
    except Exception:
        pass

def main():
    print("--- [MISIÓN B] LANZADOR UNIFICADO V5 START ---")
    
    # Definir rutas
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend") # Aunque main.py se corre desde root, el folder existe
    frontend_dir = os.path.join(root_dir, "frontend")

    # Monitor Loop
    backend_restarts = 0
    last_restart_time = time.time()
    
    # Define command correctly in scope
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "backend.main:app",
        "--host", "0.0.0.0", "--port", "8080", "--reload",
        "--reload-dir", os.path.join(root_dir, "backend"),
    ]

    def start_backend():
        print(f">>> Iniciando Backend (Intento #{backend_restarts + 1})...")
        p = subprocess.Popen(
            backend_cmd,
            cwd=root_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
        )
        # Hilos de lectura
        threading.Thread(target=stream_reader, args=(p.stdout, "BACKEND"), daemon=True).start()
        threading.Thread(target=stream_reader, args=(p.stderr, "BACK_ERR"), daemon=True).start()
        return p

    # Initial Start
    backend_process = start_backend()

    # 2. Levantando Frontend
    print(">>> [2/3] Iniciando Frontend (Port 5173)...")
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", "5173"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        shell=True 
    )
    threading.Thread(target=stream_reader, args=(frontend_process.stdout, "FRONTEND"), daemon=True).start()
    threading.Thread(target=stream_reader, args=(frontend_process.stderr, "FRONT_ERR"), daemon=True).start()

    # 3. Abrir Navegador (esperar hasta que el backend responda)
    print(">>> [3/3] Esperando que el backend esté listo...")
    url = "http://localhost:5173"
    backend_health = "http://localhost:8080/docs"
    for _ in range(30):  # max 30 segundos
        try:
            urllib.request.urlopen(backend_health, timeout=1)
            print(">>> Backend listo. Abriendo navegador...")
            break
        except Exception:
            time.sleep(1)
    else:
        print(">>> [WARN] Backend no respondió en 30s, abriendo navegador igual...")
    webbrowser.open(url)

    print(f">>> SISTEMA CORRIENDO EN: {url}")
    print(">>> PRESIONE CTRL+C PARA CERRAR EL SISTEMA.")

    try:
        while True:
            time.sleep(1)
            
            # 1. Check Frontend
            if frontend_process.poll() is not None:
                print("!!! ALERTA: El Frontend se ha detenido. Apagando sistema...")
                break

            # 2. Check Backend
            if backend_process.poll() is not None:
                print(f"!!! ALERTA: El Backend se detuvo (Exit Code: {backend_process.returncode})")
                
                # Check crash frequency (Logic: if > 3 restarts in 60 seconds, give up)
                current_time = time.time()
                if (current_time - last_restart_time) > 60:
                    # Reset counter if it's been a while
                    backend_restarts = 0
                    last_restart_time = current_time
                
                if backend_restarts < 5:
                    print(">>> [AUTO-RESTART] Reiniciando Backend en 3 segundos...")
                    time.sleep(3)
                    backend_restarts += 1
                    backend_process = start_backend()
                else:
                    print("!!! ERROR FATAL: El Backend falla repetidamente. Abortando.")
                    break
                    
    except KeyboardInterrupt:
        print("\n>>> DETENCION SOLICITADA (CTRL+C)...")
    finally:
        print(">>> EJECUTANDO PROTOCOLO DE LIMPIEZA DE PROCESOS...")
        
        # Función helper para matar árbol de procesos en Windows
        def kill_tree(pid):
            try:
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], 
                               capture_output=True, check=False)
            except Exception as e:
                print(f"Error matando PID {pid}: {e}")

        if backend_process:
            print(f" - Matando Backend (PID {backend_process.pid})...")
            kill_tree(backend_process.pid)
        
        if frontend_process:
            print(f" - Matando Frontend (PID {frontend_process.pid})...")
            kill_tree(frontend_process.pid)

        print(">>> SISTEMA APAGADO. Hasta la próxima.")

if __name__ == "__main__":
    main()
