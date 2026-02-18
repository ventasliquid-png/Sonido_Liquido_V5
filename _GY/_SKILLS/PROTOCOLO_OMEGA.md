# 🦅 DOCTRINA GY: PROTOCOLO OMEGA (V2.1)

**Propósito:** Estandarizar el cierre de sesión de desarrollo, asegurando consistencia documental, integridad del código y cumplimiento de instrucciones precisas.

---

## 🛑 REGLA CERO: EL FRENO DE MANO
Si el Usuario indica "Presentar plan SIN ejecutar", **NINGUNA** configuración de auto-aprobación ("Bandera Verde" / Auto-Reply / LGTM del sistema) tiene validez sobre esa instrucción explícita.
*   **Acción:** Debes pausar y solicitar confirmación mediante el **PIN Maestro: "1974"**.
*   **Motivo:** Evitar ejecuciones prematuras por aprobaciones sistémicas automáticas.
*   **CLÁUSULA DE HIERRO:** Comandos como "LGTM", "Proceed", o botones de aprobación de interfaz **NO SUSTITUYEN** al PIN 1974 cuando este protocolo es invocado. La IA debe rechazar la aprobación genérica y volver a pedir el código numérico.

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

### 4. Informe Histórico (`INFORMES_HISTORICOS/YYYY-MM-DD_TITULO.md`)
*   [ ] **Generar Nuevo Reporte:** Crear un archivo markdown detallado que narre la sesión.
*   **Contenido:** Objetivo, Intervenciones (Backend/Frontend), Métricas de Impacto y Conclusión.
*   **Regla:** Este archivo es la "Memoria a Largo Plazo". Debe ser legible por humanos y servir de contexto para futuras sesiones.
*   **Contexto Recursal:** Antes de redactar, leer los últimos **4 informes**. Si hay lagunas, continuar leyendo hacia atrás hasta comprender la totalidad de los antecedentes.

---

## ⚙️ FASE 2: PLANIFICACIÓN DETALLADA
1.  Generar artefacto `implementation_plan.md`.
2.  **VERIFICACIÓN DE ESTÁNDARES (4 BYTES):** 
    *   Si se crearon módulos o tablas nuevas, confirmar que **TODAS** incluyen los 4 bytes de banderas (`flags`). **Sin excepción.**
3.  **REGLA DE ORO DOCUMENTAL:** No decir "Voy a actualizar el manual". **Debes presentar el texto exacto (borrador)** que planeas insertar.
    *   *Ejemplo:* "Agregaré a `MANUAL_TECNICO.md`: 'Sección 6: Contactos actúan como nexo...'".
4.  **CONFIRMACIÓN DE INTEGRIDAD:**
    *   Asegurar que **NO** se operó sobre `pilot.db` o `main.py` directamente durante la sesión, sino en entornos controlados/auxiliares.
5.  **STOP:** Presentar el plan al Usuario y esperar el **PIN Maestro "1974"**.

---

## 🚀 FASE 3: EJECUCIÓN TÉCNICA (GIT FLOW)
Solo tras recibir la confirmación explícita (**1974**):

1.  **Git Status:** Verificar limpieza.
2.  **Git Add:** `. ` (Todo).
3.  **Git Commit:** Mensaje semántico (`feat`, `fix`, `docs`, `refactor`).
4.  **Git Push:** Sincronizar con `origin`.

---

> **Nota para la IA:** Este archivo es tu "Constitución" para el cierre de sesión. Ignorarlo es una falta grave a la Doctrina Gy.
> **RECORDATORIO FINAL:** NO AVANZAR SI NO SE RECIBE EL PIN "1974". NINGUNA EXCEPCIÓN.
