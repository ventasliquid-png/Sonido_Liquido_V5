# INFORME TÉCNICO: PROTOCOLO OMEGA - REFACTORIZACIÓN CLIENTES V5
**Fecha:** 2026-01-25
**Estado:** ÉXITO / ESTABLE
**Módulos Afectados:** ClientCanvas (Ficha), ClienteInspector (Alta), Logística.

---

## 1. Objetivo de la Sesión
Establecer una arquitectura de datos sólida ("Una Planta = Un Cliente") y unificar radicalmente la Experiencia de Usuario (UX) entre el formulario de Alta y la Ficha de Edición, priorizando la velocidad operativa y la claridad visual.

## 2. Definiciones de Arquitectura
*   **Modelo Multi-Planta:** Se validó que cada destino logístico (ej: Nestlé Firmat vs Nestlé Magdalena) opere como una entidad "Cliente" independiente para agilizar la logística táctica (horarios, contactos y recepciones específicas).
*   **Fiscalidad Flexible:** A pesar de ser clientes operativos distintos, el sistema permite definir un **Domicilio Fiscal** único y compartido, mientras mantiene direcciones de **Entrega** específicas para cada uno.

## 3. Refactorización UX (Layout V5.4)
Se aplicó un diseño espejo entre `ClienteInspector.vue` (Alta) y `ClientCanvas.vue` (Edición):

### A. Cabecera (Header)
*   **Izquierda:** Campo **Razón Social** exclusivo. Recuadrado, fondo oscuro y tipografía grande para máxima affordance (invitación a editar).
*   **Centro:** Título Institucional **"FICHA DE CLIENTE"** (o "FORMULARIO DE ALTA"). Color **Cyan Neon** (brillante) para jerarquía visual.
*   **Derecha:** Código Interno (`#`), Switch Operativo y botón Nuevo.

### B. Primera Fila (Datos Críticos)
El cuerpo principal se dividió en dos paneles de alta prioridad:
1.  **Domicilio Fiscal (Izquierda):**
    *   Bloque completo "Clickable" (Cursor pointer).
    *   Acceso directo a edición modal.
    *   Indicador de obligatoriedad (*).
2.  **Logística y Entrega (Derecha):**
    *   **Fantasía:** Integrado en la cabecera del bloque.
    *   **Entrega Principal:** Muestra la dirección real de descarga (o "Igual a Fiscal").
    *   **Transporte Habitual:** Selector rápido vinculado a la dirección de entrega.

---

## 4. Notas para Próxima Sesión (Mañana)
**Módulo Referencia:** Gestión de Contactos (Header)

*   **Ubicación:** Implementar botón/badge "Agenda" pegado al campo Razón Social en el header.
*   **Interacción:** Popover (lista flotante) para acceso rápido a teléfonos/mails sin ocupar el body.
*   **Integración:** Evaluar conexión con **Google Calendar/Contacts** como fuente de verdad para la agenda.

---
**Protocolo:** OMEGA (Sesión 782)
**Firmado:** Antigravity Agent (Google Deepmind)
