$pDir = "C:\dev\V5-LS"
$dbPath = "$pDir\data\V5_LS_MASTER.db"
$bakPath = "$pDir\POLIZON_MAESTRO.bak"
$jsonPath = "$pDir\.pasaporte_v5.json"
$targetDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "Iniciando Protocolo Omega Sencillo en V5-LS..." -ForegroundColor Cyan

# 1. Snapshot de Produccin
if (Test-Path $dbPath) {
    Copy-Item $dbPath $bakPath -Force
    Write-Host "[OK] Snapshot POLIZON_MAESTRO.bak creado." -ForegroundColor Green
} else {
    Write-Host "[WARN] No se encontró la base de datos en $dbPath" -ForegroundColor Yellow
}

# 2. Sellado de Pasaporte
$pasaporte = @{
    origen = $env:COMPUTERNAME
    fecha_cierre_real = $targetDate
    estado_salud = "GOLD"
    db_fuente = "V5_LS_MASTER.db"
    version = "V5.9 GOLD"
}
$pasaporte | ConvertTo-Json | Set-Content -Path $jsonPath -Encoding UTF8
Write-Host "[OK] Pasaporte .pasaporte_v5.json actualizado." -ForegroundColor Green

# 3. Sincronización de Documentación a la carpeta current
$sourceDocs = "C:\dev\Sonido_Liquido_V5"
$destDocs = "$pDir\current"
Copy-Item "$sourceDocs\BITACORA_DEV.md" -Destination "$destDocs\BITACORA_DEV.md" -Force
Copy-Item "$sourceDocs\CLAUDE.md" -Destination "$destDocs\CLAUDE.md" -Force
Copy-Item "$sourceDocs\VERSION.txt" -Destination "$destDocs\VERSION.txt" -Force
Write-Host "[OK] Documentación (Bitácora, Claude, Versión) sincronizada a V5-LS." -ForegroundColor Green

# 4. Git Push (Si es repo)
if (Test-Path "$pDir\.git") {
    Write-Host "Ejecutando Push en repositorio de Producción..." -ForegroundColor Yellow
    git -C $pDir add .
    git -C $pDir commit -m "Omega: Cierre V5.9 GOLD (PIN 1974) [GOLD] (Sello: $targetDate)"
    git -C $pDir push prod HEAD
    Write-Host "[OK] Push en Producción completado." -ForegroundColor Green
}

Write-Host "--- PROTOCOLO OMEGA V5-LS FINALIZADO ---" -ForegroundColor Cyan
