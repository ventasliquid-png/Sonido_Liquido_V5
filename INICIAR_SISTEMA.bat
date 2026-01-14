@echo off
TITLE SONIDO LIQUIDO V5 - SISTEMA
cd /d "%~dp0"
:: Intenta activar venv si existe
IF EXIST "backend\venv\Scripts\activate.bat" CALL backend\venv\Scripts\activate.bat
:: Ejecuta el booster
python boot_system.py
pause
