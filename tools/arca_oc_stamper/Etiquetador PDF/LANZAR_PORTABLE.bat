@echo off
title ETIQUETADOR PORTABLE - Sonido Liquido
color 0B

echo ===========================================
echo   ETIQUETADOR PORTABLE (Standalone)
echo ===========================================
echo.

:: Verificar si existe Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] No se encontro Python instalado en esta PC.
    echo Por favor instale Python 3.10 o superior.
    pause
    exit /b
)

echo [1/2] Verificando dependencias necesarias...
python -m pip install customtkinter pypdf reportlab pikepdf --disable-pip-version-check

echo [2/2] Iniciando aplicacion...
python etiquetador_standalone.py

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] La aplicacion tuvo un problema.
    pause
)
exit /b
