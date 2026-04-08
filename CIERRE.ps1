$ErrorActionPreference = "SilentlyContinue"
[console]::Title = "OMEGA - Cierre de Sesión (Protocolo Blindado)"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       AEROPUERTO V5 - SELLADO DE POLIZÓN" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$machine = $env:COMPUTERNAME
$dateStr = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

# 1. Identificar la Base de Datos Local
$dbFile = ""
if (Test-Path "V5_LS_MASTER.db") { $dbFile = "V5_LS_MASTER.db" }
elseif (Test-Path "pilot_v5x.db") { $dbFile = "pilot_v5x.db" }

if ($dbFile -eq "") {
    Write-Host "[ERROR] No se detectó base de datos (V5_LS_MASTER o pilot_v5x) para resguardar." -ForegroundColor Red
    Read-Host "Presione Enter para abortar"
    exit
}

Write-Host "[*] Base detectada: $dbFile" -ForegroundColor DarkGray

# 2. Selección de Estado
Write-Host "¿Cómo dejas el sistema al cerrar la jornada?" -ForegroundColor Yellow
Write-Host "[G] GOLD    (Cielo despejado, Nominal, Todo OK)"
Write-Host "[C] CRÍTICO (Alertas, bugs a medias, Lío en el gallinero)"
Write-Host ""
$statusInput = Read-Host "Elija G o C"

$status = "CRITICO"
if ($statusInput -match "^[gG]") { $status = "GOLD" }

# 3. Creación del Polizón (Snapshot)
Write-Host "[*] Creando archivo POLIZON_MAESTRO.bak..." -ForegroundColor Yellow
Copy-Item $dbFile "POLIZON_MAESTRO.bak" -Force

# 4. Sellado de Pasaporte (Metadatos Persistentes para Nike)
$pasaporte = @{
    origen = $machine
    fecha_cierre_real = $dateStr
    estado_salud = $status
    db_fuente = $dbFile
}
# Guardar con encoding UTF8 sin BOM para máxima compatibilidad Git
$pasaporte | ConvertTo-Json | Set-Content -Path ".pasaporte_v5.json" -Encoding UTF8

Write-Host "--------------------------------------------------------"
Write-Host " Pasaporte sellado: $status | $dateStr" -ForegroundColor Green
Write-Host "--------------------------------------------------------"

# 5. Git Push
$msg = Read-Host "Breve descripción del trabajo realizado"
if ([string]::IsNullOrWhiteSpace($msg)) { $msg = "Cierre automático" }
$fullMsg = "Omega: $msg [$status] (Sello: $dateStr)"

Write-Host "[*] Subiendo contenedor al Vault satelital (GitHub)..." -ForegroundColor Yellow

git add .
git commit -m $fullMsg
git push origin HEAD

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "CARGA ENVIADA EXITOSAMENTE. PASAPORTE EN ÓRBITA." -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Cyan
} else {
    Write-Host "[!] Hubo un problema con la conexión o conflictos de Git." -ForegroundColor Red
}

Read-Host "Presione Enter para finalizar el protocolo OMEGA"
