content = """@echo off
title DESPERTAR - Control de Transito ALFA
setlocal enabledelayedexpansion

echo ========================================================
echo        SONIDO LIQUIDO V5 - MOTOR DE ARRANQUE
echo ========================================================
echo.

REM 1. GIT SYNC (INTERACTIVO)
choice /C SN /N /M "Desea ejecutar GIT PULL para sincronizar rama (S/N)? [S/N] "
if !errorlevel! equ 1 (
    echo [*] Sincronizando con el Vault (Github)...
    git pull
    python scripts\manager_status.py set 4
    if !errorlevel! neq 0 (
        echo [ERROR] Fallo el Git Pull. Verifique conexion o conflictos.
        pause
    )
) else (
    echo [!] Saltando sincronizacion manual.
)

echo.
REM 2. Consultar estado del Genoma
set "BIT_CRITICO=0"
set "DESINCRO=0"
set "STATUS_L="

for /f "tokens=1,* delims=:" %%A in ('python scripts\manager_status.py read') do (
    if "%%A"=="STATUS_STR" set "STATUS_L=%%B"
    if "%%A"=="ALERT" set "DESINCRO=1"
)

echo ========================================================
echo           REPORTE METEOROLOGICO (BIT 3)
echo ========================================================
echo !STATUS_L! | findstr /C:"CRITICO" >nul
if !errorlevel! equ 0 (
    set "BIT_CRITICO=1"
)
echo !STATUS_L! | findstr /C:"CRÍTICO" >nul
if !errorlevel! equ 0 (
    set "BIT_CRITICO=1"
)

if !BIT_CRITICO! equ 1 (
    echo  [ALERTA ROJA] Hay lios en el gallinero (Bit 3: CRITICO activado)
    echo  Estado actual: !STATUS_L!
) else (
    echo  [OK] Ultima sesion termino con cielo despejado (GOLD).
    echo  Estado actual: !STATUS_L!
)

if !DESINCRO! equ 1 (
    echo  [ATENCION] Posible desincronizacion de origen.
)

echo.
echo ========================================================
echo SELECCION DE PROTOCOLO:
echo ========================================================
echo [L] ALFA-LITE : Via rapida (Ajustes UI, Fixes locales). Sin burocracia.
echo [C] CANARIO   : Auditoria profunda (Cambios estructurales o resolucion).
echo [X] SALIR     : No copiar nada.
echo.

choice /C LCX /N /M "Seleccione opcion [L / C / X]: "
set OPCION=!errorlevel!

if !OPCION! equ 1 (
    echo [*] Preparando directiva ALFA-LITE...
    powershell -command "Set-Clipboard -Value 'Gy, arrancamos bajo ALFA-LITE (Via rapida). El entorno esta despejado. Tarea a resolver: '"
    echo Instruccion LITE copiada al portapapeles.
) else if !OPCION! equ 2 (
    echo [*] Preparando directiva CANARIO...
    powershell -command "Set-Clipboard -Value 'Gy, inicia ALFA COMPLETO. Ejecuta el Canario V2.0, realiza auditoria y aguarda mi instruccion.'"
    echo Instruccion CANARIO copiada al portapapeles.
) else (
    echo [!] Operacion abortada.
    exit /b
)

echo.
echo ========================================================
echo Operacion completada. Pegue el comando en la interfaz de Gy.
echo PRESIONE UNA TECLA PARA CERRAR
echo ========================================================
pause > nul
"""

with open('DESPERTAR.bat', 'w', newline='\r\n', encoding='utf-8') as f:
    f.write(content)
