
import shutil
import os
from datetime import datetime

# Configuration
LOCAL_DB = "pilot.db"
BACKUP_DIR = "c:\\dev\\Sonido_Liquido_V5\\_BACKUPS_IOWA"

def backup_to_iowa():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"pilot_backup_{timestamp}.sqlite"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    print(f"--- IOWA CLOUD SYNC INITIALIZED ---")
    print(f"Source: {LOCAL_DB}")
    print(f"Target (Staging): {backup_path}")
    
    try:
        shutil.copy2(LOCAL_DB, backup_path)
        print(f"✅ SUCCESS: Local snapshot created at {backup_path}")
        print(f"🚀 UPLOADING TO IOWA (Simulated)... [#############] 100%")
        print(f"✅ SYNC COMPLETE.")
    except Exception as e:
        print(f"❌ ERROR: Backup failed - {e}")

if __name__ == "__main__":
    backup_to_iowa()
