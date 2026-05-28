# purgar_gy.ps1
# Limpieza profilactica de archivos transitorios de Antigravity
# Mantiene configuracion, historial de conversaciones y el log del dia actual
# Llamar desde CIERRE.ps1 o manualmente cuando Antigravity esta cerrado

$gyData = "$env:APPDATA\Antigravity"

if (-not (Test-Path $gyData)) {
    Write-Host "[!] No se encontro directorio de Antigravity. Nada que purgar." -ForegroundColor Yellow
    return
}

# Avisar si Antigravity esta corriendo
$gyProcess = Get-Process | Where-Object { $_.Name -match "antigravity" }
if ($gyProcess) {
    Write-Host "[!] Antigravity esta corriendo. Algunos archivos pueden estar bloqueados." -ForegroundColor Yellow
    Write-Host "    Se purgaran solo las carpetas no bloqueadas." -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Magenta
Write-Host "       PURGA PROFILACTICA DE ANTIGRAVITY (Gy)          " -ForegroundColor Magenta
Write-Host "========================================================" -ForegroundColor Magenta
Write-Host ""

# Carpetas transitorias a purgar (seguro - sin perder config ni historial)
$targets = @(
    "Cache",
    "GPUCache",
    "Code Cache",
    "blob_storage",
    "Network",
    "Service Worker",
    "WebStorage",
    "Local Storage",
    "Session Storage",
    "SharedStorage",
    "CachedData",
    "CachedExtensionVSIXs",
    "DawnGraphiteCache",
    "DawnWebGPUCache",
    "VideoDecodeStats",
    "Crashpad",
    "Shared Dictionary",
    "shared_proto_db"
)

$totalLiberado = 0

foreach ($target in $targets) {
    $path = Join-Path $gyData $target
    if (Test-Path $path) {
        $size = (Get-ChildItem $path -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
        $sizeMB = [math]::Round($size / 1MB, 2)
        Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
        if (-not (Test-Path $path)) {
            Write-Host "  [OK] $target ($sizeMB MB liberados)" -ForegroundColor Green
            $totalLiberado += $size
        } else {
            Write-Host "  [!]  $target (bloqueado - Antigravity activo)" -ForegroundColor Yellow
        }
    }
}

# Purgar logs viejos (mantener solo los del dia de hoy)
$logsPath = Join-Path $gyData "logs"
if (Test-Path $logsPath) {
    $hoy = (Get-Date).Date
    $logsViejos = Get-ChildItem $logsPath -Directory | Where-Object { $_.LastWriteTime.Date -lt $hoy }
    $sizeLogsViejos = ($logsViejos | Get-ChildItem -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
    $logsViejos | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    $restantes = (Get-ChildItem $logsPath -Directory).Count
    $sizeMBLogs = [math]::Round($sizeLogsViejos / 1MB, 2)
    Write-Host "  [OK] logs - $($logsViejos.Count) sesiones anteriores eliminadas, $restantes de hoy conservadas ($sizeMBLogs MB)" -ForegroundColor Green
    $totalLiberado += $sizeLogsViejos
}

$totalMB = [math]::Round($totalLiberado / 1MB, 2)
Write-Host ""
Write-Host "  [=] Espacio total liberado: $totalMB MB" -ForegroundColor Cyan
Write-Host ""
Write-Host "  [=] Configuracion, historial y sesion activa: INTACTOS" -ForegroundColor DarkGray
Write-Host ""
