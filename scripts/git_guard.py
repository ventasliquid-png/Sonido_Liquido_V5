import subprocess
import sys

def get_staged_files_count():
    try:
        # git diff --cached --name-only devuelve los archivos en staging
        output = subprocess.check_output(["git", "diff", "--cached", "--name-only"], stderr=subprocess.STDOUT).decode("utf-8")
        files = [line for line in output.split("\n") if line.strip()]
        return len(files), files
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar git diff: {e.output.decode('utf-8')}")
        return -1, []

def main():
    print("========================================================")
    print("       GIT GUARD V1.0 - REGLA DE ORO (MÁX 100)")
    print("========================================================")
    
    count, files = get_staged_files_count()
    
    if count == -1:
        sys.exit(1)
        
    print(f"[*] Archivos en Staging: {count}")
    
    if count > 100:
        print(f"\n[!] 🔴 ALERTA DE SEGURIDAD: Se detectaron {count} archivos para commit.")
        print("[!] Esto excede la Regla de Oro (máximo 100 archivos).")
        print("[!] POSIBLE ERROR: ¿Estás intentando subir node_modules o binarios?")
        print("\n[!] ACCIÓN REQUERIDA: Revisá tu .gitignore y ejecutá 'git rm -r --cached .'")
        print("[!] EL COMMIT QUEDA BLOQUEADO hasta autorización humana.")
        sys.exit(1)
    elif count == 0:
        print("[?] No hay archivos en Staging para el commit.")
    else:
        print(f"[OK] 🟢 DENTRO DEL LÍMITE: {count}/100 archivos.")
        print("[*] Procediendo con normalidad.")

if __name__ == "__main__":
    main()
