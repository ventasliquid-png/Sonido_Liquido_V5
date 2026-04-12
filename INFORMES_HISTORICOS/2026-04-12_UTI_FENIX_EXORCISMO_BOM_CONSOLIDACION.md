# Informe de Sesión: UTI Fénix — Exorcismo BOM y Consolidación Main

**Fecha**: 2026-04-12  
**ID de Sesión**: Omega-20260412 (Continuación UTI Restauración Fénix)  
**Agente**: Claude Sonnet 4.6 (Claude Code)  
**Estado del Sistema**: **NOMINAL GOLD**  
**Entorno**: OF (DESKTOP-4S7F5DT)

---

## 1. Punto de Partida

La sesión retomó una conversación interrumpida por límite de contexto. El trabajo previo (sesiones 11-12 de Abril) había completado:

- Trasplante de `pilot_v5x.db` desde producción Tomy (`V5_RELEASE_09/V5_LS_MASTER.db`)
- Hardening 64-bit: `flags_estado BIGINT` en todas las tablas
- Creación de `ProductoFlags` soberano en `backend/productos/constants.py`
- Fix del bug sintáctico crítico en `backend/productos/router.py`
- Normalización de DB: rubros, productos huérfanos, SKUs de prueba

El sistema sin embargo **no arrancaba en frontend** con el error:

```
Uncaught TypeError: Failed to resolve module specifier "pinia".
Relative references must start with either "/", "./", or "../".
(index):1
```

---

## 2. Diagnóstico del Error de Pinia — La Cacería

### Fase de Descarte (Caminos Falsos)

El error `(index):1` fue extremadamente engañoso. Durante la investigación se descartaron sistemáticamente:

- **Extensiones del browser**: Descartado (incógnito, múltiples browsers)
- **Caché del browser**: Descartado (limpiado múltiples veces, cache Vite eliminada)
- **Zombie processes de Vite**: Descartado (taskkill)
- **Dependencia lodash faltante**: Parcialmente correcto — `GridLoader.vue` y `PedidoCanvas.vue` tenían `import _ from 'lodash'` en HEAD sin lodash en `package.json`, pero eran lazy-loaded y no causaban el error de arranque
- **Anti-patrones de Gy en Vue**: `ToastNotification.vue`, `AppSidebar.vue`, `GlobalStatsBar.vue` tenían composables Pinia/Router dentro de `onMounted()` en vez de setup — causaban crashes de null reference pero no el error de módulo

### Causa Raíz Real: BOM en authStore.js

La causa raíz fue hallada **verificando directamente el output transformado de Vite** mediante `curl`:

```bash
curl http://localhost:5173/src/stores/authStore.js
```

Resultado revelador:

```javascript
// Línea 5 (SIN transformar):
﻿import { defineStore } from 'pinia'

// Línea 6 (transformada correctamente):
import { ref, computed } from "/node_modules/.vite/deps/vue.js?v=1436ff2c"
```

Un carácter **BOM (U+FEFF, `\xEF\xBB\xBF`)** estaba incrustado al comienzo de la línea 5 — antes de la palabra `import`. Este carácter invisible rompía el parser de Vite, que no reconocía `﻿import` como un import válido para transformar. El `from 'pinia'` llegaba crudo al browser, que lo rechazaba como bare specifier no resolvible.

**El BOM no estaba al inicio del archivo** (donde sería inofensivo y estándar). Estaba en el **medio del archivo, pegado a un import específico**, producto de la sincronización masiva de Gy del `20260407130827`.

---

## 3. Intervenciones Quirúrgicas

### 3.1 Exorcismo BOM — Frontend

| Archivo | Línea | Fix |
|---|---|---|
| `frontend/src/stores/authStore.js` | 5 | `﻿import` → `import` |

### 3.2 Fix Anti-patrones Gy — Vue Composables

Gy había movido llamadas a composables fuera del setup de Vue 3:

| Archivo | Bug | Fix |
|---|---|---|
| `frontend/src/components/ui/ToastNotification.vue` | `store = ref(null)` + `onMounted(() => { store.value = useNotificationStore() })` → `v-for` sobre `null.notifications` | Composable restaurado a setup |
| `frontend/src/components/layout/AppSidebar.vue` | `router/route/notificationStore` como `ref(null)` + `onMounted` | Composables restaurados a setup, `.value` eliminados |
| `frontend/src/components/layout/GlobalStatsBar.vue` | `router = ref(null)` en setup | `useRouter()` restaurado a setup directo |

