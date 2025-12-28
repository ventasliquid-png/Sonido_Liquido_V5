# SCRIPT: INICIAR DB (MODO TRABAJO)
Write-Host "?? CALENTANDO MOTORES EN IOWA..." -ForegroundColor Yellow
gcloud sql instances patch v5-crisol-micro --activation-policy ALWAYS --quiet
Write-Host "? ORDEN ENVIADA. ESPERE 2 MINUTOS PARA CONECTAR." -ForegroundColor Green
