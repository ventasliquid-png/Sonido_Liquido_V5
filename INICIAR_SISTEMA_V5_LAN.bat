@echo off
TITLE HAWE V5 - LAN MODE
ECHO ===============================================
ECHO  INICIANDO HAWE V5 - MODO LAN (ACCESO REMOTO)
ECHO ===============================================
REM Navega al directorio donde reside este script
cd /d "%~dp0"
ECHO Ejecutando lanzador universal...
python scripts\run_lan.py
if %ERRORLEVEL% NEQ 0 (
    ECHO ❌ Error al iniciar el sistema.
    pause
)