### 3.3 Exorcismo BOM — Backend

Barrido completo reveló el mismo patrón en el módulo `auth`:

| Archivo | Línea | Error | Fix |
|---|---|---|---|
| `backend/auth/router.py` | 5 | `SyntaxError: invalid non-printable character U+FEFF` | BOM eliminado |
| `backend/auth/schemas.py` | 5 | Potencial SyntaxError | BOM eliminado |
| `backend/auth/service.py` | 5 | Potencial SyntaxError | BOM eliminado |

Barrido confirmó: **V5-LS, RAR-V1 e IVA-V1 están limpios**. El BOM era exclusivo de V5 dev.

---

## 4. Consolidación Main — Maniobras Git

### Secuencia de Operaciones (PIN 1974)

```
1. git reset --hard c057a0a6   → main limpio (pre-Gy)
2. Backup preventivo:          → _TEMP_GY/service_gy_backup.py
3. rm backend/productos/service.py (untracked, versión Gy)
4. git merge uti/restauracion-fenix  → Fast-forward limpio
   Files changed: 19, +723/-411
5. Trasplante quirúrgico BOW:
   - normalize_name()
   - check_duplicate_name()
   - reactivate_producto() con upgrade ProductFlags→ProductoFlags (64-bit)
6. Exorcismo BOM: authStore.js
7. Commit: b12ab17a
8. Exorcismo BOM masivo auth/: router, schemas, service
9. Commit: 7a32dfa6
```

### Estado Final del Árbol Git

```
7a32dfa6  Exorcismo BOM Masivo: auth/router, schemas, service [PIN 1974]
b12ab17a  Consolidación Main: Trasplante BOW + Exorcismo BOM [PIN 1974]
cb072a91  UTI Restauración Fénix: Hardening 64-bit y Soberanía de Productos (PIN 1974)
97d0c90d  V5.8 GOLD: Remitos (SSoT + Dynamic Sede) & Productos (Fase 1 Service) - PIN 1974
c057a0a6  Omega: Audit Report IVA_V1 [GOLD]
```

---

## 5. Trasplante BOW — Auditoría 64-bit

Los métodos de Gy fueron trasplantados con upgrade soberano:

| Método | Origen | Cambio aplicado |
|---|---|---|
| `normalize_name()` | Gy (V16.2) | Limpio, sin flags |
| `check_duplicate_name()` | Gy | Limpio, sin flags |
| `reactivate_producto()` | Gy | `ProductFlags.IS_ACTIVE` → `ProductoFlags.IS_ACTIVE` (64-bit) |

El backup de Gy permanece en `_TEMP_GY/service_gy_backup.py` para referencia.

---

## 6. Métricas de la Sesión

| Métrica | Valor |
|---|---|
| BOMs eliminados | 4 archivos |
| Anti-patrones Vue corregidos | 3 archivos |
| Commits realizados | 2 propios + 2 mergeados del UTI |
| Entornos satélites auditados | 3 (V5-LS, RAR-V1, IVA-V1) — todos limpios |
| Tiempo de diagnóstico del BOM | ~2 horas (ruta larga por engaño del `(index):1`) |
| DB activa | `pilot_v5x.db` — 568KB — 35 clientes, 47 SKUs, 4 pedidos |

---

## 7. Lección Aprendida

> El error `(index):1` en Chrome DevTools es el peor tipo de pista: preciso en la ubicación (HTML document) pero totalmente opaco sobre la causa. La forma correcta de diagnosticar errores de transformación de Vite es **curlando directamente el módulo desde el servidor** y verificando si el output tiene la transformación correcta.

> Los BOMs incrustados en medio de un archivo (no al inicio) son invisibles en la mayoría de editores y lectores de texto. Solo se revelan al examinar los bytes crudos o al comparar el output del servidor con el esperado.

---

## 8. Estado de Cierre

- **Sistema**: NOMINAL GOLD
- **Frontend**: Arranca sin errores
- **Backend**: Arranca sin SyntaxErrors
- **Rama activa**: `main` — `7a32dfa6`
- **DB**: `pilot_v5x.db` — integra, sin modificaciones de esquema en esta sesión
