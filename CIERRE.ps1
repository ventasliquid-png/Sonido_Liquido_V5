$ErrorActionPreference = "SilentlyContinue"
[console]::Title = "OMEGA - Cierre de Sesion y Aduana"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       AEROPUERTO V5 - SELLADO DE PASAPORTE OMEGA" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[*] Escaneando biometria de la maquina..." -ForegroundColor DarkGray

$machine = $env:COMPUTERNAME
$date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host ""
Write-Host "¿Cual es el estado del sistema V5 al cerrar la jornada?" -ForegroundColor Yellow
Write-Host "[G] GOLD    (Cielo despejado, Nominal, Funciona)"
Write-Host "[C] CRITICO (Alertas, bugs pendientes, a medias)"
Write-Host ""
$statusInput = Read-Host "Elija G o C"

if ($statusInput -match "^[gG]") {
    $status = "GOLD"
} else {
    $status = "CRITICO"
}

# Crear json manualmente para evitar BOM o encodings raros de PS
$jsonString = '{
  "origen": "' + $machine + '",
  "fecha": "' + $date + '",
  "estado": "' + $status + '"
}'

$path = ".pasaporte_v5.json"
Set-Content -Path $path -Value $jsonString -Encoding UTF8

Write-Host "--------------------------------------------------------"
Write-Host "Pasaporte sellado: $status desde $machine" -ForegroundColor Green
Write-Host "--------------------------------------------------------"

$msg = Read-Host "Mensaje breve para la Bitacora Git (Ej: Fix UI Canvas)"
if ([string]::IsNullOrWhiteSpace($msg)) { $msg = "Omega: Cierre automatico" }
$fullMsg = "Omega: $msg [$status]"

Write-Host "[*] Subiendo contenedor al Vault satelital (GitHub)..." -ForegroundColor Yellow

git add .
git commit -m $fullMsg
git push origin HEAD

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "Carga enviada al Vault remoto exitosamente." -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Hubo un problema empujando el camión al servidor." -ForegroundColor Red
}

Read-Host "Presione Enter para salir"
