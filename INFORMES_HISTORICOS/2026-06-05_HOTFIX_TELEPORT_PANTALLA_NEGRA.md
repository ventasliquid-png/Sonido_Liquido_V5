# HOTFIX 822.1 — Pantalla negra "Nuevo Pedido" (Teleport v-if bug)
**Fecha:** 2026-06-05 | **Entorno:** OF (D + P) | **Estado:** NOMINAL GOLD
**Hash D:** 34a918fc | **Hash P:** 7ee67b3

---

## Síntoma
Al clickear "Nuevo Pedido (Táctico)" en el sidebar → pantalla negra.
Consola: 0 errores, 45 warnings. Sin crash JS visible.

## Diagnóstico

Cadena de causalidad:
1. `HaweLayout.vue` tenía `v-if="route.name !== 'PedidoCanvas'"` en GlobalStatsBar
2. `route.name` (Vue Router reactivo) cambia INMEDIATAMENTE al iniciar navegación
3. `<transition mode="out-in">` mantiene el componente saliente montado durante su animación
4. HaweView.vue tiene `<Teleport to="#global-header-center">` activo
5. Cuando `v-if=false`, GlobalStatsBar se destruye → `#global-header-center` sale del DOM
6. Teleport de HaweView busca el target → no lo encuentra → Vue warning (cuenta en los 45)
7. La transición falla silenciosamente → PedidoCanvas no renderiza → pantalla negra

## Fix

```diff
- <GlobalStatsBar v-if="route.name !== 'PedidoCanvas' && route.query.mode !== 'satellite'" />
+ <GlobalStatsBar v-show="route.name !== 'PedidoCanvas' && route.query.mode !== 'satellite'" />
```

**1 archivo, 1 línea.** `v-show` → `display:none` → DOM element persiste → Teleport lo
encuentra durante la transición → animación completa → PedidoCanvas renderiza correctamente.

## Impacto
- Sin cambios de comportamiento visible para el usuario
- GlobalStatsBar oculta en PedidoCanvas (como antes, `display:none`)
- Teleport de HaweView y PedidoList funciona sin interrupciones en transiciones

## Doctrina generada
Ver Manual Técnico V5 Sección 35 — Teleport NUNCA bajo v-if. Siempre v-show.

*Hotfix aplicado: D → P cherry-pick. Ambos entornos sincronizados.*
