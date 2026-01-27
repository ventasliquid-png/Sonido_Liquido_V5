# INFORME TÉCNICO: PROTOCOLO ALFA (CORRECCIÓN) - CONTACTOS Y TRANSPORTES
**Fecha:** 2026-01-27
**Estado:** CORREGIDO / VERIFICADO
**Incidente:** Cierre prematuro de misión sin validación de persistencia.

---

## 1. Diagnóstico del Fallo (Transport Persistence)
*   **Síntoma:** El transporte seleccionado en "Agenda Rápida" (Header) no se guardaba consistentemente.
*   **Causa Raíz:**
    *   **Frontend:** Selecciona el transporte basándose en el primer domicilio disponible (`domicilios[0]`) si no hay uno específico de entrega/fiscal.
    *   **Backend (`update_cliente`):** Solo actualizaba domicilios con flag explícito `es_entrega` o `es_fiscal`. Si el cliente no tenía esos flags (datos legacy o incompletos), el backend creaba un **nuevo domicilio duplicado** en lugar de actualizar el existente.
*   **Consecuencia:** El usuario veía el dato guardado (en el nuevo domicilio oculto), pero la UI, al recargar, mostraba el domicilio original sin cambios.

## 2. Corrección Implementada
Se modificó `backend/clientes/service.py` para alinear la lógica de selección de domicilio con la del Frontend:

1.  **Prioridad 1:** Buscar Domicilio con `es_entrega=True`.
2.  **Prioridad 2:** Buscar Domicilio con `es_fiscal=True`.
3.  **Prioridad 3 (Nueva):** Buscar **cualquier** Domicilio activo (`db_cliente.domicilios[0]`).
4.  **Último Recurso:** Solo crear uno nuevo si la lista de domicilios está vacía.

Esta lógica asegura que la "edición rápida" desde el header impacte siempre al domicilio visible.

---

## 3. Estado de Misión: CONTACTOS (AGENDA)
Además de la corrección, se validó la implementación de:
*   **Botón Agenda:** Operativo y visible en Header.
*   **Popover:** Muestra vínculos y permite copiar datos.
*   **Google Mock:** Endpoint `/sync` operativo para simulaciones locales.

---
**Firmado:** Antigravity Agent (Gy Sentinel V14)
**Protocolo:** ALFA (Restauración de Identidad)
