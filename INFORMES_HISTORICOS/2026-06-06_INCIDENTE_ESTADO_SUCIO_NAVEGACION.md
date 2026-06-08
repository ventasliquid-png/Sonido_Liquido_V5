# INCIDENTE 2026-06-06 — Estado Sucio de Navegación (Tablero Pedidos)
**Fecha:** 2026-06-06 | **Entorno:** CA | **Severidad:** Media

---

## Síntoma

Tablero Pedidos carga con 0 pedidos y warnings de Transition/Fragment al navegar
directamente desde pantalla de Ingesta sin cerrar el flujo.

```
[Vue warn]: Component inside <Transition> renders non-element root node that cannot be animated.
  at <PedidoList ...>
```

Lista muestra "Todos (0)" / "Pendientes (0)" pese a existir pedidos en DB.

---

## Causa probable

Ingesta deja estado reactivo pendiente (`ingestaData`, Teleport activo) cuando el
usuario navega abruptamente via sidebar. El componente saliente no completó su ciclo
de desmontaje limpio antes de que PedidoList montara.

Cadena de causalidad:
1. Usuario abre Ingesta → activa Teleport en `#global-header-center` + carga `ingestaData` en store
2. Sin cerrar el flujo, navega a "Tablero Pedidos" via sidebar
3. `<Transition mode="out-in">` intenta desmontar Ingesta y montar PedidoList simultáneamente
4. PedidoList es un Fragment (dos raíces: `<Teleport>` + `<div>`) — Transition no puede animarlo
5. Vue aplica `fade-enter-from` (opacity: 0) pero no completa la transición → componente queda invisible
6. Estado reactivo de Ingesta interfiere con carga del store de Pedidos → 0 pedidos renderizados

---

## Resolución aplicada

**Ctrl+Shift+R** (recarga forzada del navegador) — limpia estado DOM y JS por completo.
Tablero Pedidos carga correctamente post-recarga.

---

## Clasificación

**Estado sucio de navegación** — no es bug de código sino de ciclo de vida de componentes
Vue con Teleport activo. El Fragment en PedidoList agrava la situación al impedir que
`<Transition mode="out-in">` complete la animación de entrada.

---

## Contexto relacionado

- **Hotfix 822.1** (2026-06-05): resolvió dirección inversa (PedidoList → PedidoCanvas).
  El presente incidente es la dirección opuesta (Ingesta → PedidoList), con causa raíz diferente.
- **Fragment en PedidoList**: two root nodes (`<Teleport>` + `<div>`) es el estado
  correcto post-822.1. El Fragment no causa error en navegación normal pero sí cuando
  hay estado sucio del componente saliente.

---

## Pendiente

Implementar guard de navegación en Ingesta que limpie estado antes de abandonar la vista:

```javascript
// IngestaFacturaView.vue (o equivalente)
import { onBeforeRouteLeave } from 'vue-router'

onBeforeRouteLeave((to, from, next) => {
    ingestaStore.clearIngestaData()
    next()
})
```

**Card sugerida:** Bug — Guard `onBeforeRouteLeave` en Ingesta para limpiar estado reactivo
al navegar abruptamente. Prioridad: MEDIA.

---

*Archivado: CA — Sesión 823 | Agente: Claude Code (Sonnet 4.6)*
