# HARDENING INGESTA V2 2026-06-06 — Restauración de UX, Scroll y Resolución de Clientes Nuevos
**Fecha:** 2026-06-06 | **Entorno:** D (Local) | **Severidad:** Alta | **Agente:** Antigravity (Gemini 1.5 Pro)

---

## Síntomas Iniciales

1. **Interrupción de Flujo Visual:** Al arrastrar un nuevo documento PDF sobre la Ingesta, el sistema no reaccionaba. Si el documento previo ya había llenado el panel con un "Borrador en Memoria", el área para soltar archivos (dropzone) quedaba inutilizable.
2. **Crash Silencioso de Vue (Vite):** Al intentar corregir la pantalla para que soporte "Global Drag & Drop", un error tipográfico en la sintaxis de Vue (`missing end tag`) generó una pantalla negra de compilación. Además, el navegador arrojaba excepciones internas por variables `undefined`.
3. **Botones de Acción Inalcanzables:** Una vez parseada la factura, la tabla de ítems de la derecha crecía descontroladamente y empujaba el "Menú Explicativo" de acciones fuera del área visible del monitor, debido a que el scroll interno fallaba.
4. **Deadlock Lógico para Clientes Nuevos:** Si la factura correspondía a un cliente inexistente o sin pedidos (ej. "Criocenter"), los botones de vinculación no aparecían en pantalla.

---

## Diagnóstico y Cadena de Causalidad

1. **Refactorización Parcial del Script Setup:** Al intentar separar el método `reset()` para invocarlo desde el nuevo `handleGlobalDrop()`, se borraron accidentalmente de la declaración las referencias reactivas `selectedPedidoId` y `pendingPedidos`. Vue falló al renderizar el DOM porque dichas variables ya no existían en el estado.
2. **Propagación del layout en CSS Grid:** La columna derecha `col-span-7` usaba `flex-col h-full`, pero sin el contrapeso de `min-h-0` en el contenedor raíz y subcontenedores, las capas flexibles priorizaban el alto natural del contenido (la tabla infinita) sobre el alto fijo del navegador, deshabilitando silenciosamente el `overflow-y-auto`.
3. **Condición de Salto de ConserjeV2:** La arquitectura dictaba que si el motor de inteligencia (`ConserjeV2`) no encontraba un `client_resolution.id` (porque el cliente era nuevo), no se ejecutaba `loadClientDetails()`. Como `loadClientDetails()` era la responsable de inicializar `pendingPedidos` en vacío, la variable `selectedPedidoId` se mantenía estancada en `null`, y por ende, todo el bloque HTML `v-if="selectedPedidoId === 'NEW'"` jamás se renderizaba.

---

## Resolución Aplicada

1. **Restauración de Dependencias Reactivas:**
   Se re-inyectaron las definiciones perdidas `const selectedPedidoId = ref(null);` y `const pendingPedidos = ref([]);` en la cabecera `<script setup>` de `IngestaFacturaView.vue`.

2. **Reparación del Árbol DOM:**
   Se introdujo el cierre correspondiente `</div>` en el `<template>` raíz que provocaba la interrupción del plugin Vite-Vue.

3. **Corrección de Contención Flex-Grid (CSS):**
   ```html
   <div class="col-span-7 flex flex-col bg-slate-900/50 rounded-2xl border border-slate-700/50 overflow-hidden relative min-h-0">
       <div v-else class="flex flex-col h-full min-h-0">
   ```
   *Se añadió `min-h-0` a los contenedores padre flexibles para forzar a que el hijo (`flex-1 overflow-y-auto`) acate los límites de la pantalla, resolviendo la inaccesibilidad a los botones de Proceder/Descartar.*

4. **Inyección de Semáforo de Fallback para Clientes Inéditos:**
   ```javascript
   if (auditLog.value?.client_resolution?.id) {
       await loadClientDetails(auditLog.value.client_resolution.id);
       // ...
   } else {
       // Cliente nuevo o no resuelto -> Forzar estado NEW para mostrar botonera
       selectedPedidoId.value = 'NEW';
   }
   ```
   *El sistema ahora reconoce el caso borde y levanta explícitamente la directiva de "Crear Nuevo Pedido" para que el usuario no quede atrapado.*

---

## Doctrina Generada

- **Cuidado con el `flex-1 overflow-y-auto` en contenedores anidados:** En arquitecturas de CSS Grid con `h-full`, el padre flex SIEMPRE debe acompañarse con `min-h-0` o el `overflow` no operará en sus hijos en TailwindCSS.
- **Transparencia Activa en Operaciones Stateless:** Cuando el Conserje "falle silenciosamente" al no encontrar una identidad y pase la carga semántica al front, el Vue Store DEBE establecer estados de reemplazo (`NEW`) para desbloquear las bifurcaciones lógicas de la UI.

---

*Archivado: D — Entorno Local Windows | Operador: Carlos*
