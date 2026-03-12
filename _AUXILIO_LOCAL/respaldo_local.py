
import os
import shutil
import zipfile
from datetime import datetime

# Estrategia de Auxilio Local
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # c:\dev\Sonido_Liquido_V5\_AUXILIO_LOCAL
ROOT_DIR = os.path.dirname(BASE_DIR) # c:\dev\Sonido_Liquido_V5
BACKUP_DIR = os.path.join(ROOT_DIR, "_AUXILIO_LOCAL")

def crear_respaldo():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"[INFO] Carpeta de auxilio creada: {BACKUP_DIR}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"RESPALDO_LOCAL_{timestamp}.zip"
    zip_path = os.path.join(BACKUP_DIR, zip_filename)

    print(f"--- [PROTOCOLO AUXILIO] Iniciando respaldo local: {zip_filename} ---")

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Pilot DB
            pilot_db = os.path.join(ROOT_DIR, "pilot.db")
            if os.path.exists(pilot_db):
                print(f"[+] Agregando pilot.db ({os.path.getsize(pilot_db)/1024:.2f} KB)...")
                zipf.write(pilot_db, arcname="pilot.db")
            else:
                print("[!] ALERTA: pilot.db no encontrado!")

            # 2. RAR V1 Folder (Satélite)
            # Asumiendo que RAR_V1 está en el mismo nivel o una ruta conocida. 
            # El usuario indicó "la carpeta RAR_V1". Si está en dev/RAR_V1:
            rar_path = os.path.join(os.path.dirname(ROOT_DIR), "RAR_V1") # c:\dev\RAR_V1
            
            if os.path.exists(rar_path):
                print(f"[+] Agregando carpeta RAR_V1...")
                for root, dirs, files in os.walk(rar_path):
                    # Ignorar venv, git, pycache
                    if '.venv' in root or '.git' in root or '__pycache__' in root:
                        continue
                        
                    for file in files:
                        if file.endswith('.pyc') or file.endswith('.log'):
                            continue
                            
                        file_path = os.path.join(root, file)
                        arcname = os.path.join("RAR_V1", os.path.relpath(file_path, rar_path))
                        zipf.write(file_path, arcname=arcname)
            else:
                print(f"[!] ALERTA: Carpeta RAR_V1 no encontrada en {rar_path}")

        print(f"--- [EXITO] Respaldo completado en: {zip_path} ---")
        
    except Exception as e:
        print(f"--- [ERROR] Falla en respaldo: {e} ---")

if __name__ == "__main__":
    crear_respaldo()
