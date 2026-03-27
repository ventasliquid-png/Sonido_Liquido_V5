import os
import re

RELEASE_DIR = r'C:\dev\V5_RELEASE_09'
NEW_IP = '192.168.0.34'
NEW_BACKEND_PORT = '8090'
NEW_FRONTEND_PORT = '5174'

def operacion_autopistas_limpias():
    print(f"\n--- INICIANDO OPERACIÓN AUTOPISTAS LIMPIAS (V5-LS) ---")
    print(f"[*] Objetivo: Redirigir tráfico a {NEW_IP}:{NEW_BACKEND_PORT} / {NEW_FRONTEND_PORT}")

    # Extensiones a procesar
    extensions = ('.js', '.css', '.html', '.py', '.bat', '.env', '.json', '.txt', '.log')
    
    count = 0
    for root, dirs, files in os.walk(RELEASE_DIR):
        for file in files:
            if file.endswith(extensions):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 1. Reemplazo de puertos básicos
                    new_content = content.replace('8080', NEW_BACKEND_PORT)
                    new_content = new_content.replace('5173', NEW_FRONTEND_PORT)
                    
                    # 2. Reemplazo de URLs (localhost o 127.0.0.1 -> IP 192.168.0.34)
                    # Solo si están acompañadas del puerto 8090 (ya reemplazado)
                    new_content = new_content.replace(f'localhost:{NEW_BACKEND_PORT}', f'{NEW_IP}:{NEW_BACKEND_PORT}')
                    new_content = new_content.replace(f'127.0.0.1:{NEW_BACKEND_PORT}', f'{NEW_IP}:{NEW_BACKEND_PORT}')
                    
                    if content != new_content:
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        # print(f" [OK] {file} actualizado.")
                        count += 1
                except Exception as e:
                    # print(f" [!] Error en {file}: {e}")
                    pass

    print(f"\n[CERTIFICACIÓN] {count} archivos sintonizados con la nueva red.")

    # 3. Crear Lanzador Maestro
    bat_path = os.path.join(RELEASE_DIR, 'INICIAR_SISTEMA_V5.bat')
    bat_content = f"""@echo off
TITLE V5-LS PRODUCCION (OPERADOR TOMY)
color 0B
cd /d %~dp0
echo ==================================================
echo   SISTEMA SONIDO LIQUIDO V5 - MISION LS
echo ==================================================
echo.
echo [1/2] Iniciando Motor API (Puerto {NEW_BACKEND_PORT})...
start /b python -m uvicorn backend.main:app --host 0.0.0.0 --port {NEW_BACKEND_PORT}

echo [2/2] Iniciando Portal Web (Puerto {NEW_FRONTEND_PORT})...
start /b python -m http.server {NEW_FRONTEND_PORT} --directory static

timeout /t 5
echo [*] Accediendo a http://{NEW_IP}:{NEW_FRONTEND_PORT}
start http://{NEW_IP}:{NEW_FRONTEND_PORT}
echo.
echo [OK] Sistema Operativo. No cierre esta ventana.
pause
"""
    with open(bat_path, 'w', encoding='latin-1') as f:
        f.write(bat_content)
    print(f"[OK] Lanzador Maestro 'INICIAR_SISTEMA_V5.bat' creado.")

    print("\n--- OPERACIÓN FINALIZADA ---")

if __name__ == "__main__":
    operacion_autopistas_limpias()
