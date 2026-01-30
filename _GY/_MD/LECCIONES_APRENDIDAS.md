# 🦅 LECCIONES APRENDIDAS (Protocolo de Doctrina)

> **PROPÓSITO:** Este archivo contiene "Verdades Inmutables" destiladas de incidentes pasados. Su lectura es OBLIGATORIA para evitar errores recursivos.

---

## 💾 1. BASE DE DATOS E INTEGRIDAD
> **REGLA DE ORO:** **NO alterar la estructura física de tablas críticas por requerimientos cosméticos o de UI.**
> *   **Instrucción Precisa:** Ante la necesidad de guardar datos adicionales menores (ej: Piso, Depto, Color), priorizar SIEMPRE el uso de columnas JSON (`metadata`) o "Lógica de Fusión" (concatenar en campos de texto existentes) antes de agregar nuevas columnas físicas (`ALTER TABLE`).
> *   **Origen:** [Incidente del 23/01 - "Black Thursday" / Lazy Load Error](file:///c:/dev/Sonido_Liquido_V5/INFORMES_HISTORICOS/2026-01-23_PROTOCOLO_OMEGA_DOMICILIOS.md).
> *   **Consecuencia Evitada:** Rotura de serialización (Pydantic/SQLAlchemy conflicts) y crashes masivos (Error 500).

---

## 🎨 2. FRONTEND (VUE / UI)
> **REGLA DE ORO:** **Usar "Mounting Gates" para Teleports.**
> *   **Instrucción Precisa:** Al usar `<Teleport>`, envolverlo SIEMPRE en un `v-if="isMounted"` y activar esa variable solo en el hook `onMounted`.
> *   **Origen:** [Incidente del 24/01 - Teleport Race Condition](file:///c:/dev/Sonido_Liquido_V5/INFORMES_HISTORICOS/2026-01-24_PROTOCOLO_OMEGA_CLIENTES_SEC.md).
> *   **Consecuencia Evitada:** Crash de aplicación "Failed to locate Teleport target".

> **REGLA DE ORO:** **Contraste en Selects Nativos.**
> *   **Instrucción Precisa:** En modo oscuro/Chromium, los `<option>` pueden heredar fondo blanco con texto blanco. Solución Mandatoria: Usar siempre `class='text-black bg-white'` en las opciones.
> *   **Origen:** [Sesión del 29/01 - Dropdowns Invisibles](file:///c:/dev/Sonido_Liquido_V5/INFORMES_HISTORICOS/2026-01-29_SESION_CONTACT_CANVAS_FIX.md).

> **REGLA DE ORO:** **UX Unificada (Canvas vs Inspector).**
> *   **Instrucción Precisa:** Mantener consistencia visual absoluta entre el formulario de alta (modal) y la ficha de edición. Si el usuario aprende uno, ya sabe usar el otro. "Misma UI, Mismo Modelo Mental".

> **REGLA DE ORO:** **Una Planta = Un Cliente.**
> *   **Instrucción Precisa:** En clientes complejos (ej: Nestlé), separar las plantas como "Clientes" independientes simplifica drásticamente la operación táctica (envíos, horarios) frente a intentar modelar "Sedes" dentro de un mismo cliente maestro.

> **REGLA DE ORO:** **Affordance en Inputs.**
> *   **Instrucción Precisa:** Los títulos editables deben parecer editables (recuadro, fondo), no solo texto plano, para invitar a la acción sin ambigüedad.

> **REGLA DE ORO:** **Arquitectura de Drawers/Modales.**
> *   **Instrucción Precisa:** Componentes con `position: fixed` (paneles laterales, modales) deben ubicarse en la RAÍZ del `template` (fuera de contenedores con `overflow` o `transform`) para evitar problemas de `z-index` y recorte (`clipping`).
> *   **Origen:** [Sesión del 19/01 - Cost Drawer Invisible](file:///c:/dev/Sonido_Liquido_V5/INFORMES_HISTORICOS/2026-01-19_SESION_UI_FIXES.md).

---

## 🔌 3. API & BACKEND
> **REGLA DE ORO:** **Coherencia Estricta de Tipos de Retorno.**
> *   **Instrucción Precisa:** Si un endpoint dice crear un sub-recurso (ej: Domicilio), debe retornar ESE sub-recurso, NUNCA el padre (Cliente). El frontend no debe adivinar.
> *   **Origen:** [Incidente del 23/01 - Return Type Mismatch](file:///c:/dev/Sonido_Liquido_V5/INFORMES_HISTORICOS/2026-01-23_PROTOCOLO_OMEGA_DOMICILIOS.md).

---

## 🔒 4. SEGURIDAD & ADMIN TOOLS
> **REGLA DE ORO:** **Bypass de Heurística de Contraseñas (Stealth Mode).**
> *   **Instrucción Precisa:** Para inputs sensibles (PINs internos) que NO son login de usuario: Usar `type="text"` combinado con CSS `-webkit-text-security: disc;`. NO usar `type="password"`.
> *   **Origen:** [Sesión del 24/01 - Password Prompt Loop](file:///c:/dev/Sonido_Liquido_V5/INFORMES_HISTORICOS/2026-01-24_PROTOCOLO_OMEGA_CLIENTES_SEC.md).
> *   **Consecuencia Evitada:** El navegador acosa al usuario para "Guardar contraseña".

---

## 🌐 5. INFRAESTRUCTURA
> **REGLA DE ORO:** **Agnosticismo de Host (Proxy Friendly).**
> *   **Instrucción Precisa:** Usar SIEMPRE URLs relativas (`/api/...`) en el frontend. Prohibido hardcodear `localhost` o IPs en llamadas Axios.
> *   **Origen:** [Sesión del 20/01 - Estabilidad Sistema V1.3](file:///c:/dev/Sonido_Liquido_V5/INFORMES_HISTORICOS/2026-01-20_ESTABILIDAD_SISTEMA_V1_3.md).

---
**Última Actualización:** 2026-01-25 (Consolidación Protocolo Omega)

## [2026-01-28] BACKEND / ROUTING
1. **Trailing Slash Matter**: FastAPi es estricto. /contactos != /contactos/. Si el Store pide sin slash y hay redirección, puede perderse el contexto o fallar el proxy.
2. **SPA Catch-All Risks**: Si tienes un catch-all para servir index.html, DEBES excluir explícitamente todos los prefijos de API. De lo contrario, un 404 de API se convierte en un 200 OK con HTML, rompiendo el frontend silenciosamente.
3. **ORM Bidireccional**: SQLAlchemy requiere definir la relación en AMBOS lados (ack_populates) para que el mapper no explote. No basta con definirla en el hijo.
