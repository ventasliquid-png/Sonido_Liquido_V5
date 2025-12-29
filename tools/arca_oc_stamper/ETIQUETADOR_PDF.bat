@echo off
title Etiquetador ARCA - Sonido Liquido
cd /d "%~dp0"
:: Usar el python del venv de la app principal
set VENV_PATH=..\..\backend\venv\Scripts\python.exe

if exist "%VENV_PATH%" (
    "%VENV_PATH%" "etiquetador_escritorio.py"
) else (
    python "etiquetador_escritorio.py"
)
pause
