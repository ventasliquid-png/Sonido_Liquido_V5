@echo off
echo [OPS] Iniciando secuencia de encendido para v5-crisol-micro...
gcloud sql instances patch v5-crisol-micro --activation-policy=ALWAYS
echo.
echo [OPS] Servidor encendido. Esperando a que este listo...
timeout /t 5
echo [OPS] Estado actual:
gcloud sql instances describe v5-crisol-micro --format="value(state)"
pause
