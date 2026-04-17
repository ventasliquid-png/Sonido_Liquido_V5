$source = "C:\dev\Sonido_Liquido_V5"
$dest = "C:\dev\V5-LS\current"

Write-Host "Iniciando Despliegue de Rubros V5.9 a Producción (V5-LS)..." -ForegroundColor Cyan

# 1. Sincronizar Backend
$backendFiles = @(
    "backend\productos\constants.py",
    "backend\productos\models.py",
    "backend\productos\schemas.py",
    "backend\productos\service.py",
    "backend\productos\router.py"
)

foreach ($file in $backendFiles) {
    Copy-Item "$source\$file" -Destination "$dest\$file" -Force
    Write-Host "  [OK] $file"
}

# 2. Sincronizar Frontend
$frontendFiles = @(
    "frontend\src\views\DataIntel\HardDeleteManager.vue"
)

foreach ($file in $frontendFiles) {
    Copy-Item "$source\$file" -Destination "$dest\$file" -Force
    Write-Host "  [OK] $frontendFiles"
}

# 3. Compilar en Produccin
Write-Host "Construyendo Frontend en Producción..." -ForegroundColor Yellow
Set-Location "$dest\frontend"
npm run build | Out-Null
Write-Host "  [OK] Build completado."

# 4. Inyectar en Static
Copy-Item -Path "dist\*" -Destination "..\static\" -Recurse -Force
Write-Host "  [OK] Archivos inyectados en Static."

Write-Host "--- DESPLIEGUE V5.9 COMPLETADO CON ÉXITO ---" -ForegroundColor Green
