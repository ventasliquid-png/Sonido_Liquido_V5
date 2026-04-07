import os
import shutil
from datetime import datetime

# Configuration
ARCHIVE_NAME = "_ARCHIVE_2026_04_07"
ROOT_DIR = "."
CORE_FILES = {
    "pilot_v5x.db", "V5_LS_MASTER.db", ".env", ".gitignore", "requirements.txt",
    "ALFA.md", "BITACORA_DEV.md", "CLAUDE.md", "manual.pdf", "README.md",
    "SESION_ACTUAL.md", "task.md", "implementation_plan.md", "walkthrough.md"
}
EXTENSIONS_TO_ARCHIVE = {".pdf", ".xlsx", ".zip", ".csv", ".log"}
PREFIXES_TO_ARCHIVE = {"test_", "fc ", "debug_output", "Gemini-", "client_debug"}

def sanitize():
    if not os.path.exists(ARCHIVE_NAME):
        os.makedirs(ARCHIVE_NAME)
        print(f"[*] Created archive folder: {ARCHIVE_NAME}")

    moved_count = 0
    for filename in os.listdir(ROOT_DIR):
        if filename in CORE_FILES:
            continue
        
        filepath = os.path.join(ROOT_DIR, filename)
        if not os.path.isfile(filepath):
            continue

        base, ext = os.path.splitext(filename)
        ext = ext.lower()

        should_archive = False
        if ext in EXTENSIONS_TO_ARCHIVE:
            should_archive = True
        if any(filename.startswith(prefix) for prefix in PREFIXES_TO_ARCHIVE):
            should_archive = True
        
        # Specific files mentioned in previous sessions for cleanup
        if filename in ["mapa_sistema.txt", "mapa_tactico_v5.txt", "current_git_status.txt"]:
            should_archive = True

        if should_archive:
            try:
                dest = os.path.join(ARCHIVE_NAME, filename)
                # Handle duplicates if any
                if os.path.exists(dest):
                    timestamp = datetime.now().strftime("%H%M%S")
                    dest = os.path.join(ARCHIVE_NAME, f"{base}_{timestamp}{ext}")
                
                shutil.move(filepath, dest)
                print(f"[+] Moved: {filename} -> {ARCHIVE_NAME}")
                moved_count += 1
            except Exception as e:
                print(f"[!] Error moving {filename}: {e}")

    print(f"\n[DONE] Sanitization complete. Total files moved: {moved_count}")

if __name__ == "__main__":
    sanitize()
