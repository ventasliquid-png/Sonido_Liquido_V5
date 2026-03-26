@echo off
title DESPERTAR - Protocolo ALFA (Atenea V5)
setlocal enabledelayedexpansion

echo ========================================================
echo        SONIDO LIQUIDO V5 - PROTOCOLO DE DESPERTAR
echo ========================================================
echo.

:: 1. GIT SYNC (INTERACTIVO)
set /p git_pull="Desea ejecutar GIT PULL para sincronizar rama (S/N)? [N]: "
if /i "%git_pull%"=="S" (
    echo [*] Sincronizando con el Vault...
    git pull
    python scripts/manager_status.py set 4
    if !errorlevel! neq 0 (
        echo [ERROR] Fallo el Git Pull. Verifique conexion o conflictos.
        pause
    )
) else (
    echo [!] Saltando sincronizacion manual.
)

echo.

:: 2. LECTURA DE BITS Y CARGA DE COMANDO
python scripts/manager_status.py read | python -c "import sys, subprocess; cmd=sys.stdin.read().split('STATUS_STR:')[1].strip(); subprocess.run(['clip.exe'], input='Gy, ejecutá el Canario V2.0 y reportá el estado del cielo. BitStatus: ' + cmd, encoding='utf16')"

echo ========================================================
echo        COMANDO COPIADO AL PORTAPAPELES
echo ========================================================
echo Instruccion: Pegue el comando en la interfaz de Gy para
echo iniciar la auditoria constitucional del sistema.
echo.
echo Presione cualquier tecla para finalizar...
pause > nul
exit
