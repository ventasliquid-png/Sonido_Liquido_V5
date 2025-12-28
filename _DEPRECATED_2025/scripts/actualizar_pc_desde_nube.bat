@echo off
ECHO ===============================================
ECHO  ACTUALIZANDO PC DESDE EL REPOSITORIO (NUBE)
ECHO ===============================================

REM Navega al directorio raíz del proyecto
cd /d "%%~dp0\.."

ECHO Trayendo cambios desde la nube (git pull)
git pull
echo.
echo.
ECHO *** ACTUALIZACION FINALIZADA ***
echo.
pause
