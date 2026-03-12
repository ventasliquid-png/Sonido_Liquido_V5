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
start "GY BACKEND (Uvicorn)" cmd /k "IF EXIST backend\venv\Scripts\activate.bat (call backend\venv\Scripts\activate.bat) & python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [3/3] Lanzando Frontend en ventana aislada...
cd frontend
start "GY FRONTEND (Vite)" cmd /k "npm run dev -- --port 5173"

echo.
echo [SISTEMA DESPLEGADO]
echo - Se han abierto 2 ventanas negras nuevas.
echo - NO las cierres mientras trabajes.
echo - El navegador se abrira en 5 segundos...
timeout /t 5
start http://localhost:5173

exit
