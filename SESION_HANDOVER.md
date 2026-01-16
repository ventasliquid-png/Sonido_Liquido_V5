# Protocolo de Transición (Handover)
**Fecha:** 15 de Enero de 2026
**Estado:** BLOQUEADO (Frontend Crash en ProductoInspector)

## Estado Situacional
1.  **Backend (V5.4):**
    *   Implementado soporte para Proveedores Alternativos (`ProductoProveedor`) y flag `tipo_producto` (Insumos).
    *   Router y Modelos actualizados. Endpoint de proveedores probado manualmente OK.
2.  **Frontend (Inspector):**
    *   Layout de 3 columnas implementado.
    *   **CRASH:** El componente `ProductoInspector.vue` falla al montar.
    *   **Sospecha:** La prop `producto` o el store `productos` (tasasIva, proveedores) no están sincronizados al momento de montar, causando error en el watcher `immediate: true`.

## Próxima Tarea (Immediate Next Action)
**Objetivo:** Reparar `ProductoInspector.vue` y Verificar Fase 3.
**Referencia:** Tarea "Phase 3" en `task.md`.

### Pasos Obligatorios:
1.  **NO asumir que funciona.** El componente está roto.
2.  Revisar `frontend/src/views/Hawe/components/ProductoInspector.vue`.
3.  Implementar defensas robustas en `onMounted` y `watch` para manejar `tasasIva` vacías.
4.  Una vez reparado, verificar:
    *   Switch "Es Insumo".
    *   Selector IVA (Centro).
    *   Tabla Proveedores (Derecha).

> [!WARNING]
> No avanzar con nuevas features hasta que el Inspector abra correctamente sin errores de consola.
