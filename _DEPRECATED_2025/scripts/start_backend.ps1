# --- start_backend.ps1 (Script Interactivo) ---
# EjecuciÃ³n: .\start_backend.ps1

# Variables de ConfiguraciÃ³n de Infraestructura (EstÃ¡ticas)
 = "postgres"
 = "34.95.172.190"
 = "postgres"
 = "5432"
 = "..\.google_credentials"

Write-Host "=============================================" -ForegroundColor Green
Write-Host "        INICIO DE SESIÃ“N DE BASE DE DATOS" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# 1. Solicitar la ContraseÃ±a de forma Segura (no se muestra en pantalla)
 = Read-Host -Prompt "Ingrese la contraseÃ±a de Cloud SQL" -AsSecureString
 = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR())

# 2. Construir la DATABASE_URL (El paquete de datos final)
 = "postgresql://:@:/"

# 3. Establecer Variables de Entorno
postgresql://postgres:Spawn8559@34.95.172.190:5432/postgres = 
O:\Mi unidad\Sonido-liquido-api\service-account.json = 

Write-Host "Conectando a la IP: " -ForegroundColor Cyan
Write-Host "Variables de entorno establecidas. Iniciando Uvicorn..." -ForegroundColor Green

# 4. Iniciar Uvicorn
uvicorn main:app
