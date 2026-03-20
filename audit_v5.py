import os
import time
from datetime import datetime, timedelta

def audit_physical_changes(root_dir, hours=12):
    """
    Tracks physical file changes in the last X hours.
    Ignores system directories (.git, venv, node_modules, __pycache__).
    """
    ignored_dirs = {'.git', 'venv', 'node_modules', '__pycache__', '.next', 'dist', '.idea', '.vscode'}
    cutoff_time = time.time() - (hours * 3600)
    
    changed_files = []
    
    print(f"--- [HALCON V5] AUDITORIA FISICA (Ultimas {hours} horas) ---")
    print(f"Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    for root, dirs, files in os.walk(root_dir):
        # In-place directory filtering
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                mtime = os.path.getmtime(file_path)
                if mtime > cutoff_time:
                    relative_path = os.path.relpath(file_path, root_dir)
                    # Ignore the audit output itself and common logs if needed
                    if relative_path in ['audit_v5.py', 'audit_results.txt']:
                        continue
                    
                    mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                    changed_files.append((relative_path, mtime_str))
            except (OSError, PermissionError):
                continue

    if not changed_files:
        print("OK: No se detectaron cambios fisicos fuera de Git.")
    else:
        print(f"ALERTA: Se detectaron {len(changed_files)} archivos modificados:")
        for path, mtime in sorted(changed_files):
            print(f" [!] {mtime} | {path}")
            
    print("-" * 50)
    return changed_files

if __name__ == "__main__":
    current_dir = os.getcwd()
    audit_physical_changes(current_dir)
