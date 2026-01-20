@echo off
echo [OPS] Iniciando secuencia de APAGADO para v5-crisol-micro...
echo [ADVERTENCIA] Esto cortara la conexion a la base de datos inmediatamente.
gcloud sql instances patch v5-crisol-micro --activation-policy=NEVER
echo.
echo [OPS] Comando de apagado enviado. El servidor se detendra en breve.
echo [OPS] Estado actual:
gcloud sql instances describe v5-crisol-micro --format="value(state)"
pause
