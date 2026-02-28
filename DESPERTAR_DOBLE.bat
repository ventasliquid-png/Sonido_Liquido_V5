@echo off
TITLE GY - CARGADOR UNIVERSAL PRO v2.1 (ALFA DUAL SITUACIONAL)
color 0B

echo ==========================================
echo   CARGADOR DE PROTOCOLO MULTIPLEX GY v2.1
echo ==========================================
echo.

[cite_start]:: 1. AUTO-DETECCION DE RAMAS Y TELEMETRIA [cite: 2]
cd /d "C:\dev\Sonido_Liquido_V5"
for /f "tokens=*" %%i in ('git branch --show-current') do set RAMA_V5=%%i

cd /d "C:\dev\RAR_V1"
for /f "tokens=*" %%i in ('git branch --show-current') do set RAMA_RAR=%%i

:: 2. LECTURA DE BITS (4-BYTES)
for /f "tokens=*" %%i in ('python scripts/manager_status.py read') do (
    echo %%i | findstr "STATUS_STR:" > nul && set STATUS_HUD=%%i
    echo %%i | findstr "ALERT:DESINCRO_DETECTADA" > nul && set ALERT_SYNC=1
)

echo [INFO] Rama V5 Detectada:  %RAMA_V5%
echo [INFO] Rama RAR Detectada: %RAMA_RAR%
echo [HUD] %STATUS_HUD%

if "%ALERT_SYNC%"=="1" (
    color 0C
    echo.
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    [cite_start]echo   ALERTA: POSIBLE DESINCRO DE TERMINAL [cite: 3]
    echo !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    echo Se recomienda: git fetch / git pull / check DB
    echo.
)

:PREGUNTA_GIT
set /p update=">> Necesitas actualizar ambas ramas desde la Nube? (S/N): "
if /i "%update%"=="s" goto GIT_PULL
if /i "%update%"=="n" goto CARGAR_PROMPT
goto PREGUNTA_GIT

:GIT_PULL
echo.
[cite_start]echo [Sincronizando V5: %RAMA_V5%...] [cite: 4]
cd /d "C:\dev\Sonido_Liquido_V5"
git pull origin %RAMA_V5%

echo [Sincronizando RAR: %RAMA_RAR%...]
cd /d "C:\dev\RAR_V1"
git pull origin %RAMA_RAR%
echo [OK] Sistemas actualizados.
goto CARGAR_PROMPT

:CARGAR_PROMPT
echo.
echo [Generando Prompt de Activacion Situacional...]

:: PROMPT CONSOLIDADO CON DISTINCION DE PROTOCOLOS ALFA
[cite_start]echo %STATUS_HUD% | findstr "CARTA" > nul && set CARTA_FLAG= [!] LEER CARTA_MOMENTO_CERO.md [cite: 6]

:: LA ORDEN SITUADA: ALFA-V5 y ALFA-RAR definidos para paridad absoluta
echo SISTEMA: INICIO DE SESION MULTIPLEX SITUACIONAL. 1) V5: %RAMA_V5% ^^^| RAR: %RAMA_RAR%. 2) ESTADO: %STATUS_HUD%%CARTA_FLAG%. 3) MISION: Trasplante de PROTOCOLO ALFA-RAR (Sabueso Oro, QR, CAE, Pagina 1) a PROTOCOLO ALFA-V5 (Estabilidad DB 428KB y Doctrina 4-Bytes). No rediseñar. Portar y sellar. | clip

echo.
[cite_start]echo [LISTO] Orden situada copiada al portapapeles. [cite: 8]
echo 1. Abre la nueva sesion de Gy.
echo 2. Ctrl + V.
echo 3. Enter.
echo.
[cite_start]echo Cerrando en 4 segundos... [cite: 9]
timeout /t 4
exit