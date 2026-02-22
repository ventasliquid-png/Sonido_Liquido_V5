import json
import time
import os
from datetime import datetime, timedelta

# --- CONFIGURACIÓN TÁCTICA ---
STATUS_FILE = "quota_status.json"
DEFAULT_COOLDOWN = 60  # Segundos (Mínimo estándar RPM)
MODEL_PRO = "gemini-3.1-pro"
MODEL_FLASH = "gemini-1.5-flash"

def registrar_penalizacion(error_msg=None, retry_after=None):
    """
    Simula la captura de un error 429 e inicia el reloj táctico.
    Si retry_after no viene de la API, usa el DEFAULT_COOLDOWN.
    """
    espera = int(retry_after) if retry_after else DEFAULT_COOLDOWN
    release_time = datetime.now() + timedelta(seconds=espera)
    
    status = {
        "status": "DEGRADADO",
        "active_model": MODEL_FLASH,
        "release_timestamp": release_time.isoformat(),
        "reason": error_msg or "Quota limit reached (429)",
        "last_update": datetime.now().isoformat()
    }
    
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=4)
    
    print(f"[CLOCK] Penalización iniciada. Liberación estimada: {status['release_timestamp']}")
    print(f"[CLOCK] Downgrade automático activo: Usando {MODEL_FLASH}")

def get_current_tactical_model():
    """
    Lógica de enrutamiento dinámico.
    Si el reloj está activo, devuelve Flash. Si expiró, vuelve a Pro.
    """
    if not os.path.exists(STATUS_FILE):
        return MODEL_PRO
    
    try:
        with open(STATUS_FILE, "r") as f:
            status = json.load(f)
        
        release_time = datetime.fromisoformat(status["release_timestamp"])
        
        if datetime.now() < release_time:
            segundos_restantes = int((release_time - datetime.now()).total_seconds())
            print(f"[RELOJ] Modo Degradado: Quedan {segundos_restantes}s para volver a {MODEL_PRO}")
            return MODEL_FLASH
        else:
            # Auto-Upgrade: El tiempo expiró
            print(f"[RELOJ] Tiempo cumplido. Auto-Upgrade ejecutado: Volviendo a {MODEL_PRO}")
            # Limpiamos el archivo para la próxima
            os.remove(STATUS_FILE)
            return MODEL_PRO
            
    except Exception as e:
        print(f"[ERROR] No se pudo leer el estado: {e}")
        return MODEL_PRO

# --- BLOQUE DE PRUEBA Y SIMULACIÓN ---
if __name__ == "__main__":
    print("--- INICIANDO SIMULACIÓN DE CUOTA ---")
    
    # 1. Simulamos el impacto de un error 429
    print("\n[SIM] Recibiendo Error 429: Resource Exhausted...")
    registrar_penalizacion(retry_after=15) # 15 segundos para la prueba rápida
    
    # 2. Bucle de monitoreo para ver el Downgrade/Upgrade en acción
    for i in range(20):
        modelo = get_current_tactical_model()
        print(f"Iteración {i+1}: Modelo Activo -> {modelo}")
        time.sleep(1)
    
    print("\n--- FIN DE SIMULACIÓN ---")
