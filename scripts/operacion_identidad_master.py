import os

RELEASE_DIR = r'C:\dev\V5_RELEASE_09'
OLD_DB = 'pilot_v5x.db'
NEW_DB = 'V5_LS_MASTER.db'

def operacion_identidad_master():
    print(f"\n--- INICIANDO OPERACIÓN IDENTIDAD MASTER (V5-LS) ---")
    print(f"[*] Objetivo: Migrar referencias de {OLD_DB} a {NEW_DB}")

    extensions = ('.js', '.css', '.html', '.py', '.bat', '.env', '.json', '.txt', '.log')
    
    count = 0
    for root, dirs, files in os.walk(RELEASE_DIR):
        for file in files:
            if file.endswith(extensions):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 1. Reemplazo de base de datos
                    new_content = content.replace(OLD_DB, NEW_DB)
                    new_content = new_content.replace('pilot_v5x', 'V5_LS_MASTER')
                    
                    if content != new_content:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        count += 1
                except Exception as e:
                    pass

    print(f"\n[CERTIFICACIÓN] {count} archivos sintonizados con la Identidad MASTER.")

    # 4. Actualizar .env explícitamente
    env_path = os.path.join(RELEASE_DIR, '.env')
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f"DATABASE_URL=sqlite:///{NEW_DB}\n")
            f.write("PORT=8090\n")
            f.write("HOST=0.0.0.0\n")
            f.write("ENABLE_AI=True\n")
        print("[OK] Archivo .env actualizado con Soberanía Master.")
    except:
        pass

    print("\n--- OPERACIÓN FINALIZADA ---")

if __name__ == "__main__":
    operacion_identidad_master()
