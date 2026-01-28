@echo off
TITLE GY - CARGADOR UNIVERSAL (AUTO-DETECT)
color 0A

echo ==========================================
echo   CARGADOR DE PROTOCOLO GY [DINAMICO]
echo ==========================================
echo.

:: 1. AUTO-DETECCION DE RAMA (Magia Negra de Git)
:: Le pide a Git el nombre de la rama actual y lo guarda en la variable RAMA_ACTUAL
for /f "tokens=*" %%i in ('git branch --show-current') do set RAMA_ACTUAL=%%i

echo [INFO] Rama Detectada: %RAMA_ACTUAL%
echo.

:PREGUNTA_GIT
set /p update=">> Necesitas actualizar '%RAMA_ACTUAL%' desde la Nube? (S/N): "
if /i "%update%"=="s" goto GIT_PULL
if /i "%update%"=="n" goto CARGAR_PROMPT
goto PREGUNTA_GIT

:GIT_PULL
echo.
echo [Sincronizando %RAMA_ACTUAL%...]
:: Usa la variable detectada, nunca mas hardcodeo
git pull origin %RAMA_ACTUAL%
if %errorlevel% neq 0 (
    color 4F
    echo [ERROR] Fallo la actualizacion. Revisa tu conexion o conflictos.
    pause
) else (
    echo [OK] Sistema actualizado.
)
goto CARGAR_PROMPT

:CARGAR_PROMPT
echo.
echo [Generando Prompt de Activacion...]

:: PROMPT GENERICO: No contiene datos fijos, contiene INSTRUCCIONES DE BUSQUEDA.
:: 1. La Rama es la variable detectada.
:: 2. La Identidad se busca por ubicacion, no por nombre (V14/V15).
:: 3. La Mision se delega al archivo BOOTLOADER.
echo SISTEMA: INICIO DE SESION. 1) RAMA ACTIVA: %RAMA_ACTUAL%. 2) IDENTIDAD: Busca y carga el archivo mas reciente en la carpeta "_GY/_IPL/". 3) MISION: Lee "_GY/BOOTLOADER.md". Si dice "Complete", verifica con 'git status' antes de cerrar. EJECUTAR PROTOCOLO ALFA. | clip

echo.
echo [LISTO] Orden generica copiada.
echo 1. Abre Antigravity.
echo 2. Ctrl + V.
echo 3. Enter.
echo.
echo Cerrando en 4 segundos...
timeout /t 4
exit