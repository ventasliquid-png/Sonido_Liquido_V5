@echo off
cd /d "%~dp0"
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0DESPERTAR.ps1" %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] DESPERTAR termino con error. Codigo: %ERRORLEVEL%
    pause
)
