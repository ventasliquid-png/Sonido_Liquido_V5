@echo off
echo ===================================================
echo   SISTEMA SONIDO LIQUIDO V5 - INICIANDO PILOTO
echo ===================================================
echo.
echo [1/3] Verificando entorno...
if not exist "venv" (
    echo [ERROR] No se detecta entorno virtual 'venv'.
    echo Ejecute este script dentro de la carpeta del sistema.
    pause
    exit
)

echo [2/3] Iniciando Backend...
call venv\Scripts\activate
start /B python backend\main.py

echo [3/3] Abriendo navegador...
timeout /t 5 >nul
start http://localhost:8000

echo.
echo SISTEMA CORRIENDO. NO CIERRE ESTA VENTANA.
echo Para detener presione Ctrl+C
pause
