
# [RECUPERACIÓN] 2026-01-14 - Parche de Emergencia "Math Guard Clauses"

> **ESTADO:** SATISFACTORIO
> **TIPO:** HOTFIX / SEGURIDAD

Se detectó y documentó retroactivamente el parche de emergencia 'Math Guard Clauses' tras un colapso por Error 500 (División por cero).

**Detalles Técnicos:**
1.  **Backend:** Se blindaron `pricing_engine.py` y `router.py` (función `calculate_prices`) para capturar valores `None` o `0` en `precio_roca` y `costo_reposicion`.
2.  **Resultado:** El sistema devuelve `0.00` en todos los precios calculados en lugar de crashear, permitiendo que el listado de productos cargue incluso con datos corruptos.
3.  **Schemas:** Ajustados `schemas.py` para permitir `0.00` y `Optional` en campos de precios.

**Acción Requerida:** Revisar datos de origen para corregir ceros, pero el sistema ya es estable.
