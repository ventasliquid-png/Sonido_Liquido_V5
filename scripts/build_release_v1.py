import os
import shutil
import zipfile
import subprocess
from datetime import datetime

# CONFIGURATION
ROOT_DIR = "c:\\dev\\Sonido_Liquido_V5"
STAGING_DIR = os.path.join(ROOT_DIR, "_SISTEMA_INTERNO")
ZIP_NAME = "Sonido_Liquido_V5_Instalador_v1.0.zip"
ZIP_PATH = os.path.join(ROOT_DIR, ZIP_NAME)

# CONTENT DEFINITIONS

TXT_LEER_ANTES = """¡ALTO! LEA ESTO PARA NO PERDER DATOS.

1. Si usa WINDOWS: Haga doble clic en el archivo [ 2_INSTALAR_WINDOWS.bat ].
2. Si usa MAC/LINUX: Ejecute el archivo [ 3_INSTALAR_MAC_LINUX.sh ].

IMPORTANTE:
Al finalizar la instalación, se abrirá una ventana pidiéndole que elija una carpeta.
DEBE SELECCIONAR SU CARPETA DE GOOGLE DRIVE.
Si no lo hace, el sistema funcionará pero NO HARÁ COPIAS DE SEGURIDAD."""

TXT_CC6 = """SI TIENES UN ERROR Y NO ENTIENDES QUÉ PASA:
1. Copia el mensaje de error.
2. Abre Gemini (tienes el icono en el escritorio).
3. Pega este mensaje secreto y luego el error:

"Sos CC6, una IA veterana y pragmática. Tu misión es protegerme a mí (Tomás), el operador.
No tengo conocimientos técnicos. Traducime qué pasó en lenguaje humano para que no me asuste,
y redactame un informe técnico preciso para que yo se lo mande a Carlos.
Tu lealtad es conmigo."
"""

BAT_INSTALLER = r"""@echo off
setlocal EnableDelayedExpansion
title INSTALADOR SONIDO LIQUIDO V5 - OPERACION INDEPENDENCIA

echo ========================================================================
echo        SONIDO LIQUIDO V5 - INSTALADOR AUTOMATICO (WINDOWS)
echo ========================================================================
echo.
echo [PASO 1/4] Creando directorio del sistema (C:\SL_SYSTEM)...
if not exist "C:\SL_SYSTEM" mkdir "C:\SL_SYSTEM"

echo [PASO 2/4] Copiando archivos del sistema...
xcopy "_SISTEMA_INTERNO\*" "C:\SL_SYSTEM\" /E /I /H /Y /Q

echo [PASO 3/4] Creando accesos directos...
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\INICIAR_SISTEMA.lnk');$s.TargetPath='C:\SL_SYSTEM\INICIAR_SISTEMA.bat';$s.Save()"
powershell "$s=(New-Object -COM WScript.Shell).CreateShortcut('%USERPROFILE%\Desktop\SOPORTE IA (HAWE).lnk');$s.TargetPath='https://gemini.google.com/app';$s.Save()"

echo [PASO 4/4] CONFIGURACION DE RESPALDO (NUBE)
echo.
echo ************************************************************************
echo  ATENCION: Se abrira una ventana.
echo  SELECCIONE SU CARPETA DE GOOGLE DRIVE PARA LOS RESPALDOS.
echo ************************************************************************
echo.
pause

REM GUI MAGICA: FolderBrowserDialog via PowerShell
for /f "usebackq tokens=*" %%A in (`powershell -Command "Add-Type -AssemblyName System.Windows.Forms; $f = New-Object System.Windows.Forms.FolderBrowserDialog; $f.Description = 'SELECCIONE SU CARPETA DE GOOGLE DRIVE PARA BACKUPS'; $f.ShowNewFolderButton = $true; if($f.ShowDialog() -eq 'OK'){ echo $f.SelectedPath }"`) do set "CHOSEN_PATH=%%A"

if "%CHOSEN_PATH%"=="" (
    echo [ADVERTENCIA] No selecciono ninguna carpeta. El respaldo automatico NO funcionara.
    set "CHOSEN_PATH=C:\Respaldos_Locales_SL"
)

echo Ruta seleccionada: "%CHOSEN_PATH%"

REM Escribir en .env
echo. >> "C:\SL_SYSTEM\.env"
echo # CONFIGURACION AUTOMATICA DE INSTALADOR >> "C:\SL_SYSTEM\.env"
echo PATH_DRIVE_BACKUP=%CHOSEN_PATH% >> "C:\SL_SYSTEM\.env"

echo.
echo ========================================================================
echo        INSTALACION COMPLETADA CON EXITO PRO
echo ========================================================================
echo.
echo Ya puede cerrar esta ventana y usar el icono INICIAR_SISTEMA en su escritorio.
echo.
pause
"""

