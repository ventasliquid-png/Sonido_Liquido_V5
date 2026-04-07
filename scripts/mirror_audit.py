# [IDENTIDAD] - scripts\mirror_audit.py
# Versión: V5.7 GOLD | Sincronización: 20260407142400
# ---------------------------------------------------------
import os
import hashlib

PATHS = {
    'D': r"C:\dev\Sonido_Liquido_V5",
    'S': r"C:\dev\V5-LS\staging",
    'P': r"C:\dev\V5-LS\current"
}

CORE_FILES = [
    r"backend\clientes\service.py",
    r"frontend\src\views\Hawe\ClientCanvas.vue",
    r"backend\main.py",
    r"backend\core\database.py"
]

def get_hash(path):
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def audit():
    print("========================================================")
    print("       AUDITORÍA DE ESPEJO SOBERANO (V5.7)")
    print("========================================================")
    
    for rel_path in CORE_FILES:
        print(f"\n[ARCHIVO] {rel_path}")
        h_d = get_hash(os.path.join(PATHS['D'], rel_path))
        h_s = get_hash(os.path.join(PATHS['S'], rel_path))
        h_p = get_hash(os.path.join(PATHS['P'], rel_path))
        
        status_dp = "SINC" if h_d == h_p else "DIFF (D divergió de P)"
        status_sp = "SINC" if h_s == h_p else "PENDIENTE DESPLIEGUE (S -> P)"
        status_ds = "SINC" if h_d == h_s else "MODIFICADO EN STAGING (S -> D?)"
        
        print(f"  ∟ D vs P: {status_dp}")
        print(f"  ∟ S vs P: {status_sp}")
        if h_s != h_p:
            print(f"  [BIT ALERT] Bit 1 ON: El Gemelo S tiene cambios para Producción.")
        if h_d != h_s and h_s == h_p:
            print(f"  [BIT ALERT] Bit 2 ON: El Laboratorio D está adelantado. No pasar a P sin Staging.")

if __name__ == "__main__":
    audit()
