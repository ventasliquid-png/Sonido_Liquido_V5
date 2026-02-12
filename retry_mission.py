import subprocess
import time
import sys

def retry_mission():
    print("=== MONITOR DE MISIÓN RAR V1 ===")
    print("Estado: Esperando liberación de token AFIP...")
    
    max_retries = 20
    wait_time = 60 # segundos
    
    for i in range(1, max_retries + 1):
        print(f"\n[INTENTO {i}/{max_retries}] Ejecutando misión...")
        
        # Ejecutamos el proxy y capturamos salida
        # Usamos stderr a stdout para capturar todo
        result = subprocess.run(
            [r"C:\dev\RAR_V1\venv\Scripts\python.exe", r"c:\dev\Sonido_Liquido_V5\run_rar_proxy.py"],
            cwd=r"c:\dev\Sonido_Liquido_V5",
            capture_output=True,
            text=True
        )
        
        output = result.stdout + result.stderr
        print(output)
        
        if "EXITO" in output or "MISION CUMPLIDA" in output:
            print("\n[!!!] ¡MISIÓN ÉXITOSA! SE HA OBTENIDO EL CAE.")
            return
            
        if "El CEE ya posee un TA valido" in output:
            print(f"[!] AFIP indica sesión duplicada. Esperando {wait_time}s para reintentar...")
            time.sleep(wait_time)
            continue
            
        if "DN del Source invalido" in output: # Si pasa esto, algo está mal configurado
            print("[X] Error de Configuración (DN). Abortando.")
            break
            
        # Otros errores
        print("[?] Error desconocido o falla técnica. Reintentando en breve...")
        print(f"ERROR OUTPUT:\n{output[:500]}...") # Print preview
        time.sleep(10)

    print("\n[X] Se agotaron los intentos. Revisar logs.")

if __name__ == "__main__":
    retry_mission()
