
# check_health.ps1
# Monitoreo de salud para Antigravity (Protocolo de Prevención de Bloqueo)

$logBase = "$env:APPDATA\Antigravity\logs"
if (-not (Test-Path $logBase)) {
    Write-Host "[!] No se encontró el directorio de logs de Antigravity." -ForegroundColor Red
    return
}

$latestLogDir = Get-ChildItem -Path $logBase -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $latestLogDir) {
    Write-Host "[!] No hay logs disponibles para analizar." -ForegroundColor Yellow
    return
}

Write-Host "[*] Analizando salud desde: $($latestLogDir.Name)..." -ForegroundColor Cyan

$authLog = Join-Path $latestLogDir.FullName "auth.log"
$healthOk = $true
$warnings = @()

# 1. Verificar Refrescos de Token (auth.log)
if (Test-Path $authLog) {
    $recentRefreshes = Get-Content $authLog | Where-Object { $_ -match "OAuth token changed" }
    if ($recentRefreshes.Count -gt 5) {
        $warnings += "Detectado 'Parpadeo' de Tokens ($($recentRefreshes.Count) refrescos). Posible inestabilidad de sesión."
        $healthOk = $false
    }
}

# 2. Buscar "key not found" o errores de sincronización
$allLogs = Get-ChildItem -Path $latestLogDir.FullName -Filter "*.log"
foreach ($logFile in $allLogs) {
    $errors = Get-Content $logFile.FullName | Where-Object { $_ -match "key not found|state syncing error|Failed to get OAuth token" }
    if ($errors) {
        $warnings += "Error Crítico detectado en $($logFile.Name): $($errors[-1])"
        $healthOk = $false
    }
}

# 3. Resultado
if ($healthOk) {
    Write-Host "[OK] Salud de Antigravity estable. Sin patrones de bloqueo detectados." -ForegroundColor Green
} else {
    Write-Host "[ALERTA] Se detectaron síntomas de bloqueo inminente o inestabilidad:" -ForegroundColor Red
    foreach ($w in $warnings) {
        Write-Host "  - $w" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host ">>> SUGERENCIA: Si experimentas parpadeo o falta de respuesta:" -ForegroundColor Cyan
    Write-Host "    1. Ejecutá 'Sign Out' y luego 'Sign In'." -ForegroundColor White
    Write-Host "    2. Si persiste, cerrá el IDE y matá procesos remanentes: taskkill /F /IM node.exe" -ForegroundColor White
    Write-Host "    3. Limpieza preventiva: Borrar carpeta Cache en AppData\Roaming\Antigravity." -ForegroundColor White
}
Write-Host ""
