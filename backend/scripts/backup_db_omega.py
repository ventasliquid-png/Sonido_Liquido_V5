
import shutil
import os
from datetime import datetime

source = "c:\\dev\\Sonido_Liquido_V5\\pilot.db"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
# Simulamos "Drive" creando una carpeta de backups segura si no existe
backup_dir = "c:\\dev\\Sonido_Liquido_V5\\_BACKUPS" 
os.makedirs(backup_dir, exist_ok=True)

dest = os.path.join(backup_dir, f"pilot_backup_{timestamp}.db")

try:
    shutil.copy2(source, dest)
    print(f"Backup exitoso: {dest}")
except Exception as e:
    print(f"Error en backup: {e}")
