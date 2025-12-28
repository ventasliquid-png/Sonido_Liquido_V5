# Script para lanzar HAWE V5 en modo LAN (Acceso Remoto)
Set-Location "C:\dev\Sonido_Liquido_V5"

# 1. Obtener IP Local
$ip = (Test-Connection -ComputerName (hostname) -Count 1).IPV4Address.IPAddressToString
Write-Host "--- HAWE V5 MODO LAN ---" -ForegroundColor Cyan
Write-Host "Tu IP Local es: $ip" -ForegroundColor Green

# 2. Configurar URL del Backend para el Frontend
$env:VITE_API_URL = "http://$ip:8000"
Write-Host "Frontend configurado para conectarse a: $env:VITE_API_URL" -ForegroundColor Yellow

# 3. Lanzar Backend (en nueva ventana)
Write-Host "Iniciando Backend..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

# 4. Lanzar Frontend (en nueva ventana)
# [GY-FIX] Escribir .env.local para asegurar que Vite lo tome
# [GY-FIX-ARCH] Configuramos VITE_API_URL vacío para forzar que use el Proxy (relativo)
# De esta forma, el browser remoto le pide todos los datos al Frontend Server (5173)
# y el Frontend Server los reenvia internamente a localhost:8000.
# Esto elimina problemas de CORS y de IPs visibles.
$envContent = "VITE_API_URL="
Set-Content -Path "frontend\.env.local" -Value $envContent
Write-Host "Configuración PROXY guardada en frontend\.env.local (API Relative Mode)" -ForegroundColor Yellow

Write-Host "Iniciando Frontend..." -ForegroundColor Magenta
Start-Process powershell -ArgumentList "cd frontend; npm run dev -- --host"

# 5. Instrucciones
Write-Host "`n--- LISTO ---" -ForegroundColor Green
Write-Host "Para acceder desde otra PC, abre el navegador y ve a:"
Write-Host "http://$ip:5173" -ForegroundColor Cyan
Write-Host "`nAsegurate que la otra PC este en la misma red WiFi/Cable."
Read-Host "Presiona Enter para cerrar este lanzador (las ventanas de backend/frontend seguiran abiertas)..."
