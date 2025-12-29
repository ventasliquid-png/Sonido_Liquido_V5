# Sesión Actual - Sonido Líquido V5

**Fecha:** 2025-11-27
**Estado:** Finalizado

## Resumen de Contexto
Sesión enfocada en pulir la UX/UI del módulo de Clientes, específicamente la gestión de Domicilios.

## Tareas Completadas
1.  **Pulir Sistema de Clientes**:
    *   **BUG:** El campo "Transporte" no se guarda/muestra correctamente al editar clientes antiguos (legacy) que lo tenían vacío. (CORREGIDO)
    *   **BUG:** Error al guardar/modificar domicilio ("Error al guardar domicilio"). (CORREGIDO - Causa: campo `zona_id` inexistente en DB).
    *   **UX:** Rediseño de Ficha de Cliente (Dashboard de Domicilios). (IMPLEMENTADO)
    *   **BUG:** Error de sintaxis/500 en `ClienteForm.vue`. (CORREGIDO)
    *   **UX:** Mejorar interacción con Domicilios (Doble click, obligatoriedad fiscal). (IMPLEMENTADO)
    *   **UX:** Rediseño Tab Logística (`DomicilioGrid`). (IMPLEMENTADO)
    *   **BUG:** Pantalla de cliente vacía (sin datos). (CORREGIDO)
    *   **BUG:** Errores en Domicilios (Validación "S/N" y Lista Transporte). (CORREGIDO)
    *   **BUG:** Duplicidad y Visualización en Domicilios. (CORREGIDO)
    *   **BUG:** Refresco y Conteo de Domicilios. (CORREGIDO)
    *   **UX:** Lógica de Transporte por Defecto y F10. (CORREGIDO - Auto-relleno inteligente y captura de F10 en modal).
    *   **BUG:** Crash por `ReferenceError: onUnmounted`. (CORREGIDO).

## Archivos Relevantes
*   `frontend/src/views/Maestros/ClienteForm.vue`
*   `frontend/src/views/Clientes/components/DomicilioGrid.vue`
*   `backend/clientes/models.py`
*   `backend/clientes/service.py`


## SESIÓN 2025-12-29 (Gy)
- **FEATURE:** Módulo de Etiquetado PDF ARCA (Standalone + Core). (COMPLETO)
- **DOCS:** Informe para Arquitecta, Bitácora y Manual Operativo. (ACTUALIZADOS)
