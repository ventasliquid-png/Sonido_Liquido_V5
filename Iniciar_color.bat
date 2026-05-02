@echo off
TITLE GY - V5 DESARROLLO (LOCAL) - PESTAÑA MULTICOLOR
color 0B

echo ==================================================
echo   LANZADOR DESARROLLO V5 (SONIDO_LIQUIDO_V5)
echo   Puerto Frontend: 5173 ^| Puerto Backend: 8080
echo ==================================================
echo.
echo [1/3] Detectando entorno...
cd /d "%~dp0"

echo [2/3] Lanzando Backend (Desarrollo) en ventana aislada...
start "GY BACKEND D (8080)" cmd /k "color 4F & echo ========================================== & echo   BACKEND DESARROLLO - Puerto 8080 & echo ========================================== & IF EXIST backend\venv\Scripts\activate.bat (call backend\venv\Scripts\activate.bat) & python -m uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload"

echo [3/3] Lanzando Frontend (Desarrollo) en ventana aislada...
cd frontend
start "GY FRONTEND D (5173)" cmd /k "color 2F & echo ========================================== & echo   FRONTEND DESARROLLO - Puerto 5173 & echo ========================================== & npm run dev -- --port 5173"

echo.
echo [SISTEMA DESPLEGADO - DESARROLLO]
echo - BACKEND: ventana ROJA (8080)
echo - FRONTEND: ventana VERDE (5173)
echo - El navegador se abrira en 10 segundos...
timeout /t 10
start http://localhost:5173

exit