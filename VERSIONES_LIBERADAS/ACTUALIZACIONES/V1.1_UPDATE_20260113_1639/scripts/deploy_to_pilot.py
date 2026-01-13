import os
import shutil
import subprocess
import sys

# Configuración
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
PILOT_DIR = os.path.join(PROJECT_ROOT, "BUILD_PILOTO")
PILOT_BACKEND = os.path.join(PILOT_DIR, "backend")
PILOT_STATIC = os.path.join(PILOT_DIR, "static")

def print_step(msg):
    print(f"\n>>> {msg}")

def main():
    print_step("INICIANDO DESPLIEGUE A PILOTO (Local LAN)")
    
    # 1. Build Frontend
    print_step("Compilando Frontend (Vue/Vite)...")
    if not os.path.exists(os.path.join(FRONTEND_DIR, "node_modules")):
        print("Error: node_modules no encontrado. Ejecuta 'npm install' en frontend primero.")
        return

    # Ejecutar npm run build
    try:
        subprocess.check_call(["npm.cmd", "run", "build"], cwd=FRONTEND_DIR, shell=True)
    except subprocess.CalledProcessError:
        print("❌ Error en compilación de Frontend.")
        return

    # 2. Limpiar Destino (Parcialmente)
    print_step("Limpiando directorio destino...")
    if os.path.exists(PILOT_BACKEND):
        shutil.rmtree(PILOT_BACKEND)
    if os.path.exists(PILOT_STATIC):
        shutil.rmtree(PILOT_STATIC)
    
    # No borramos PILOT_DIR entero para no borrar la DB (produccion.db) ni la carpeta data
    os.makedirs(PILOT_BACKEND, exist_ok=True)
    os.makedirs(PILOT_STATIC, exist_ok=True)

    # 3. Copiar Backend
    print_step("Copiando Backend...")
    # Copiamos todo 'backend' recursivamente
    shutil.copytree(BACKEND_DIR, PILOT_BACKEND, dirs_exist_ok=True)
    
    # Copiar archivos raíz necesarios
    files_to_copy = ["requirements.txt", ".google_credentials", "ARQUITECTURA_Y_DOCTRINA_V5.md"]
    for f in files_to_copy:
        src = os.path.join(PROJECT_ROOT, f)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(PILOT_DIR, f))

    # 4. Copiar Frontend (Dist -> Static)
    print_step("Instalando Frontend en Servidor...")
    dist_dir = os.path.join(FRONTEND_DIR, "dist")
    shutil.copytree(dist_dir, PILOT_STATIC, dirs_exist_ok=True)

    # 5. Crear Script de Arranque
    print_step("Generando launcher...")
    launcher_content = """@echo off
echo --- INICIANDO SERVIDOR PILOTO V5 (IP CENTRAL) ---
echo Para acceder desde otra PC, usa la IP de esta maquina + :8000
echo Ejemplo: http://192.168.1.55:8000
echo ------------------------------------------------
cd /d "%~dp0"
call venv\\Scripts\\activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
"""
    with open(os.path.join(PILOT_DIR, "INICIAR_SISTEMA.bat"), "w") as f:
        f.write(launcher_content)

    print_step(f"✅ DESPLIEGUE EXITOSO en: {PILOT_DIR}")
    print("Recuerda crear el venv en la carpeta piloto si no existe:")
    print(f"cd {PILOT_DIR} && python -m venv venv && venv\\Scripts\\pip install -r requirements.txt")

if __name__ == "__main__":
    main()
