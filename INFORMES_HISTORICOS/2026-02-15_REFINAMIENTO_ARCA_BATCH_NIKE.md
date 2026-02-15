# INFORME DE REFINAMIENTO DE SISTEMA (ARCA / BATCH / UX)
**Para:** Nike (IA Arquitecta)
**De:** Módulo Operativo V5 (Gy)
**Fecha:** 2026-02-15
**Asunto:** Consolidación de Validación Fiscal (ARCA) y Refinamiento de UX

## 1. Resumen Ejecutivo
Se ha completado con éxito la integración del "Puente ARCA" (RAR-V5), habilitando la validación fiscal tanto interactiva (Alta de Clientes) como masiva (Batch Script). Se han resuelto limitaciones de UX críticas y se ha establecido una lógica de preservación de datos para casos complejos (UPEs, Sucursales).

## 2. Operaciones SQL y Estructura de Datos
No se realizaron cambios estructurales (DDL) en esta sesión, pero si operaciones DML masivas y lógicas de integridad:

### A. Validación Masiva (`validate_arca_batch.py`)
- **Objetivo:** Sincronizar el estado fiscal de la base instalada (`pilot.db`) con ARCA.
- **Lógica:**
    - Se iteró sobre clientes con `estado_arca != 'VALIDADO'`.
    - Se utilizó `AfipBridgeService` para consultar a RAR V1.
    - **Resultado:** 26+ Clientes validados y normalizados.

### B. Lógica de Preservación (Caso UBA / Sucursales)
Se detectó que entidades como "UBA" comparten un único CUIT ("Universidad de Buenos Aires") para múltiples facultades.

> **Nota de Coherencia:** Esta implementación ejecuta la visión del "Caso Nestlé" (Unidades de Negocio) planificada en el informe *2026-02-04_PLAN_TECNICO_SPLIT_V7.md*.

- **Regla Implementada:**
    - Si `razon_social` local es específica (ej: "Facultad de Medicina") y diferente de la legal (ARCA), **SE MANTIENE** la local.
    - Se actualiza solo `estado_arca`, `condicion_iva` y `domicilio_fiscal`.
    - Esto evita la "homogeneización destructiva" de sucursales.

## 3. Refinamiento de UX (ClientCanvas.vue)
Se pulió la experiencia de usuario en el "Formulario de Alta" para eliminar fricción:

1.  **Enfoque Automático:** Implementado `nextTick` + `setTimeout` para forzar el foco en el campo CUIT al abrir el modal.
2.  **Eliminación de Redundancia:** Removido el input CUIT del cuerpo del formulario (ahora solo en Header).
3.  **Auto-Completado IVA (Fuzzy Logic):**
    - Mapeo inteligente de strings de ARCA ("RESPONSABLE INSCRIPTO") a IDs locales.
    - Soporta variaciones y coincidencia parcial.
4.  **Detección de Duplicados:**
    - Antes de llamar a ARCA, se verifica si el CUIT ya existe en `pilot.db`.
    - **Alerta:** "Este CUIT ya existe para [Nombre]".
    - **Opción:** Permite crear nuevo (para sucursales) o cancelar.

## 4. Conclusiones y Estado Final
El módulo de Clientes ha alcanzado un nivel de madurez "V6.3", con capacidad de autogestión fiscal y ergonomía de alta velocidad.

---
**Firma Digital:** Gy V14
**Hash de Operación:** PRE-OMEGA-VERIFIED
