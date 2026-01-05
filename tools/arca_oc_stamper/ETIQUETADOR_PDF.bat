@echo off
title ETIQUETADOR ARCA - Sonido Liquido V6.x
color 0A

echo ===========================================
echo   ETIQUETADOR ARCA - MODO ESTABLE
echo ===========================================
echo.

:: 1. Configuracion de Rutas
set "ROOT=c:\dev\Sonido_Liquido_V5"
set "TOOLS_DIR=%ROOT%\tools\arca_oc_stamper"
set PYTHONPATH=%ROOT%

:: 2. Seleccion de Motor
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