SH_INSTALLER = """#!/bin/bash
echo "========================================================================"
echo "       SONIDO LIQUIDO V5 - INSTALADOR AUTOMATICO (MAC/LINUX)"
echo "========================================================================"

TARGET_DIR="$HOME/SL_SYSTEM"

echo "[PASO 1/3] Creando directorio del sistema ($TARGET_DIR)..."
mkdir -p "$TARGET_DIR"

echo "[PASO 2/3] Copiando archivos..."
cp -r _SISTEMA_INTERNO/* "$TARGET_DIR/"
chmod +x "$TARGET_DIR/"*.sh
chmod +x "$TARGET_DIR/"*.bat

echo "[PASO 3/3] CONFIGURACION DE RESPALDO (NUBE)"
echo "Seleccione su carpeta de Google Drive..."

OS="$(uname)"
CHOSEN_PATH=""

if [ "$OS" = "Darwin" ]; then
    # MAC OS GUI
    CHOSEN_PATH=$(osascript -e 'tell application "System Events" to return POSIX path of (choose folder with prompt "SELECCIONE SU CARPETA DE GOOGLE DRIVE PARA BACKUPS")')
else
    # LINUX GUI (Intentar zenity o kdialog, fallback a consola)
    if command -v zenity &> /dev/null; then
        CHOSEN_PATH=$(zenity --file-selection --directory --title="SELECCIONE SU CARPETA DE GOOGLE DRIVE PARA BACKUPS")
    elif command -v kdialog &> /dev/null; then
        CHOSEN_PATH=$(kdialog --getexistingdirectory)
    else
        echo "No se detectó GUI. Por favor ingrese la ruta completa a su carpeta de Drive:"
        read CHOSEN_PATH
    fi
fi

if [ -z "$CHOSEN_PATH" ]; then
    echo "[ADVERTENCIA] No selecciono ninguna carpeta. Usando local."
    CHOSEN_PATH="$HOME/Respaldos_Locales_SL"
fi

echo "Ruta seleccionada: $CHOSEN_PATH"

# Escribir en .env
echo "" >> "$TARGET_DIR/.env"
echo "# CONFIGURACION AUTOMATICA DE INSTALADOR" >> "$TARGET_DIR/.env"
echo "PATH_DRIVE_BACKUP=$CHOSEN_PATH" >> "$TARGET_DIR/.env"

echo ""
echo "========================================================================"
echo "       INSTALACION COMPLETADA"
echo "========================================================================"
echo "Ejecute el sistema desde $TARGET_DIR"
"""

def ignore_patterns(path, names):
    ignored = []
    if "backend" in path:
        ignored.extend([n for n in names if n in ['venv', '__pycache__', '.git', '.pytest_cache', 'pilot_vacio_backup.db']])
    if "frontend" in path:
        ignored.extend([n for n in names if n in ['node_modules', '.git', 'dist', '.vscode']])
    return ignored

