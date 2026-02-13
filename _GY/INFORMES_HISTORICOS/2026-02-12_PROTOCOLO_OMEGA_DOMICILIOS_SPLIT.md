# REPORTE DE SESION: PROTOCOLO OMEGA (DOMICILIOS V7)

**Fecha:** 2026-02-12
**Operador:** Gy V14
**Estado:** MISIÓN CUMPLIDA (VERIFICADO)
**Rama Final:** `feature/v7-logistica-split`

## 1. Resumen Ejecutivo
Se ha completado la implementación de la **Arquitectura Split-View** para el módulo de Domicilios.
Esta actualización permite gestionar la complejidad logística de clientes corporativos (ej: Nestlé, Hospitales) separando la "Dirección Fiscal" (Facturación) de la "Dirección de Entrega" (Logística), sin corromper la integridad de datos ni requerir duplicación de clientes.

## 2. Intervenciones Críticas (Forensic Log)

### A. Base de Datos (Schema Evolution)
- **Eliminación de Deuda Técnica:** Se abandonó el uso de "Pipe Logic" (`Calle|Piso|Depto`) en favor de **Columnas Nativas SQL** (`piso`, `depto`).
- **Nuevos Campos Activos:**
    - `notas_logistica`: Instrucciones para choferes.
    - `maps_link`: Geolocalización.
    - `contacto_id`: Referencia a contacto logístico específico.
    - `calle_entrega`, `numero_entrega`, etc.: Espejo completo de dirección para casos Split.

### B. Migración de Datos (Data Rescue)
- Se ejecutó el script `scripts/migration_v7_domicilios.py`.
- **Resultado:** 100% de registros legacy analizados. Los datos "hackeados" con pipes fueron parseados y movidos a las nuevas columnas.

### C. Backend (Service Layer)
- `create_domicilio` y `update_domicilio` ahora escriben directamente en el nuevo esquema.
- **Seguridad:** Se mantiene compatibilidad de lectura para evitar crashes en módulos satélite no actualizados, pero la escritura es estricta V7.

### D. Frontend (UX)
- Implementado `DomicilioSplitCanvas.vue`.
- Visualización 50/50: Fiscal a la Izquierda (Solo Lectura/Fuente), Logística a la Derecha (Editable).
- Botonera de sincronización ("Copiar Fiscal") funcional.

## 3. Estado de Verificación
- **Tests Automatizados:** `tests/test_v7_functional.py` ✅ **PASSED**.
- **Pruebas Manuales:** Validación de persistencia de datos complejos (Piso, Depto, Notas).

## 4. Deuda Técnica Remanente (Orden D+1)
1.  **Limpieza:** Eventual remoción de código muerto referente a "Pipes" en el frontend legacy.
2.  **Merge:** Fusión de `feature/v7-logistica-split` a `develop` tras periodo de "Enfriamiento" (24hs).

## 5. Instrucción de Cierre
El sistema queda en estado **ESTABLE**. La próxima sesión debe centrarse en la integración de esta nueva logística en el `PedidoTacticoView` (visualización de iconos de entrega).

---
*Fin del Reporte.*
