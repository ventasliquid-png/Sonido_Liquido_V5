@echo off
TITLE GY V14 - CARGADOR MANUAL
color 0A

echo ==========================================
echo   CARGADOR DE PROTOCOLO GY V14
echo ==========================================
echo.
echo RAMA OBJETIVO: v5.6-contactos-agenda
echo.

:PREGUNTA_GIT
set /p update=">> Es necesario bajar del GIT actualizaciones? (S/N): "
if /i "%update%"=="s" goto GIT_PULL
if /i "%update%"=="n" goto CARGAR_PROMPT
goto PREGUNTA_GIT

:GIT_PULL
echo.
echo [Sincronizando...]
:: Pull especifico de la rama de trabajo actual para evitar errores de main
git pull origin v5.6-contactos-agenda
if %errorlevel% neq 0 (
    color 4F
    echo [ERROR] Fallo la actualizacion.
    pause
) else (
    echo [OK] Sistema actualizado.
)
goto CARGAR_PROMPT

:CARGAR_PROMPT
echo.
echo [Cargando Orden de Despertar...]
:: COPIA SILENCIOSA AL PORTAPAPELES
echo Gy, despierta. TU PRIMERA ACCION ES LEER "_GY/BOOTLOADER.md". Ahi esta tu Identidad V14 y tu Mision. | clip
echo.
echo [LISTO] La orden esta en tu portapapeles (Ctrl+V).
echo Abre Antigravity y pegala.
echo.
timeout /t 3
exit