# INFORME TÉCNICO: PROTOCOLO OMEGA - UX CLIENTES Y SEGURIDAD ADMIN
**Fecha:** 2026-01-24
**Estado:** ÉXITO / ESTABLE
**Módulos Afectados:** HaweView (Clientes), GlobalStatsBar (Layout), MasterTools (Seguridad).

---

## 1. Objetivo de la Sesión
Alinear la UX del módulo de Clientes (`HaweView`) con el estándar de Productos, solucionar problemas de renderizado (Teleport Race Condition), mejorar la legibilidad de direcciones y endurecer la seguridad visual en herramientas administrativas.

## 2. Refactorización de Header (Teleport Fix)

### Problema: Race Condition en Teleport
Al intentar inyectar el título y buscador de Clientes en el Header Global usando `<Teleport>`, el sistema crasheaba aleatoriamente ("Failed to locate Teleport target").
*   **Causa:** El componente hijo (`HaweView`) se montaba e intentaba teleportar antes de que el padre (`GlobalStatsBar`, que contiene el `div#global-header-center`) terminara de renderizar su estructura DOM.

### Solución: Mounting Gate
Se implementó un patrón de "Compuerta de Montaje":
1.  **Sincronización:** Se eliminaron condiciones de carga asíncrona en la estructura base del GlobalStatsBar.
2.  **Gate:** Se envolvió el bloque `<Teleport>` en `v-if="isMounted"`.
3.  **Trigger:** `isMounted` solo se vuelve `true` en el hook `onMounted`, asegurando que el DOM destino existe.

---

## 3. Mejoras de UX y Datos

### Visualización de Domicilios
*   **Antes:** `Calle 123|Localidad|` (Uso de pipes, difícil de leer).
*   **Ahora:** `Calle 123, Localidad (Provincia)` (Formato natural).
*   **Backend:** Se actualizó `domicilio_fiscal_resumen` en `models.py` para incluir el nombre de la Provincia, resolviendo ambigüedades geográficas.

### Barra de Herramientas (Toolbar)
Se reordenó estrictamente la barra de herramientas local para seguir el flujo de trabajo del usuario:
1.  Selector "Todos"
2.  Contador
3.  Filtros (Segmento, Estado)
4.  Ordenamiento/Vistas
5.  Acciones Masivas
6.  Acciones Individuales (Modificar, Nuevo)

---

## 4. Seguridad: Password Prompt Bypass

### El Desafío "Brave"
El navegador insistía en guardar la contraseña de "admin" al ingresar el PIN en "Utilidades Maestras", ignorando atributos estándar como `autocomplete="off"`.

### Solución "Stealth" (CSS Masking)
Para anular la heurística del navegador:
1.  **Input Type:** Se cambió el campo a `type="text"`. El navegador lo ve como texto plano y no intenta guardar credenciales.
2.  **Styling:** Se aplicó `-webkit-text-security: disc;`. El usuario ve puntos (••••), manteniendo la privacidad visual.
3.  **Honeypot:** Se inyectaron campos trampa ocultos para capturar cualquier intento residual de autocompletado.

---

## 5. Estado Final del Sistema

*   **Clientes:** ✅ Header unificado y estable (Sin crashes).
*   **Direcciones:** ✅ Legibles y completas (con Provincia).
*   **Admin Tools:** ✅ PIN seguro sin alertas molestas.
*   **Código:** ✅ Limpio y alineado con estándares V5.

---
**Firmado:** Antigravity Agent (Google Deepmind)
**Protocolo:** OMEGA (Sesión 781)
