import subprocess
import webbrowser
import time
import os
import signal
import sys
import threading

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

    # 1. Levantando Backend
    # Se ejecuta via modulo para evitar problemas de path/reload
    print(">>> [1/3] Iniciando Backend (Port 8000)...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"]
    
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=root_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Hilos para no bloquear leyendo salida
    t_be_out = threading.Thread(target=stream_reader, args=(backend_process.stdout, "BACKEND"), daemon=True)
    t_be_err = threading.Thread(target=stream_reader, args=(backend_process.stderr, "BACK_ERR"), daemon=True)
    t_be_out.start()
    t_be_err.start()

    # 2. Levantando Frontend
    print(">>> [2/3] Iniciando Frontend (Port 5173)...")
    # npm run dev -- --port 5173
    # shell=True es necesario en Windows para encontrar npm
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", "5173"],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        shell=True 
    )

    t_fe_out = threading.Thread(target=stream_reader, args=(frontend_process.stdout, "FRONTEND"), daemon=True)
    t_fe_err = threading.Thread(target=stream_reader, args=(frontend_process.stderr, "FRONT_ERR"), daemon=True)
    t_fe_out.start()
    t_fe_err.start()

    # 3. Abrir Navegador
    print(">>> [3/3] Abriendo Navegador en 5 segundos...")
    time.sleep(5)
    url = "http://localhost:5173"
    webbrowser.open(url)

    print(f">>> SISTEMA CORRIENDO EN: {url}")
    print(">>> PRESIONE CTRL+C PARA CERRAR EL SISTEMA.")

    try:
        while True:
            time.sleep(1)
            # Verificar si algún proceso murió
            if backend_process.poll() is not None:
                print("!!! ALERTA: El Backend se ha detenido.")
                break
            if frontend_process.poll() is not None:
                print("!!! ALERTA: El Frontend se ha detenido.")
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
