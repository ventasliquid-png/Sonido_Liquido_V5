
import sys
import os
from pathlib import Path

# Add backend to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from backend.cantera.service import CanteraService

if __name__ == "__main__":
    print("Forcing Cantera Sync...")
    try:
        success = CanteraService.sync_from_json()
        if success:
            print("Sync Completed Successfully.")
        else:
            print("Sync Failed.")
    except Exception as e:
        print(f"Error during sync: {e}")
