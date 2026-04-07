import os
import time

VERSION = "V5.6 GOLD"
TIMESTAMP = time.strftime("%Y%m%d%H%M%S")
HEADER_TEMPLATE = """# [IDENTIDAD] - {rel_path}
# Versión: {version} | Sincronización: {timestamp}
# ---------------------------------------------------------
"""

JS_HEADER_TEMPLATE = """// [IDENTIDAD] - {rel_path}
// Versión: {version} | Sincronización: {timestamp}
// ------------------------------------------
"""

DIRECTORIES = [
    "backend/admin", "backend/agenda", "backend/auth", "backend/clientes",
    "backend/logistica", "backend/maestros", "backend/pedidos",
    "frontend/src/views", "frontend/src/services", "frontend/src/stores",
    "frontend/src/composables", "frontend/src/router"
]

def inject_header(file_path, rel_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Determine header style
    if file_path.endswith('.py'):
        header = HEADER_TEMPLATE.format(rel_path=rel_path, version=VERSION, timestamp=TIMESTAMP)
    elif file_path.endswith('.js') or file_path.endswith('.vue'):
        header = JS_HEADER_TEMPLATE.format(rel_path=rel_path, version=VERSION, timestamp=TIMESTAMP)
    else:
        return False

    # Avoid double injection
    if "[IDENTIDAD]" in content[:200]:
        # Update existing header (we could replace it, but let's just skip for now to be safe)
        print(f" [!] Skipping (already has identity): {rel_path}")
        return False

    # Check for shebang
    if content.startswith("#!"):
        lines = content.splitlines()
        lines.insert(1, header)
        new_content = "\n".join(lines)
    else:
        new_content = header + "\n" + content

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    print(f"=== INYECCIÓN DE PROTOCOLO DE IDENTIDAD: {VERSION} ===")
    count = 0
    for base_dir in DIRECTORIES:
        if not os.path.exists(base_dir):
            print(f" [?] Skipping missing directory: {base_dir}")
            continue
            
        for root, dirs, files in os.walk(base_dir):
            if "__pycache__" in root: continue
            
            for f in files:
                if f.endswith(('.py', '.js', '.vue')):
                    file_path = os.path.join(root, f)
                    rel_path = os.path.relpath(file_path, ".")
                    if inject_header(file_path, rel_path):
                        print(f" [+] Inyectado: {rel_path}")
                        count += 1

    print(f"\n[DONE] Identidad inyectada con éxito en {count} archivos.")

if __name__ == "__main__":
    main()
