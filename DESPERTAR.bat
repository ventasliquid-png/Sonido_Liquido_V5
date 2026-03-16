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
for /f "tokens=2 delims=:" %%i in ('python scripts/manager_status.py read ^| findstr "STATUS_STR:"') do set STATUS=%%i

echo Gy, el sistema reporta [!STATUS!]. Ejecuta el Protocolo ALFA.md y reporta estado de integridad.| clip

echo ========================================================
echo        COMANDO COPIADO AL PORTAPAPELES
echo ========================================================
echo Instruccion: Pegue el comando en la interfaz de Gy para
echo iniciar la auditoria constitucional del sistema.
echo.
echo Presione cualquier tecla para finalizar...
pause > nul
exit
