
# [V5.7] 2026-02-05 - Estabilización Crítica & Hub Logístico

> **ESTADO:** DEPLOYED
> **TIPO:** CRITICAL FIX / STABILIZATION

**Objetivo:** Levantar el sistema tras caída por Error 500 y reparar la gestión de Domicilios.

**Intervenciones:**
1.  **Backend & DB:**
    *   Identificada causa raíz de 500: Schema Mismatch (Columna `stock_fisico` faltante).
    *   Ejecutada migración `update_schema.py`.
    *   Reparados datos corruptos de productos (Costos nulos) con `fix_product_data.py`.
2.  **Frontend (Hub Logístico):**
    *   **Fix Data Loss:** Implementado hook en `DomicilioSplitCanvas` para copiar datos de entrega a campos principales en domicilios no fiscales.
    *   **UX:** Mejorada visualización de listas (Fallbacks para calles vacías) y añadido soporte F10.

**Resultado:** Sistema operativo y confiable.
