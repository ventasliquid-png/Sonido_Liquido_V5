@echo off
TITLE GY - CARGADOR UNIFICADO V5 Y RAR (AUTO-DETECT)
color 0E

echo =======================================================
echo   CARGADOR DE PROTOCOLO GY [DINAMICO - V5 ^& RAR]
echo =======================================================
echo.

:: 1. AUTO-DETECCION DE RAMA EN V5
cd /d "C:\dev\Sonido_Liquido_V5"
for /f "tokens=*" %%i in ('git branch --show-current') do set RAMA_V5=%%i

echo [INFO] RAMA V5 Detectada: %RAMA_V5%
echo.

:: 2. AUTO-DETECCION DE RAMA EN RAR
cd /d "C:\dev\RAR_V1"
for /f "tokens=*" %%i in ('git branch --show-current') do set RAMA_RAR=%%i

echo [INFO] RAMA RAR Detectada: %RAMA_RAR%
echo.

:PREGUNTA_GIT
set /p update=">> Necesitas actualizar ambas ramas desde la Nube? (S/N): "
if /i "%update%"=="s" goto GIT_PULL
if /i "%update%"=="n" goto CARGAR_PROMPT
goto PREGUNTA_GIT

:GIT_PULL
echo.
echo [Sincronizando V5: %RAMA_V5%...]
cd /d "C:\dev\Sonido_Liquido_V5"
git pull origin %RAMA_V5%
if %errorlevel% neq 0 (
    color 4F
    echo [ERROR] Fallo la actualizacion en V5.
    pause
    exit /b
) else (
    echo [OK] V5 actualizado.
)

echo.
echo [Sincronizando RAR: %RAMA_RAR%...]
cd /d "C:\dev\RAR_V1"
git pull origin %RAMA_RAR%
if %errorlevel% neq 0 (
    color 4F
    echo [ERROR] Fallo la actualizacion en RAR.
    pause
    exit /b
) else (
    echo [OK] RAR actualizado.
)
color 0E
goto CARGAR_PROMPT


:CARGAR_PROMPT
echo.
echo [Generando Prompt de Activacion Dual...]

:: PROMPT GENERICO DUAL
echo SISTEMA UNIFICADO: INICIO DE SESION. 1) RAMA V5: %RAMA_V5% ^| RAMA RAR: %RAMA_RAR%. 2) IDENTIDAD V5: Busca y carga el archivo mas reciente en "C:\dev\Sonido_Liquido_V5\_GY\_IPL\". 3) MISION V5: Lee "C:\dev\Sonido_Liquido_V5\_GY\BOOTLOADER.md". 4) MISION RAR: Lee "C:\dev\RAR_V1\_RAR\BOOTLOADER.md" y verifica "RAR_DEFINITION.md". Si dice "Complete" en V5, verifica con 'git status' en ambos directorios antes de continuar. EJECUTAR PROTOCOLOS ALFA EN AMBOS. | clip

echo.
echo [LISTO] Orden generica dual copiada al portapapeles.
echo 1. Abre Antigravity.
echo 2. Ctrl + V.
echo 3. Enter.
echo.
echo Cerrando en 5 segundos...
timeout /t 5
exit
