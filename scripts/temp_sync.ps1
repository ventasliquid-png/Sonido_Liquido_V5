$source = "C:\dev\Sonido_Liquido_V5"
$dest = "C:\dev\V5-LS\current"

Write-Host "Iniciando Espejado de Novedades a V5_LS (Produccion)..." -ForegroundColor Cyan

# Backend
Copy-Item "$source\backend\pricing_engine.py" -Destination "$dest\backend\pricing_engine.py" -Force
Write-Host "Backend pricing_engine copiado."

# Frontend
Copy-Item "$source\frontend\src\stores\calculatorStore.js" -Destination "$dest\frontend\src\stores\calculatorStore.js" -Force
Copy-Item "$source\frontend\src\components\ui\HotCalculator.vue" -Destination "$dest\frontend\src\components\ui\HotCalculator.vue" -Force
Copy-Item "$source\frontend\src\App.vue" -Destination "$dest\frontend\src\App.vue" -Force
Copy-Item "$source\frontend\src\directives\v-excel.js" -Destination "$dest\frontend\src\directives\v-excel.js" -Force
Copy-Item "$source\frontend\src\views\Ventas\PedidoCanvas.vue" -Destination "$dest\frontend\src\views\Ventas\PedidoCanvas.vue" -Force
Copy-Item "$source\frontend\src\views\Hawe\components\ProductoInspector.vue" -Destination "$dest\frontend\src\views\Hawe\components\ProductoInspector.vue" -Force
Write-Host "Archivos Frontend copiados."

# Compilar
Write-Host "Construyendo Frontend en Produccion..." -ForegroundColor Yellow
Set-Location "$dest\frontend"
npm run build | Out-Null
Write-Host "Build completado."

# Mover a static
Copy-Item -Path "dist\*" -Destination "..\static\" -Recurse -Force
Write-Host "Archivos HTML inyectados en Static. Produccion Sincronizada." -ForegroundColor Green
