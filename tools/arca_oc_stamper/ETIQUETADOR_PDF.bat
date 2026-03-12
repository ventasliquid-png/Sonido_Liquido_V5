@echo off
title ETIQUETADOR ARCA - Sonido Liquido V6.x
color 0A

echo ===========================================
echo   ETIQUETADOR ARCA - MODO ESTABLE
echo ===========================================
echo.

:: 1. Configuracion de Rutas Dinamicas
:: %~dp0 es la carpeta donde vive este .bat
set "TOOLS_DIR=%~dp0"
set "TOOLS_DIR=%TOOLS_DIR:~0,-1%"
pushd "%~dp0"..\..
set "ROOT=%cd%"
popd
set PYTHONPATH=%ROOT%

:: 2. Seleccion de Motor (Venv o Global)
if exist "%ROOT%\backend\venv\Scripts\python.exe" (
    set "PY=%ROOT%\backend\venv\Scripts\python.exe"
) else (
    set "PY=python"
)

:: 3. Asegurar Municion (Dependencias)
echo [1/2] Verificando librerias (customtkinter, pikepdf, etc)...
"%PY%" -m pip install customtkinter pypdf reportlab pikepdf --disable-pip-version-check

:: 4. Lanzamiento
cd /d "%TOOLS_DIR%"
echo [2/2] Iniciando interfaz grafica...
"%PY%" "etiquetador_escritorio.py"

:: 5. Control de Errores
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo [ERROR] La aplicacion se cerro con fallas.
    pause
)

exit /b