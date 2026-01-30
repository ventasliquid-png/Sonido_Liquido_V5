# Análisis de Arquitectura: La Paradoja de Pedro (Contactos N:M)

## 🩺 Diagnóstico Actual (Modelo 1:1)
El módulo `contactos` opera bajo un paradigma de **Asociación Exclusiva**:
- **Estructura**: La tabla `contactos` posee Foreign Keys directas (`cliente_id`, `transporte_id`).
- **Restricción**: Un registro solo puede "pertenecer" a una entidad padre.
- **Consecuencia**: Pedro (Jefe de Taller y Comprador) debe ser duplicado en dos registros (`uuid_1`, `uuid_2`).
- **Código Afectado**: `backend/contactos/models.py`, `schemas.py`, `ContactCanvas.vue` (Lógica de selección exclusiva).

## 💥 Análisis de Impacto (Refactor N:M)
Migrar a un modelo de Vínculos Múltiples implica:

### Backend
1.  **Schema Change (Breaking)**:
    - Transformar tabla `contactos` en `personas` (Identidad Única).
    - Eliminar columnas `cliente_id` y `transporte_id`.
    - Crear tabla `asignaciones` (o `vinculos`): `id`, `persona_id`, `entidad_type` ('CLIENTE', 'TRANSPORTE'), `entidad_id`, `rol`, `activo`.
2.  **Migration Strategy**:
    - Script de migración de datos para convertir los actuales `cliente_id` en filas de la tabla `asignaciones`.

### Frontend
1.  **ContactCanvas.vue**:
    - Cambiar de "Select Parent" a "Manage Links".
    - UI para agregar/quitar múltiples roles.
2.  **Listados (Clientes/Logística)**:
    - Actualizar `join` para buscar personas a través de la tabla intermedia.

## ⚖️ Veredicto: EJECUCIÓN INMEDIATA
**Recomendación:** ✅ **HACERLO AHORA.**

### Justificación
1.  **Deuda Técnica Exponencial**: En sistemas B2B/Logísticos, la superposición de roles (Paradox of Pedro) es la norma, no la excepción. Mantener el 1:1 obligará a parches sucios y duplicidad que degradarán la calidad de datos rápidamente.
2.  **Momento Oportuno**: Estamos en fase Piloto (pocos datos). Una migración ahora es un script SQL sencillo. Postergado, será costoso.
3.  **Refactor Frontend Reciente**: El contexto de `ContactCanvas` está activo, reduciendo el esfuerzo cognitivo de la adaptación visual.

### Estimación de Complejidad
- **Nivel**: **MEDIA-ALTA (Arquitectura)** / **MEDIA (Implementación)**.
- **Tiempo Estimado**: 1 Sesión Focus (Backend Models + Migration + Frontend Adaptation).