def main():
    print(f"--- INICIO OPERACION INDEPENDENCIA: {datetime.now()} ---")
    
    # 1. CLEANUP PREVIO
    if os.path.exists(STAGING_DIR):
        shutil.rmtree(STAGING_DIR)
    
    # 2. STAGING
    print(f"Creating Staging Directory: {STAGING_DIR}")
    os.makedirs(STAGING_DIR)
    
    # Copy Backend
    print("Copying Backend...")
    shutil.copytree(os.path.join(ROOT_DIR, "backend"), os.path.join(STAGING_DIR, "backend"), ignore=ignore_patterns)
    
    # Copy Frontend
    print("Copying Frontend...")
    shutil.copytree(os.path.join(ROOT_DIR, "frontend"), os.path.join(STAGING_DIR, "frontend"), ignore=ignore_patterns)
    
    # Copy DB (Active)
    print("Copying pilot.db...")
    shutil.copy2(os.path.join(ROOT_DIR, "pilot.db"), os.path.join(STAGING_DIR, "pilot.db"))

    # Copy Docs
    print("Copying Docs...")
    if os.path.exists(os.path.join(ROOT_DIR, "MANUAL_TECNICO_V5.md")):
        shutil.copy2(os.path.join(ROOT_DIR, "MANUAL_TECNICO_V5.md"), os.path.join(STAGING_DIR, "MANUAL_TECNICO_V5.md"))
        
    # Create .env template
    print("Creating .env template...")
    # Leer .env original pero limpiar valores sensibles si fuera necesario. En este caso copiamos estructura básica.
    # Mejor copiamos el .env actual, ya que tiene las configs correctas para el usuario final (excepto el path de backup que se sobrescribira)
    shutil.copy2(os.path.join(ROOT_DIR, ".env"), os.path.join(STAGING_DIR, ".env"))

    # Copy Launch Scripts
    print("Copying Launch Scripts...")
    # Assuming start scripts are needed inside system
    # If they are in root, copy them. If not, create dummies.
    # User mentioned INICIAR_SISTEMA.bat in root.
    if os.path.exists(os.path.join(ROOT_DIR, "INICIAR_SISTEMA.bat")):
        shutil.copy2(os.path.join(ROOT_DIR, "INICIAR_SISTEMA.bat"), os.path.join(STAGING_DIR, "INICIAR_SISTEMA.bat"))
    
    if os.path.exists(os.path.join(ROOT_DIR, "INSTALAR_DEPENDENCIAS.bat")):
        shutil.copy2(os.path.join(ROOT_DIR, "INSTALAR_DEPENDENCIAS.bat"), os.path.join(STAGING_DIR, "INSTALAR_DEPENDENCIAS.bat"))

    # 3. ROOT ARTIFACTS
    print("Creating Root Artifacts...")
    
    with open(os.path.join(ROOT_DIR, "1_LEER_ANTES_DE_TOCAR.txt"), "w", encoding="utf-8") as f:
        f.write(TXT_LEER_ANTES)
        
    with open(os.path.join(ROOT_DIR, "2_INSTALAR_WINDOWS.bat"), "w", encoding="latin-1") as f: # Batches often prefer ANSI/latin-1
        f.write(BAT_INSTALLER)
        
    with open(os.path.join(ROOT_DIR, "3_INSTALAR_MAC_LINUX.sh"), "w", encoding="utf-8") as f:
        f.write(SH_INSTALLER.replace('\r\n', '\n')) # Ensure unix line endings

    with open(os.path.join(ROOT_DIR, "INVOCAR_CC6.txt"), "w", encoding="utf-8") as f:
        f.write(TXT_CC6)

    # 4. PACKAGING
    print(f"Zipping to {ZIP_PATH}...")
    with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add Root Artifacts
        artifacts = ["1_LEER_ANTES_DE_TOCAR.txt", "2_INSTALAR_WINDOWS.bat", "3_INSTALAR_MAC_LINUX.sh", "INVOCAR_CC6.txt"]
        for art in artifacts:
            zipf.write(os.path.join(ROOT_DIR, art), arcname=art)
            
        # Add Staging Inner System
        for root, dirs, files in os.walk(STAGING_DIR):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, STAGING_DIR) # Inside zip it should start with _SISTEMA_INTERNO
                zipf.write(abs_path, arcname=os.path.join("_SISTEMA_INTERNO", rel_path))

    # 5. CLEANUP
    print("Cleaning up Staging...")
    shutil.rmtree(STAGING_DIR)
    
    print("Cleaning up Artifacts from Root (they are in zip now)...")
    for art in artifacts:
        os.remove(os.path.join(ROOT_DIR, art))
        
    print("Cleaning up Trash...")
    trash_files = ["pilot_contrabando.dat"]
    for t in trash_files:
        p = os.path.join(ROOT_DIR, t)
        if os.path.exists(p):
            os.remove(p)
            print(f"Removed {t}")
            
    # Clean .bak
    for file in os.listdir(ROOT_DIR):
        if file.endswith(".bak"):
            os.remove(os.path.join(ROOT_DIR, file))

    print(f"--- DONE. ZIP Created at: {ZIP_PATH} ---")

if __name__ == "__main__":
    main()
