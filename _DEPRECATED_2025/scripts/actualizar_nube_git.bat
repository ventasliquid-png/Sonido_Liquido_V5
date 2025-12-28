@echo off
ECHO ===============================================
ECHO  GUARDANDO Y ENVIANDO CAMBIOS AL REPOSITORIO
ECHO ===============================================

REM Navega al directorio raíz del proyecto
cd /d "%%~dp0\.."

ECHO 1. Preparando todos los archivos (git add .)
git add .
echo.

set /p commit_message="--> Ingresa el mensaje para el commit y presiona Enter: "
echo.
ECHO 2. Guardando cambios locales (git commit)
git commit -m "%%commit_message%%"
echo.

ECHO 3. Enviando cambios a la nube (git push)
git push
echo.
echo.
ECHO *** SINCRONIZACION FINALIZADA ***
echo.
pause
