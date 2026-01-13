import shutil
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load Env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / "backend" / ".env")

class BackupManager:
    @staticmethod
    def get_backup_path():
        """
        Determina la ruta de destino.
        Prioridad: 
        1. Env Var PATH_DRIVE_BACKUP (Google Drive)
        2. Local /backups
        """
        drive_path = os.getenv("PATH_DRIVE_BACKUP")
        if drive_path and os.path.exists(drive_path):
            return Path(drive_path)
            
        # Fallback local
        local_path = BASE_DIR / "backups"
        local_path.mkdir(exist_ok=True)
        return local_path

    @staticmethod
    def perform_backup(prefix: str = "auto", silent: bool = False) -> str:
        """
        Ejecuta la copia de seguridad de pilot.db.
        Returns: Ruta del archivo generado.
        """
        try:
            source_db = BASE_DIR / "pilot.db"
            if not source_db.exists():
                if not silent: print("❌ pilot.db no encontrado.")
                return None
                
            dest_folder = BackupManager.get_backup_path()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_{prefix}_{timestamp}.db"
            dest_file = dest_folder / filename
            
            shutil.copy2(source_db, dest_file)
            
            if not silent:
                print(f"✅ Backup exitoso: {filename} -> {dest_folder}")
                
            return str(dest_file)
            
        except Exception as e:
            if not silent:
                print(f"❌ Error en Backup: {e}")
            return None

class SessionCounter:
    SESSION_FILE = BASE_DIR / "session_counter.json"
    
    @staticmethod
    def check_and_increment():
        """
        Lee el contador. Si es < 4, incrementa.
        Si es >= 4, ejecuta Backup y resetea A 1.
        """
        import json
        
        count = 0
        try:
            if SessionCounter.SESSION_FILE.exists():
                with open(SessionCounter.SESSION_FILE, "r") as f:
                    data = json.load(f)
                    count = data.get("count", 0)
        except:
            count = 0
            
        count += 1
        triggered = False
        
        if count >= 4:
            BackupManager.perform_backup(prefix="session_rule_4_6", silent=True)
            count = 0 # Reset (or 1?) Rule says "every 4". Let's reset to 0 so next is 1.
            triggered = True
            
        # Save
        try:
            with open(SessionCounter.SESSION_FILE, "w") as f:
                json.dump({"count": count}, f)
        except:
            pass
            
        return triggered, count
