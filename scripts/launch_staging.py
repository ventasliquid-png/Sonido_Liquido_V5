import subprocess
import os

STAGING_DIR = r"C:\dev\V5-LS\staging"
# We'll use the absolute path to python to avoid environment issues
PYTHON_EXE = "python" 

def start_staging():
    print(f"--- Iniciando Sistema Gemelo (S) en Puerto 8091 ---")
    try:
        # We start it as a background process
        process = subprocess.Popen(
            [PYTHON_EXE, "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8091"],
            cwd=STAGING_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print(f" [OK] Proceso iniciado. PID: {process.pid}")
        # Wait a bit to see if it crashes
        import time
        time.sleep(3)
        if process.poll() is not None:
             stdout, stderr = process.communicate()
             print(f" [!] El proceso falló al arrancar:\n{stderr}")
        else:
             print(" [OK] El servidor parece estar corriendo. Procedo a verificar con el navegador.")
             
    except Exception as e:
        print(f" [!] Error: {str(e)}")

if __name__ == "__main__":
    start_staging()
