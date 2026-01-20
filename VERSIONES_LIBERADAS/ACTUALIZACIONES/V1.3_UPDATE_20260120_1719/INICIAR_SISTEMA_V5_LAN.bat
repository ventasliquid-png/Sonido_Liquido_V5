@echo off
TITLE HAWE V5 - LAN MODE
ECHO ===============================================
ECHO  INICIANDO HAWE V5 - MODO LAN (ACCESO REMOTO)
ECHO ===============================================
REM Asegura que el contexto de ejecución sea la raíz del proyecto
C:
cd "C:\dev\Sonido_Liquido_V5"
ECHO Ejecutando lanzador universal...
python scripts\run_lan.py
if %ERRORLEVEL% NEQ 0 (
    ECHO ❌ Error al iniciar el sistema.
    pause
)
