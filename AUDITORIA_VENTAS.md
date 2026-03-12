# Auditoría de Módulo Ventas (Refactorización)

**Fecha:** 18/01/2026
**Estado:** ANÁLISIS PRELIMINAR

## 1. Análisis de Archivos

### A. `PedidoCanvas.vue` (NUEVO ESTÁNDAR)
- **Estado:** Activo y en Evolución.
- **Rol:** Carga y Edición centralizada de Pedidos.
- **Estética:** "Tokyo Blue" + HUD.
- **Acciones:** Se ha unificado aquí la lógica de Creación (`/pedidos/nuevo`) y Edición (`/pedidos/editar/:id`).

### B. `GridLoader.vue` (LEGADO ACTIVO)
- **Estado:** Activo en ruta `/hawe/tactico`.
- **Análisis:** Es el anterior "Cargador Táctico". Contiene lógica compleja de eventos de teclado y gestión de estado local.
- **Observación:** Al redirigir la edición a `PedidoCanvas`, este componente solo queda sirviendo para la creación rápida vía F4 (`Loader Táctico`). Si `PedidoCanvas` es igual de rápido, `GridLoader` debería ser retirado.
- **Recomendación:** Mantener como respaldo hasta validar que `PedidoCanvas` iguala la velocidad de carga (Mouse-less) del GridLoader.

### C. `TacticalView.vue` (CÓDIGO MUERTO)
- **Estado:** Inactivo (No referenciado en Router).
- **Análisis:** Parece un prototipo anterior o una versión alternativa de `GridLoader`.
- **Recomendación:** **ELIMINAR**. No tiene rutas apuntando a él y genera ruido.

## 2. Recomendaciones de Limpieza

1.  **Eliminación Inmediata:**
    -   `src/views/Ventas/TacticalView.vue`

2.  **Deprecación Gradual:**
    -   `src/views/Ventas/GridLoader.vue` -> Redirigir ruta `/hawe/tactico` a `PedidoCanvas` y evaluar feedback de usuarios de "alto rendimiento".

3.  **Unificación de Estilos:**
    -   `PedidoCanvas.vue` ya cumple con el estándar Tokyo Blue.
    -   Falta aplicar estándar a `PedidoList.vue` (actualmente tiene mezcla de verdes oscuros).

## 3. Próximos Pasos sugeridos
-   Borrar `TacticalView.vue`.
-   Aplicar estilo Tokyo Blue a `PedidoList.vue`.
