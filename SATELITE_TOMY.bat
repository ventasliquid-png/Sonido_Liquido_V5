@echo off
TITLE SONIDO LIQUIDO V5 - ACCESO SATELITE (TOMY)
color 0B

echo ==================================================
echo   SONIDO LIQUIDO V5 - MODO SATELITE
echo   Conectando al servidor...
echo ==================================================
echo.
echo   Servidor: 192.168.0.34
echo   Puerto:   8090
echo.
echo   El navegador se abrira en 3 segundos...
echo.
timeout /t 3 /nobreak > nul
start http://192.168.0.34:8090
echo.
echo   Si la pagina no carga:
echo   1. Verifica que el servidor este encendido
echo   2. Verifica que estes en la misma red WiFi
echo   3. Avisale a Carlos
echo.
pause
