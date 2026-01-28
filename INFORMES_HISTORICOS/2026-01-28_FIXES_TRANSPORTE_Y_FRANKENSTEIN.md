# INFORME DE SESIÓN: 2026-01-28 (FIXES TRANSPORTE Y FRANKENSTEIN)

**Fecha:** 28 de Enero de 2026
**Operador:** GY (AI Agent) / Usuario
**Estado:** NOMINAL (Cierre Exitoso)

## 1. Resumen Ejecutivo
Se abordó y resolvió un problema crítico de persistencia en la asignación de transportes para los clientes. Adicionalmente, se realizó una refactorización mayor ("Frankenstein Cleanup") del componente `ClientCanvas.vue` y se simplificó la interfaz de usuario para evitar futuros conflictos de datos.

## 2. Problemas Detectados

### A. Persistencia de Transporte ("El Fantasma de Alberto")
- **Síntoma:** Al cambiar el transporte de un domicilio (ej. de "Alberto" a "Expreso Damonte"), el cambio no persistía al recargar la página, a pesar de que el servidor retornaba 200 OK.
- **Causa Raíz:** Conflicto de datos en el backend (`backend/clientes/service.py`). El modelo `Domicilio` tiene dos campos: `transporte_id` (Empresa) y `transporte_habitual_nodo_id` (Nodo Legacy). Al actualizar solo la Empresa, el Nodo Legacy ('Alberto') permanecía activo y sobrescribía la selección al recargar.
- **Solución:** Se aplicó un parche en el servicio (`[GY-FIX-V5]`) que limpia explícitamente el `transporte_habitual_nodo_id` cuando se detecta una actualización de `transporte_id`.

### B. Código "Frankenstein" en ClientCanvas
- **Síntoma:** El archivo `ClientCanvas.vue` contenía código muerto, imports no utilizados (`SegmentoForm`) y lógica de negocio dispersa y redundante, dificultando el mantenimiento.
- **Solución:** Limpieza profunda del archivo. Se reescribió la función `handleDomicilioSaved` para centralizar las Reglas de Negocio (Leyes de Conservación Fiscal y Protocolos de Seguridad) en un flujo lineal y legible.

### C. UX Confusa en Selección de Transporte
- **Síntoma:** Existían dos selectores de transporte (uno en la tarjeta, otro en el modal), lo que confundía al usuario sobre cuál era la fuente de verdad.
- **Solución:** Se eliminó el selector rápido de la tarjeta. Se implementó un **Menú Contextual (Click Derecho)** sobre la dirección de entrega para gestionar "Alta", "Baja" y "Modificación", forzando el uso del modal oficial y garantizando la integridad de los datos.

## 3. Cambios Técnicos Relevantes

### Backend
- **`backend/clientes/service.py`**:
    - Patch `update_domicilio`: Auto-nulificar nodo legacy.

### Frontend
- **`src/views/Hawe/ClientCanvas.vue`**:
    - Eliminado `SmartSelect` de la UI principal.
    - Implementado `openAddressContextMenu` con opciones CRUD.
    - Refactor `handleDomicilioSaved` (Bloques lógicos claros).
    - Restaurado `loadCliente()` tras guardado para consistencia visual.
- **`src/views/Hawe/components/DomicilioForm.vue`**:
    - Verificación de binding de datos (OK).

## 4. Estado Final
- El sistema guarda y persiste correctamente los cambios de transporte.
- La interfaz es más limpia y estricta (Padre-Hijo).
- El código base ha reducido su deuda técnica.

---
**Firma Digital:** GY-V10-OMEGA
