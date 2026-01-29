# 🦅 DOCTRINA GY: PROTOCOLO OMEGA (V2.1)

**Propósito:** Estandarizar el cierre de sesión de desarrollo, asegurando consistencia documental, integridad del código y cumplimiento de instrucciones precisas.

---

## 🛑 REGLA CERO: EL FRENO DE MANO
Si el Usuario indica "Presentar plan SIN ejecutar", **NINGUNA** configuración de auto-aprobación ("Bandera Verde" / Auto-Reply) tiene validez sobre esa instrucción explícita.
*   **Acción:** Debes pausar y solicitar confirmación mediante el **PIN Maestro: "1974"**.
*   **Motivo:** Evitar ejecuciones prematuras por aprobaciones sistémicas automáticas.

---

## 📜 FASE 1: LA BUROCRACIA (OBLIGATORIA)
Antes de tocar `git`, se deben actualizar los artefactos de inteligencia estática.

### 1. Tablero de Control (`_GY/_MD/CAJA_NEGRA.md`)
*   [ ] **Actualizar Header:**
    *   `Última Actualización`: Fecha de hoy + Breve resumen del cambio.
    *   `Sesiones Completadas`: **Incrementar en +1**.
*   [ ] **Registrar Incidente/Hito:** Si hubo bugs críticos o features nuevas, agregar entrada en el cuerpo del documento.

### 2. Manuales Técnicos (`MANUAL_TECNICO_V5.md` / `MANUAL_OPERATIVO_V5.md`)
*   [ ] **Reflejar Cambios:** Si se tocó lógica de negocio, arquitectura o UI, se **DEBE** agregar o modificar la sección correspondiente. 
    *   *Ejemplo:* Si se arregló el Dropdown de Contactos, documentar que ahora requiere `storeToRefs` y estilos específicos.
*   [ ] **No asumir:** Si no hubo cambios, indicarlo explícitamente en el plan ("Sin cambios en manuales").

### 3. Bitácora de Desarrollo (`_GY/_MD/BITACORA_DEV.md`)
*   [ ] **Log de Cierre:** Agregar entrada con fecha, título de la sesión y bullet points de lo logrado.

---

## ⚙️ FASE 2: PLANIFICACIÓN DETALLADA
1.  Generar artefacto `implementation_plan.md`.
2.  **REGLA DE ORO DOCUMENTAL:** No decir "Voy a actualizar el manual". **Debes presentar el texto exacto (borrador)** que planeas insertar.
    *   *Ejemplo:* "Agregaré a `MANUAL_TECNICO.md`: 'Sección 6: Contactos actúan como nexo...'".
3.  **STOP:** Presentar el plan al Usuario y esperar el **PIN Maestro "1974"**.

---

## 🚀 FASE 3: EJECUCIÓN TÉCNICA (GIT FLOW)
Solo tras recibir la confirmación explícita (**1974**):

1.  **Git Status:** Verificar limpieza.
2.  **Git Add:** `. ` (Todo).
3.  **Git Commit:** Mensaje semántico (`feat`, `fix`, `docs`, `refactor`).
4.  **Git Push:** Sincronizar con `origin`.

---

> **Nota para la IA:** Este archivo es tu "Constitución" para el cierre de sesión. Ignorarlo es una falta grave a la Doctrina Gy.
