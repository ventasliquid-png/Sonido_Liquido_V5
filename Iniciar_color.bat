@echo off
TITLE GY - LANZADOR ESTRATEGICO (WINDOWS 11 COMPATIBLE)
color 0B

echo ==================================================
echo   LANZADOR DIVIDIDO V5 (ANTI-CRASH WIN11)
echo ==================================================
echo.
echo [1/3] Detectando entorno...
cd /d "%~dp0"

echo [2/3] Lanzando Backend en ventana aislada...
start "GY BACKEND (Uvicorn)" cmd /k "color 4F & echo ========================================== & echo   BACKEND - Uvicorn (Puerto 8080) & echo ========================================== & IF EXIST backend\venv\Scripts\activate.bat (call backend\venv\Scripts\activate.bat) & python -m uvicorn backend.main:app --host 0.0.0.0 --port 8080 --reload"

echo [3/3] Lanzando Frontend en ventana aislada...
cd frontend
start "GY FRONTEND (Vite)" cmd /k "color 2F & echo ========================================== & echo   FRONTEND - Vite (Puerto 5173) & echo ========================================== & npm run dev -- --port 5173"

echo.
echo [SISTEMA DESPLEGADO]
echo - BACKEND: ventana ROJA
echo - FRONTEND: ventana VERDE
echo - NO las cierres mientras trabajes.
echo - El navegador se abrira en 5 segundos...
timeout /t 5
start http://localhost:5173

exit