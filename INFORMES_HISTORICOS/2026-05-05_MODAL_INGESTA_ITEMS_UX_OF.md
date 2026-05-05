# Informe de Sesión: Modal Resolución Ítems — Parche Visual + UX (OF)

**Fecha:** 2026-05-05
**Entorno:** D (CA replicará a OF luego)
**Estado:** NOMINAL
**Hash:** 296a120e
**Archivo:** frontend/src/views/Ventas/PedidoCanvas.vue

## 1. Objetivo

Resolver 5 problemas en el modal de resolución de ítems desde factura: visibilidad, pre-carga de búsqueda, escapatoria de ESC, cancelación incompleta y manejo de 0 en precio.

## 2. Intervenciones

### A. Template — Rediseño visual oscuro
- Cambio: `bg-white` → `bg-[#0f172a]/95` (dark consistente con V5)
- Overlay: `bg-black bg-opacity-50` → `bg-black/40 backdrop-blur-sm`
- Z-index: `z-50` → `z-[9998]` (respeta ClientCanvas Modal en z-[9999])
- Header: Gradient emerald/cyan, texto mono, uppercase labels
- Referencia: Émula estilo ClientCanvas.vue (DarkMode v5)

### B. Pre-carga de búsqueda — Fix con nextTick()
Bug: `ingestaItemSearchTerm` se seteaba antes de que `currentIngestaItem` computara (era null).
Fix: Envuelto en `nextTick()` para garantizar que el computed tenga el array antes.

### C. Captura de ESC en overlay
Adición: `@keydown.esc.stop="cancelItemResolution"` en overlay div.
Duplicado en input para doublet safety.
Efecto: Usuario puede cancelar presionando ESC en cualquier punto.

### D. Cancelación incompleta
Antes: Solo limpiaba estado local.
Ahora: `router.push({ name: 'IngestaFactura' })` redirige al 409 modal original.

### E. Null-safety en precio
Template: `{{ currentIngestaItem.precio.toFixed(2) }}` → `{{ Number(currentIngestaItem.precio || 0).toFixed(2) }}`
Evita error cuando precio es null/undefined (ítems sin cotz).

## 3. Métricas

- Líneas modificadas: 58 insertions, 49 deletions
- Imports: nextTick agregado a vue
- Refs nuevos: itemResolutionOverlayRef
- Computeds afectados: 0 (todos revisados)
- Tests requeridos: Frontend (visual + ESC + router.push)

## 4. Pendientes

- Tests E2E para modal resolution flow (ingesta → búsqueda → confirm → siguiente)
- P: Sincronización manual de parche (revisar rebase vs merge)
- F4 Dar de alta producto: Placeholder actualmente, requiere modal satélite

**Sello de cierre:** PIN 1974 — Sesión OF 2026-05-05 — NOMINAL
