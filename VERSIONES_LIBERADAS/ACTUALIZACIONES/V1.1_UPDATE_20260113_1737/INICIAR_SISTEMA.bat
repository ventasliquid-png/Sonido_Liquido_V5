@echo off
chcp 65001 > nul
title SONIDO LIQUIDO V5 - LAUNCHER
echo ------------------------------------------------------------------
echo            INICIANDO SISTEMA TACTICO INTEGRAL
echo ------------------------------------------------------------------

set "BACKEND_HOST=0.0.0.0"
set "BACKEND_PORT=8000"

echo [1/2] Levantando Backend (Puerto %BACKEND_PORT%)...
start "BACKEND V5" cmd /k "python -m uvicorn backend.main:app --host %BACKEND_HOST% --port %BACKEND_PORT% --reload"

echo [2/2] Levantando Frontend (Puerto 5173)...
cd frontend
start "FRONTEND V5" cmd /k "npm run dev -- --host"
cd ..

echo.
echo [SISTEMA INICIADO]
echo -- Backend corriendo en segundo plano.
echo -- Frontend corriendo en segundo plano.
echo.
echo Espere unos segundos y abra: http://localhost:5173
echo.
echo (No cierre las ventanas negras que aparecieron)
echo.
pause
