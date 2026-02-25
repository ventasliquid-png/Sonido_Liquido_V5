@echo off
TITLE GY - CARGADOR UNIVERSAL PRO (MULTIPLEX)
color 0B

echo ==========================================
echo   CARGADOR DE PROTOCOLO MULTIPLEX GY
echo ==========================================
echo.

:: 1. AUTO-DETECCION DE RAMAS
cd /d "C:\dev\Sonido_Liquido_V5"
for /f "tokens=*" %%i in ('git branch --show-current') do set RAMA_V5=%%i

cd /d "C:\dev\RAR_V1"
for /f "tokens=*" %%i in ('git branch --show-current') do set RAMA_RAR=%%i

echo [INFO] Rama V5 Detectada:  %RAMA_V5%
echo [INFO] Rama RAR Detectada: %RAMA_RAR%
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

echo [Sincronizando RAR: %RAMA_RAR%...]
cd /d "C:\dev\RAR_V1"
git pull origin %RAMA_RAR%
echo [OK] Sistemas actualizados.
goto CARGAR_PROMPT

:CARGAR_PROMPT
echo.
echo [Generando Prompt de Activacion Multiplex...]

:: PROMPT CONSOLIDADO
echo SISTEMA: INICIO DE SESION MULTIPLEX. 1) RAMA V5: %RAMA_V5% ^| RAMA RAR: %RAMA_RAR%. 2) IDENTIDAD: Asume contexto V5 (Protocolo V14) y RAR_V1 (Caja Registradora). 3) MISION: Manten ambos contextos activos en memoria. EJECUTAR PROTOCOLO ALFA EN AMBOS. | clip

echo.
echo [LISTO] Orden generica copiada al portapapeles.
echo 1. Abre Antigravity.
echo 2. Ctrl + V.
echo 3. Enter.
echo.
echo Cerrando en 4 segundos...
timeout /t 4
exit
