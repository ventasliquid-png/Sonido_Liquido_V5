@echo off
TITLE GY V14 - CARGADOR TACTICO
color 0A

:: ==========================================
:: CONFIGURACION DE MISION (EDITAR AL CAMBIAR DE FASE)
:: ==========================================
set RAMA_OBJETIVO=v5.6-contactos-agenda

echo ==========================================
echo   CARGADOR DE PROTOCOLO GY V14
echo   RAMA ACTIVA: %RAMA_OBJETIVO%
echo ==========================================
echo.

:PREGUNTA_GIT
set /p update=">> Necesitas actualizar desde la Nube (Hubo trabajo en otro lado)? (S/N): "
if /i "%update%"=="s" goto GIT_PULL
if /i "%update%"=="n" goto CARGAR_PROMPT
goto PREGUNTA_GIT

:GIT_PULL
echo.
echo [Sincronizando %RAMA_OBJETIVO%...]
git pull origin %RAMA_OBJETIVO%
if %errorlevel% neq 0 (
    color 4F
    echo [ERROR] Fallo la actualizacion. Revisa tu conexion.
    pause
) else (
    echo [OK] Sistema actualizado.
)
goto CARGAR_PROMPT

:CARGAR_PROMPT
echo.
echo [Generando Prompt de Activacion...]
:: EL SECRETO: Ordenamos leer el IPL (Identidad) ANTES que el Bootloader (Estado)
:: Esto evita que se crea que "terminó" si el bootloader quedó viejo.
echo SISTEMA: INICIO DE SESION. EJECUTAR PROTOCOLO ALFA (PRIORIDAD 1). Paso 1: Lee e instala tu identidad desde "_GY/_IPL/GY_IPL_V14.md". Paso 2: Solo una vez instalada, lee "_GY/BOOTLOADER.md" para contexto, pero VERIFICA la realidad con 'git status' antes de asumir que la mision termino. TU MISION ACTUAL: Logistica/Transporte (Rama %RAMA_OBJETIVO%). Reportate lista. | clip

echo.
echo [LISTO] La orden de encendido esta en tu portapapeles.
echo 1. Abre Antigravity.
echo 2. Presiona Ctrl + V.
echo 3. Dale Enter.
echo.
echo Cerrando cargador en 4 segundos...
timeout /t 4
exit