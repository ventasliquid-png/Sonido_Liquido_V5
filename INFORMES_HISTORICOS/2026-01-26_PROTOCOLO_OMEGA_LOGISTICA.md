# INFORME TÉCNICO: PROTOCOLO OMEGA - ESTABILIZACIÓN DE LOGÍSTICA (TRANSPORTE)
**Fecha:** 2026-01-26
**Estado:** ÉXITO / ESTABLE
**Módulos Afectados:** Logística (Frontend/Backend), Base de Datos (SQLite), Validación (ARCA/AFIP).

---

## 1. Objetivo de la Sesión
Resolver la imposibilidad de guardar nuevos transportes ("Botón Guardar no responde", "Error 500"), implementar validación estricta de CUIT según normas ARCA, y solucionar inconsistencias entre el Frontend (UUID) y el Backend (Integer) en el módulo de Logística.

## 2. La Saga "Alta de Transporte" (Análisis Post-Mortem)

### Problema A: El "Botón Mudo" (Frontend Validation)
*   **Síntoma:** Al presionar "Guardar" en `TransporteCanvas`, no sucedía nada. Sin errores, sin feedback.
*   **Causa:** La validación de campos obligatorios (`validaCuit`) fallaba silenciosamente por conflictos de Z-Index en las notificaciones (Toast) y falta de manejo de errores explícito en el `catch`.
*   **Solución:**
    1.  Se implementó `alert()` nativo como fallback para garantizar que el usuario vea el error.
    2.  Se agregó validación en tiempo real (Watcher) para el CUIT.
    3.  Se eliminó el cierre accidental del modal (`@click.self`).

### Problema B: El Crash del Backend (Error 422 y 500)
*   **Síntoma 1 (422 Unprocessable Entity):** El servidor rechazaba los datos.
    *   **Causa:** El esquema Pydantic (`schemas.py`) esperaba que `condicion_iva_id` fuera un `Integer`, pero el Frontend enviaba un `UUID` (String).
    *   **Fix:** Se actualizó `schemas.py` para aceptar `UUID` como tipo de dato válido.
*   **Síntoma 2 (500 Internal Server Error):** Tras corregir el 422, el servidor crasheaba al escribir en DB.
    *   **Causa 1 (Schema Drift):** La tabla `empresas_transporte` en SQLite (`pilot.db`) estaba desactualizada. Le faltaban **7 columnas** críticas (incluyendo `cuit`, `condicion_iva_id`, `localidad`).
    *   **Causa 2 (Model Mismatch):** El modelo SQLAlchemy (`models.py`) definía `condicion_iva_id` como `Integer`, chocando con la realidad de los Maestros (UUID).
    *   **Fix:**
        1.  Se ejecutó un script de parcheo (`scripts/patch_transport_schema.py`) que inyectó las columnas faltantes sin perder datos.
        2.  Se refactorizó `models.py` para usar `GUID()` en la Foreign Key.

### Problema C: Consistencia CUIT (ARCA/AFIP)
*   **Requisito:** El usuario exigió que el sistema tolere separadores (`-`, `.`, `/`) **solo** en posiciones específicas (3 y 12), pero que guarde **solo números**.
*   **Implementación:**
    1.  **Validación Visual:** Regex estricto `/^\d{2}[-_\/.\s]\d{8}[-_\/.\s]\d{1}$/` que alerta en tiempo real si el formato es erróneo.
    2.  **Sanitización:** En el momento del `save()` y `update()`, se aplica un `.replace(/[^0-9]/g, '')` para limpiar el payload antes de enviarlo al servidor.

## 3. Estado Final del Sistema

*   **Alta de Transporte:** ✅ Funcional. Guarda nombre, dirección, CUIT, IVA y Sucursal 1.
*   **Edición:** ✅ Funcional. Mantiene la integridad de los datos.
*   **Validación CUIT:** ✅ Estricta (Formato visual) y Limpia (Storage numérico).
*   **Base de Datos:** ✅ Sincronizada (Schema Patch aplicado).

---
**Firmado:** Antigravity Agent (Google Deepmind)
**Para:** NIKE AI (System Architect)
**Protocolo:** OMEGA (Logística)
