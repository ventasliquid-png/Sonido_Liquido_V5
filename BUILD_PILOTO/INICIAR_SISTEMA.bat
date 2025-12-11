@echo off
echo --- INICIANDO SERVIDOR PILOTO V5 (IP CENTRAL) ---
echo Para acceder desde otra PC, usa la IP de esta maquina + :8000
echo Ejemplo: http://192.168.1.55:8000
echo ------------------------------------------------
cd /d "%~dp0"
call venv\Scripts\activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
