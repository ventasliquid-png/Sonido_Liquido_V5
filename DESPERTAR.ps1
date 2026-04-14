$ErrorActionPreference = "SilentlyContinue"
[console]::Title = "DESPERTAR - Aduana Inteligente (Protocolo Nike)"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       SONIDO LÍQUIDO V5 - ADUANA DE IMPORTACIÓN" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 0. FETCH PREVENTIVO (MIRADA SATELITAL)
Write-Host "[*] Contactando a la Torre de Control (Git Fetch)..." -ForegroundColor DarkGray
git fetch origin HEAD > $null 2>&1

$remotePasaporte = $null
try {
    # Detectar rama actual dinámicamente
    $branch = git branch --show-current
    if (-not $branch) { $branch = "main" }
    
    $remotePasaporteStr = git show "origin/$branch":.pasaporte_v5.json 2>$null
    if ($remotePasaporteStr) { $remotePasaporte = $remotePasaporteStr | ConvertFrom-Json }
} catch {}

if ($remotePasaporte) {
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "📦 PASAPORTE REMOTO DETECTADO" -ForegroundColor Yellow
    $rOrigen = $remotePasaporte.origen
    $rFecha  = $remotePasaporte.fecha_cierre_real
    $rEstado = $remotePasaporte.estado_salud

    $color = "Green"
    if ($rEstado -match "CRITICO") { $color = "Red" }
    
    Write-Host " - Origen del vuelo    : $rOrigen"
    Write-Host " - Sello de Tiempo (P) : $rFecha"
    Write-Host " - Estado de Salud     : $rEstado" -ForegroundColor $color
    Write-Host "========================================================" -ForegroundColor Cyan
}

Write-Host ""

# 1. GIT PULL Y CONTROL DE CONFLICTOS
$gitPrompt = Read-Host "¿Desea bajar la carga de la otra oficina (Git Pull)? (S/N)"
if ($gitPrompt -match "^[sS]") {
    
    # Paracaídas automático antes de tocar nada si es crítico
    if ($remotePasaporte -and $remotePasaporte.estado_salud -match "CRITICO") {
        Write-Host "[!] ALERTA: La carga es CRÍTICA. Se recomienda rama salvavidas." -ForegroundColor Red
        $doBranch = Read-Host "¿Crear rama de seguridad local ahora? (S/N)"
        if ($doBranch -match "^[sS]") {
            $bName = "salvavidas-$(Get-Date -Format 'yyyyMMdd-HHmm')"
            git branch $bName
            Write-Host "[OK] Rama $bName creada." -ForegroundColor Green
        }
    }

    Write-Host "[*] Ejecutando Pull..." -ForegroundColor Yellow
    git pull origin HEAD
    
    # Chequeo de Conflictos Binarios (Protocolo Nike)
    $conflicts = git ls-files -u
    if ($conflicts) {
        Write-Host ""
        Write-Host "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" -ForegroundColor Red
        Write-Host "!!! ERROR CRÍTICO: CONFLICTO BINARIO DETECTADO       !!!" -ForegroundColor Red
        Write-Host "!!! La base de datos o el polizón están en conflicto !!!" -ForegroundColor Red
        Write-Host "!!! Intervención humana manual requerida en Git.     !!!" -ForegroundColor Red
        Write-Host "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" -ForegroundColor Red
        Read-Host "Presione Enter para ABORTAR"
        exit
    }
}

# 2. ADUANA DE POLIZÓN (TRASPLANTE)
if (-not (Test-Path "POLIZON_MAESTRO.bak")) {
    Write-Host ""
    Write-Host "[!] No hay POLIZON_MAESTRO.bak disponible." -ForegroundColor Yellow
    Write-Host "    (No estás conectado, Git no disponible, o cerraste en este mismo puesto.)" -ForegroundColor DarkGray
    Write-Host "    Continuando sin sincronización de base de datos." -ForegroundColor DarkGray
} else {
    Write-Host ""
    Write-Host "[*] Analizando carga del Polizón..." -ForegroundColor Cyan
    
    # Identificar base local
    $localDb = ""
    if (Test-Path "V5_LS_MASTER.db") { $localDb = "V5_LS_MASTER.db" }
    elseif (Test-Path "pilot_v5x.db") { $localDb = "pilot_v5x.db" }

    if ($localDb -ne "" -and $remotePasaporte) {
        # Obtener fechas
        $pFechaObj = [datetime]::ParseExact($remotePasaporte.fecha_cierre_real, "yyyy-MM-dd HH:mm:ss", $null)
        $lFechaObj = (Get-Item $localDb).LastWriteTime

        Write-Host " - Polizón (Remoto): $($remotePasaporte.fecha_cierre_real)"
        Write-Host " - Base Local      : $($lFechaObj.ToString('yyyy-MM-dd HH:mm:ss'))"

        if ($pFechaObj -gt $lFechaObj) {
            Write-Host " >>> RECOMENDACIÓN: EL POLIZÓN ES MÁS RECIENTE. RESTAURAR." -ForegroundColor Green
        } else {
            Write-Host " >>> ADVERTENCIA: EL POLIZÓN ES MÁS VIEJO QUE TU BASE LOCAL." -ForegroundColor Red
            Write-Host " >>> Restaurar podría causar pérdida de datos (Enchastre)." -ForegroundColor Red
        }
        
        Write-Host ""
        $restaurar = Read-Host "¿Deseas RESTAURAR la base local desde el Polizón? (S/N)"
        if ($restaurar -match "^[sS]") {
            Write-Host "[*] Asegurando base local antigua (respaldo_pre_trasplante.db.bak)..." -ForegroundColor Yellow
            Copy-Item $localDb "$localDb.pre_trasplante.bak" -Force
            
            Write-Host "[*] Ejecutando Trasplante Físico..." -ForegroundColor Green
            Copy-Item "POLIZON_MAESTRO.bak" $localDb -Force
            Write-Host "[OK] Base de datos sincronizada." -ForegroundColor Green
        } else {
            Write-Host "[!] Polizón ignorado. Se mantiene la base local actual." -ForegroundColor Yellow
        }
    }
}

Write-Host ""
# 3. SEMÁFORO ALFA (LITE / CANARIO)
$statusL = "LIMPIO"
$output = & python scripts\manager_status.py read
foreach ($line in $output) {
    if ($line -match "^STATUS_STR:(.*)") { $statusL = $matches[1].Trim() }
}

Write-Host "========================================================" -ForegroundColor Cyan
if ($statusL -match "CRÍTICO") {
    Write-Host " [ALERTA] Estado actual: $statusL" -ForegroundColor Red
} else {
    Write-Host " [OK] Estado actual: $statusL" -ForegroundColor Green
}
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[L] ALFA-LITE | [C] CANARIO | [X] SALIR"
$opc = Read-Host "Seleccione"

if ($opc -match "^[lL]") {
    Set-Clipboard -Value "Gy, arrancamos bajo ALFA-LITE (Vía rápida). El entorno está despejado. Tarea: "
    Write-Host "Instrucción ALFA-LITE copiada." -ForegroundColor Green
} elseif ($opc -match "^[cC]") {
    Set-Clipboard -Value "Gy, inicia ALFA COMPLETO. Ejecutá el Canario y validá integridad."
    Write-Host "Instrucción CANARIO copiada." -ForegroundColor Green
}

Read-Host "Enter para cerrar"
