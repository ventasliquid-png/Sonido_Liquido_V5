# INFORME HISTÓRICO — Sesión 810
**Fecha:** 2026-05-18
**Entorno:** OF — D (`C:\dev\Sonido_Liquido_V5`) + P (`C:\dev\v5-ls-Tom`)
**Agente:** Claude Code Sonnet 4.6
**Tema:** FIX C4 ClientCanvas + IVA Rosa PedidoCanvas + Syntax Vite + Navegación + Migración Bit 4

---

## 1. Contexto

Sesión de continuación de 809 (CA). OMEGA formal 809 pendiente se completa en esta sesión. Trabajo en D, cherry-pick a P al cierre. Canario reportó NOMINAL GOLD al inicio (`flags_estado = 13`).

---

## 2. FIX C4 — ClientCanvas: `has4Pillars` bifurcado + Doctrina IS_VIRGIN

**Problema:** `ClientCanvas.vue` usaba un único `hasDomicilioFiscal` que exigía domicilio fiscal (`es_fiscal`) a todos los clientes — incluyendo los Rosa que no tienen ni deben tener domicilio fiscal. Además, la línea `currentFlags &= ~2` apagaba IS_VIRGIN (Bit 1) desde el frontend, violando la Doctrina de Virginidad.

**Solución:**
- `hasDomicilioValido` bifurcado: si `isRosa` (Bit 4) → valida `es_entrega`; si Gold → valida `es_fiscal`.
- Eliminada `currentFlags &= ~2`. IS_VIRGIN solo puede apagarse en backend: trigger CUMPLIDO en `pedidos/router.py` o CAE en `facturacion/service.py`.

**Archivos:** `frontend/src/views/Hawe/ClientCanvas.vue`

---

## 3. FIX PedidoCanvas — Syntax Error Vite

**Problema:** Vite lanzaba `Unexpected token (1306:10)` al arrancar. Un bloque `else { }` espurio insertado en sesión 809 intentaba colgar como tercer else de un bloque `if(route.params.id) { } else { }` ya cerrado — sintaxis inválida para el parser.

**Diagnóstico:** Localizado con script Babel parser que trazó profundidad de llaves línea por línea hasta detectar desequilibrio.

**Solución:** Eliminadas las 4 líneas del bloque espurio (~1964-1967).

**Archivos:** `frontend/src/views/Ventas/PedidoCanvas.vue`

---

## 4. FIX PedidoCanvas — IVA Rosa (Motor Bipolar)

**Problema:** Al cargar un pedido para cliente Rosa (MINORISTA, `nivel_lista=5`), el motor de precios devolvía `Lista 5 = Lista_4 × 1.21` (precio con IVA incluido para consumidor final). El frontend no diferenciaba Rosa/Gold en la cascada, mostrando el precio con IVA al operador.

**Solución:**
- `selectProduct`: si `isSinIVA.value && res.origen === 'LISTA_5'` → `precioFinal = precioFinal / 1.21`.
- Template: bloque IVA pie de pantalla envuelto en `v-if="!isSinIVA"` — invisible para clientes informales.

**Regla canónica confirmada:** `isSinIVA` para pedidos nuevos = `isClientRosa.value`; para edición = `(flagsEstadoPedido & 4096) !== 0` (Bit 12 soberano).

**Archivos:** `frontend/src/views/Ventas/PedidoCanvas.vue`

---

## 5. FIX PedidoCanvas — Reset post-save

**Problema:** Al guardar un pedido manual (`wasIngesta = false`), `resetPedido()` disparaba un `confirm('¿Descartar pedido actual?')` porque los items aún estaban en memoria en el momento del reset.

**Solución:** `resetPedido(skipConfirm = false)` — nuevo parámetro. `savePedido` llama `resetPedido(true)` post-guardado exitoso.

---

## 6. FIX Navegación — Ruta `/hawe/tactico` muerta

**Problema:** El botón "Nuevo" en `PedidoList.vue` y el enlace de edición en `PedidoInspector.vue` apuntaban a `/hawe/tactico`, ruta que no existe en el router. Vue redirigía al catch-all (`/hawe` → Contactos).

**Solución:** 4 ocurrencias reemplazadas por named routes:
- `PedidoList.vue` (botón Nuevo y F4 handler) → `{ name: 'PedidoCanvas' }`
- `PedidoInspector.vue` (edición y returnUrl) → `{ name: 'PedidoEditar', params: { id } }`

---

## 7. Migración Bit 4 — Clientes Rosa D y P

**Diagnóstico `_audit_sovereignty()`:** La inferencia automática de Bit 4 (línea 346, `service.py`) requiere `has_segmento AND not has_real_cuit`. Clientes creados sin `segmento_id` asignado no reciben el sello automático.

**Acción (PIN 1974):**
- `V5_LS_MASTER.db`: `UPDATE ... SET flags_estado = flags_estado | 16` → 4 registros (ANA ROBLES `19`, Cecilia Pascual `1048593`, LUISA PISCITELLI `17`, Pao Tandil `557083`).
- `pilot_v5x.db`: misma query → 2 nuevas (Cecilia Pascual, LUISA PISCITELLI). Ana Robles y Pao Tandil ya tenían Bit 4.

**Deuda técnica registrada:** `_audit_sovereignty()` necesita rama alternativa para inferir Rosa sin `segmento_id`, o documentar como comportamiento intencional.

---

## 8. Commits sesión 810

| Hash D | Hash P | Descripción |
|---|---|---|
| `bf406415` | `5adf6f4` | FIX C4 ClientCanvas — has4Pillars bifurcado + IS_VIRGIN intocable frontend |
| `ff77a309` | `3e060bb` | FIX PedidoCanvas syntax + IVA Rosa + reset post-save + navegación named routes |

---

## 9. Pendientes sesión 811

| # | Tarea | Prioridad |
|---|---|---|
| 1 | MT git pull + npm run build (frontend P) | 🔴 |
| 2 | HONNEY `flags=0` — registro sin EXISTENCE, investigar | 🟡 |
| 3 | `_audit_sovereignty()` hardening — inferir Bit 4 sin segmento | 🟡 |
| 4 | Auditoría Productos | 🟡 |
| 5 | Auditoría Remitos | 🟢 |
| 6 | Auditoría Facturación | 🟢 |

---

*Documento generado sesión 810 — Carlos + Claude Code Sonnet 4.6*
