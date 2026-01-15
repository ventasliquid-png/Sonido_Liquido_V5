
# [RECUPERACIÓN] 2026-01-14 - Parche de Emergencia "Math Guard Clauses"

> **ESTADO:** SATISFACTORIO
> **TIPO:** HOTFIX / SEGURIDAD

Se detectó y documentó retroactivamente el parche de emergencia 'Math Guard Clauses' tras un colapso por Error 500 (División por cero).

**Detalles Técnicos:**
1.  **Backend:** Se blindaron `pricing_engine.py` y `router.py` (función `calculate_prices`) para capturar valores `None` o `0` en `precio_roca` y `costo_reposicion`.
2.  **Resultado:** El sistema devuelve `0.00` en todos los precios calculados en lugar de crashear, permitiendo que el listado de productos cargue incluso con datos corruptos.
3.  **Schemas:** Ajustados `schemas.py` para permitir `0.00` y `Optional` en campos de precios.

**Acción Requerida:** Revisar datos de origen para corregir ceros, pero el sistema ya es estable.

# [V5.4] 2026-01-15 - Implementación Multi-Proveedor y Ajustes UI

> **ESTADO:** BLOQUEADO (FRONTEND CRASH)
> **TIPO:** FEATURE / REFINEMENT

**Objetivo:** Implementar "Es Insumo", Selector IVA en Panel Central, y Tabla Multi-Proveedor.

**Avances:**
1.  **Backend (Completado):**
    *   Schema: Creada tabla `productos_proveedores`.
    *   Models: Actualizado `Producto` y creado `ProductoProveedor`.
    *   Router: Agregados endpoints `POST /proveedores` y `DELETE /proveedores/{id}`.
2.  **Frontend (Parcial):**
    *   Implementado layout y lógica en `ProductoInspector.vue`.
    *   Agregado servicio en `productosApi.js`.

**Incidente Bloqueante:**
*   El componente `ProductoInspector.vue` crashea al intentar abrirse (spinner infinito o error Vue).
*   **Causa Raíz Identificada:** Inicialización de arrays en Store (`tasasIva`, `proveedores`) puede ser `null/undefined` en el momento que el `watch(immediate: true)` dispara la lógica.
*   **Estado:** Se aplicaron parches de seguridad (`?.` y `|| []`), pero el error persiste. Se requiere revisión profunda del ciclo de vida del componente.

**Próximos Pasos (Protocolo Omega):**
1.  Debuggear inicio de `ProductoInspector` (Store vs Props).
2.  Verificar persistencia de "Es Insumo".
3.  Verificar tabla de proveedores.
