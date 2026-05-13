# PROTOCOLO DE EMERGENCIA — Bug en MT

## Doctrina
El flujo canónico de desarrollo es siempre:
D (desarrollo) → P en MC (staging) → MT (producción vía git pull)

Nunca operar directamente en P de MC ni en MT para resolver bugs,
salvo autorización explícita de Carlos con PIN 1974 y registro en bitácora.

## Cuándo aplica
Cuando MT presenta un bug en producción y Tomy no puede operar.

## Pasos

### 1. Contener — destrabar a Tomy si es posible
- Si el bug es de datos (registro huérfano, duplicado, etc.):
  CC puede operar quirúrgicamente sobre V5_LS_MASTER.db en MT con PIN 1974
- Si el bug es de código: Tomy espera. No parchear P ni MT directamente.

### 2. Reproducir en D
- Copiar V5_LS_MASTER.db de MT a D como DB de prueba:
  cp \\192.168.0.34\dev\v5-ls-Tom\data\V5_LS_MASTER.db
     C:\dev\Sonido_Liquido_V5\data\debug_MT.db
- Apuntar temporalmente el .env de D a debug_MT.db
- Reproducir el bug en D con datos reales de MT

### 3. Solucionar en D
- Todo el trabajo de código se hace en D
- Tests en D con debug_MT.db
- Commit en D cuando el fix está verificado

### 4. Propagar D → P en MC
- Cherry-pick de los commits de fix de D hacia P:
  git remote add desarrollo C:\dev\Sonido_Liquido_V5
  git fetch desarrollo
  git cherry-pick <hash_fix>
- Verificar que P en MC arranca y funciona
- Push P MC a origin

### 5. Desplegar en MT
- En MT: git pull
- Aplicar migraciones si las hay
- npm run build + xcopy si hay cambios de frontend
- Reiniciar uvicorn
- Verificar con Tomy

## Registro obligatorio
Todo incidente de emergencia debe quedar registrado en:
- Bitácora OMEGA de la sesión
- Tabla bugs o deuda_tecnica en pilot_v5x.db con sesión y descripción

## Excepciones autorizadas
- Limpieza quirúrgica de datos en MT: autorizada con PIN 1974
- Migración de schema en MT: autorizada con PIN 1974 + script versionado
- Nunca: edición directa de código en MT o P sin pasar por D primero

---
*Documento creado sesión 806 — Carlos + Claude Sonnet*
*Canonizado por doctrina de flujo D→P→MT*
