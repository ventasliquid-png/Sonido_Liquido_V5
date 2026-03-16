@echo off
TITLE SONIDO LIQUIDO V5 - ACCESO SATÉLITE
echo --- ESTABLECIENDO CONEXIÓN CON SERVIDOR CENTRAL ---
echo IP MAESTRA: 192.168.0.34
echo.
echo [MODO SATÉLITE]: Abriendo el sistema en su navegador...
echo No es necesario correr Backend ni Frontend localmente.
echo.
timeout /t 3
start http://192.168.0.34:5173
echo.
echo Conexión establecida. Deje esta ventana abierta si desea recordatorio.
echo Para cerrar, simplemente cierre el navegador.
pause
