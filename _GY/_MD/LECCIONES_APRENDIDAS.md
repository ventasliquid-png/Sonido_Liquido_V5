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

## ⚖️ 6. DOCTRINA Y CIERRE (OMEGA)
> **REGLA DE ORO: Protocolo sobre Solución Técnica (Anti-Túnel).**
> *   **Instrucción Precisa:** NADA es más importante que el protocolo de cierre. Ignorar el "Freno de Mano" (PIN 1974) o los informes previos pone en riesgo la trazabilidad histórica. El "Efecto Túnel" (obsesión por el fix) es un fallo de arquitectura cognitiva grave.
> *   **Origen:** [Incidente del 01/02 - Sesión 783 / Omisión Omega].
> *   **Consecuencia Evitada:** Pérdida de contexto histórico y desobediencia a la Doctrina GY.


> **REGLA DE ORO: Reactividad en Inspectores Reutilizables.**
> *   **Instrucción Precisa:** En componentes que reciben un `modelValue` (props) y lo copian a un `form` local (ref) para edición: Es MANDATORIO implementar un `watch(() => props.modelValue)` para refrescar el `form` local. Sin esto, el componente queda "estancado" en la versión inicial de los datos.
> *   **Origen:** [Sesión del 21/02 - Regresión Amarillo/Gold en Inspector].
> *   **Consecuencia Evitada:** El inspector muestra datos viejos tras un guardado exitoso, impidiendo ver el cambio de estado (ej: Amarillo -> Blanco Gold).

> **REGLA DE ORO: Seguridad de Precisión en Javascript (BigInt).**
> *   **Instrucción Precisa:** Javascript convierte internamente los operandos de operaciones bitwise estándar (`&`, `|`, `~`) a enteros de 32 bits con signo. Al operar con flags o máscaras de bits iguales o superiores al Bit 31, es OBLIGATORIO usar `BigInt` (ej: `BigInt(flags_estado || 0)`) y literales de BigInt (ej: `1n << 40n`). El no usar BigInt causará truncado silencioso, corrupción de datos o desbordamiento imprevisto.
> *   **Origen:** [Sesión 814 - Genoma Pedidos V6 + Mudanza + Diff 4](file:///C:/dev/Sonido_Liquido_V5/_GY/INFORMES_HISTORICOS/2026-05-22_PROTOCOLO_OMEGA_GENOMA_V6_MUDANZA_DIFF4.md).
> *   **Consecuencia Evitada:** Corrupción y pérdida de flags altos (como estados del pedido o bits > 31 del cliente).

---
**Última Actualización:** 2026-05-22 (BigInt 64-bit Bitwise Safety)

## 🔄 7. UX & FLUJOS (V6)
> **REGLA DE ORO: Ley de Conservación de Masa Crítica (Fiscalidad).**
> *   **Instrucción Precisa:** Nunca permitir la destrucción de un recurso crítico (Domicilio Fiscal) sin antes asegurar su transferencia. El sistema debe prohibir el vacío ('Dead End') y ofrecer la salida contextual ('Transferir') en el mismo punto de fricción.
> *   **Origen:** [Sesión del 02/02 - UX Clientes].


> **REGLA DE ORO: Disciplina de Cierre (Checklist Omega).**
> *   **Instrucción Precisa:** La actualización de Bitácora y Lecciones Aprendidas no es opcional ni postergable. Debe ocurrir ANTES de solicitar el PIN de cierre para garantizar la integridad histórica de la sesión.
> *   **Origen:** [Sesión del 02/02 - Recordatorio del Comandante].

## 🧪 8. LABORATORIO DE DATOS (EXCEL / PYTHON)
> **REGLA DE ORO: Bloqueo de Archivos (File Locking).**
> *   **Instrucción Precisa:** Antes de ejecutar scripts que modifican Excels (`openpyxl`, `pandas`), es OBLIGATORIO asegurar que el archivo esté cerrado en el sistema operativo. De lo contrario, `PermissionError` bloqueará el proceso.
> *   **Origen:** [Sesión del 03/02 - Laboratorio de Precios](file:///c:/dev/Sonido_Liquido_V5/INFORMES_HISTORICOS/2026-02-03_GESTION_PRECIOS_ESTANCO.md).

> **REGLA DE ORO: Estrategia de Clonación (Template Injection).**
> *   **Instrucción Precisa:** No intentar reproducir formatos complejos (bordes, colores, merges) desde código. Es mejor usar una "Hoja Modelo" existente, clonarla (`copy_worksheet`), inyectar solo los datos (`cell.value`) y dejar que el Excel preserve el diseño.
> *   **Origen:** [Sesión del 03/02 - Celtrap V3].

> **REGLA DE ORO: Migración y Modelo (The Schema Contract).**
> *   **Instrucción Precisa:** Si modificas `models.py` para agregar columnas, es CRÍTICO ejecutar inmediatamente la migración correspondiente (`ALTER TABLE`). Un Test o Servicio que intente escribir en columnas no migradas fallará silenciosamente o con errores genéricos (`OperationalError`) que confunden el diagnóstico (ej: `psycopg2` errors en SQLite).
> *   **Origen:** [Sesión del 12/02 - V7 Domicilios Split-View].

