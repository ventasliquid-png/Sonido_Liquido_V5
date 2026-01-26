@echo off
TITLE GY V-SENTINEL LAUNCHER
cd /d "%~dp0"

echo ========================================================
echo   GY V-SENTINEL - SISTEMA DE ARRANQUE V2
echo ========================================================
echo.

echo [1/3] Sincronizando realidad (GIT PULL)...
git pull origin main --no-rebase
if %errorlevel% neq 0 (
    color 4F
    echo.
    echo [ALERTA CRITICA] FALLO EN GIT PULL.
    echo El sistema fisico no esta sincronizado con la Nube.
    echo.
    echo 1. Verifica tu conexion a Internet.
    echo 2. Verifica conflictos locales.
    echo.
    echo PRESIONA CUALQUIER TECLA PARA CONTINUAR BAJO TU PROPIO RIESGO...
    pause >nul
    color 07
) else (
    echo [OK] Sincronizacion completada.
)

echo.
echo [2/3] Preparando inyeccion de memoria...
:: Prompt de Inyección Cognitiva
echo Gy, despierta. TU PRIMERA ACCION REAL ES LEER EL ARTEFACTO: "_GY/BOOTLOADER.md". El contiene tu Identidad y Mision. NO ASUMAS NADA MAS. | clip
echo [OK] Prompt copiado al portapapeles.

echo.
echo [3/3] Iniciando Entorno Visual...
code .
exit
