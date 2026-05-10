@echo off
setlocal
echo ======================================================
echo [SISTEMA] Actualizando Sonido Liquido V5 para Tomy...
echo ======================================================
cd /d %~dp0

:: Verificar si Git está instalado
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git no esta instalado o no esta en el PATH.
    pause
    exit /b 1
)

echo [1/2] Obteniendo cambios del servidor (git fetch)...
git fetch origin

echo [2/2] Aplicando actualizaciones (git pull)...
git pull origin main

if %errorlevel% neq 0 (
    echo.
    echo [ALERTA] Hubo un problema con la actualizacion. 
    echo Es posible que haya cambios locales sin guardar.
    echo Por favor, consulta con soporte tecnico.
) else (
    echo.
    echo [OK] Sistema actualizado correctamente a la ultima version.
)

echo.
pause
