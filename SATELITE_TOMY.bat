@echo off
TITLE SONIDO LIQUIDO V5 - ACCESO SATELITE (TOMY)
color 0B

echo ==================================================
echo   SONIDO LIQUIDO V5 - MODO SATELITE
echo   Verificando servidor...
echo ==================================================
echo.

powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://192.168.0.34:8090' -TimeoutSec 4 -UseBasicParsing | Out-Null; exit 0 } catch { exit 1 }" > nul 2>&1
if %errorlevel% NEQ 0 (
    color 4F
    echo ==================================================
    echo   [!] SERVIDOR NO RESPONDE
echo ==================================================
    echo.
    echo   El sistema no esta activo en este momento.
    echo   Avisale a Carlos para que lo levante.
    echo.
    echo   (Esperado en: 192.168.0.34:8090)
    echo.
    pause
    exit
)

echo   Servidor activo. Abriendo sistema...
echo.
timeout /t 2 /nobreak > nul
start http://192.168.0.34:8090
echo.
echo   Si la pagina no carga:
echo   1. Verifica que estes en la misma red
echo   2. Avisale a Carlos
echo.
pause
