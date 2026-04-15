@echo off
TITLE V5-SL :: PRODUCCION SOBERANA
color 0E
cd /d "C:\dev\V5-LS"

echo ==================================================
echo   SONIDO LIQUIDO V5 - PRODUCCION
echo   Levantando servidor para Tomy y acceso local
echo ==================================================
echo.

:: 1. Entorno virtual
echo [!] Activando entorno...
IF EXIST current\backend\venv\Scripts\activate.bat (
    call current\backend\venv\Scripts\activate.bat
) ELSE (
    echo [WARN] venv no encontrado. Usando Python global.
)

:: 2. Motor API en 8090 (accesible por red)
echo [!] Iniciando backend en puerto 8090...
start "Backend_Produccion_8090" /min cmd /k "cd /d "C:\dev\V5-LS\current" && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8090"

:: 3. Gracia para que levante
echo [!] Esperando estabilizacion...
timeout /t 5 /nobreak > nul

:: 4. Abrir browser local
echo [!] Abriendo sistema...
start http://localhost:8090

echo.
echo ==================================================
echo   Acceso local  : http://localhost:8090
echo   Acceso Tomy   : http://192.168.0.34:8090
echo ==================================================
echo   No cierres esta ventana (mata el servidor).
echo.
pause
