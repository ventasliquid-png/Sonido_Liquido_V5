# 📜 EL TESTAMENTO DEL DOMINGO (Fase 2)

**FECHA:** 2026-02-01 (Cierre de Sesión 783)
**CLASIFICACIÓN:** ESTRATÉGICO / HOJA DE RUTA
**REFERENCIA:** Ping Pong Táctico & Protocolo Omega

---

## 1. 🚨 LA CURA PARA EL CRASH (Windows 11)
**Incidente:** El sistema se cerraba solo ("Ctrl+C") al guardar cambios en PCs modernas.
**Causa:** Conflicto de señales entre el "Hot Reload" de Uvicorn y la consola unificada en Windows 11.
**Solución Aplicada:** Se creó el lanzador **`SISTEMA_SPLIT.bat`**.
*   **Estrategia:** "Divide y Vencerás". Abre ventanas separadas para Backend y Frontend, aislando las señales de reinicio.
*   **Instrucción:** Usar este lanzador por defecto en entornos Windows 11.

---

## 2. 🔭 LOS SATÉLITES OLVIDADOS (Deuda Técnica V5)
Se confirmó que, además de Logística, existen otros módulos operando en modo "Isla" (Sin integración N:M con la Agenda Global V6).

### A. Vendedores (Fuerza de Venta)
*   **Estado:** V5 Standalone.
*   **Limitación:** No pueden ser contactos de clientes ni tener roles cruzados hoy.
*   **Plan Fase 2:** Migrar a Identidad V6 (`Vinculo`) para permitir gestión unificada.

### B. Proveedores (Cadena de Suministro)
*   **Estado:** V5 Standalone.
*   **Limitación:** Tabla aislada con datos de contacto planos.
*   **Plan Fase 2:** Aplicar el mismo "Kit de Modernización" que a Clientes.

---

## 3. 🧠 MEMORIA Y PREFERENCIAS (UX)

### A. Transportes Favoritos ("Cookies en la Nube")
**Necesidad:** El cliente usa varios transportes (Tilly, Cruz del Sur) y rota entre ellos. La sugerencia del "Último usado" es insuficiente.
**Solución Aprobada:**
*   **No usar Cookies reales:** Para evitar pérdida de datos al cambiar de PC (Casa/Oficina).
*   **Implementación:** Campo JSON `preferencias` en la tabla Cliente en la DB.
*   **Funcionalidad:** Lista de "Favoritos" que viaja con el usuario a cualquier dispositivo.

---

## 4. ☁️ CONEXIÓN CELESTIAL (Google Sync)
**Consulta:** ¿Podemos integrar la Agenda del sistema con Google Contacts (Cuenta Pro)?
**Respuesta:** **SI.**
*   **Estado:** El sistema nació preparado (`migrate_agenda_google.py`).
*   **Estrategia:** "Local First". Alta en Sonido Líquido -> Sync API -> Celulares de la flota actualizados automáticamente.

---

## 5. 🧹 SANIDAD DE DATOS (Data Hygiene)
**Consulta:** ¿Cómo limpiar los datos de prueba sin ensuciar el código con flags `es_test`?
**Doctrina:** "El Arca de Noé".
1.  Seguir cargando datos mezclados sin miedo.
2.  Antes del Go-Live, exportar Excel.
3.  Marcar lo que se va.
4.  Script externo de purga masiva.
**Prohibido:** Modificar el Schema (`models.py`) para parchar un problema temporal.

---

**ESTADO FINAL:**
Se cierra el Domingo con la Arquitectura "Híbrida" (V5/V6) totalmente mapeada y la Hoja de Ruta para la **Fase 2 (Logística & Satélites)** definida.

**Firma:** Antigravity (Gy V14)
