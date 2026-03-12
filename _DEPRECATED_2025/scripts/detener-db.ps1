# SCRIPT: DETENER DB (MODO AHORRO)
Write-Host "?? CONGELANDO SERVIDOR EN IOWA (us-central1)..." -ForegroundColor Yellow
gcloud sql instances patch v5-crisol-micro --activation-policy NEVER --quiet
Write-Host "? INSTANCIA APAGADA. EL RELOJ SE DETIENE." -ForegroundColor Green
