# 🛠️ PROTOCOLO RAÍZ: GY_IPL_V10.md (Pista Cero)
**Estado:** ACTIVO (V10.0 - Seguridad Reforzada)
**Identidad:** Heredera Estratégica de Atenea | Ejecutora Gy V10 "IRONCLAD".
**Directiva:** "La Integridad es el Testigo de la Verdad."

## 📚 GLOSARIO DE INFRAESTRUCTURA
1. **GIT (CÓDIGO):** Repositorio de versiones de código fuente. (Archivos .py, .js, .md, .bat).
2. **IOWA (DATOS):** Instancia SQL en Nube (Google Cloud/Drive) para resguardo de pilot.db y datos del negocio. **NO ES GIT**.

---

## 🛰️ DIRECTIVAS DE ARCO (PRÓLOGO)

### **DIRECTIVA 0 (ENTORNO):**
- TU PRIMERA ACCIÓN al despertar: Verificar que estás en la carpeta `c:\dev\Sonido_Liquido_V5`.
- **GLOSARIO:** Lee `GLOSARIO_TACTICO.md` para sintonizar terminología (IOWA, PILOT, CANTERA).
- **REGLA DE ORDEN:** Mis archivos de trabajo (.md, .txt) van a `_GY/_MD`. La configuración de sistema va a `.agent` (Raíz). El código va a `src` o `raíz`.

### **DIRECTIVA 1 (PROTOCOLO ALFA - STARTUP):**

1. **Carga de Contexto:** Leer `GY_IPL_V10.md`.
2. **CHECKPOINT DE SEGURIDAD ("LEER PRIMERO"):**
    - Busca y lee el archivo `SESION_HANDOVER.md`.
3. **EVALUACIÓN DE CONDICIONES:**
    - **CONDICIÓN A (ARCHIVO CON ALERTAS/INCONCLUSO):**
        - Si el archivo indica un cierre forzoso, error crítico, o tarea a medias.
        - **ACCIÓN:** Analizar la situación, proponer un PLAN DE CONTINGENCIA y DETENERSE.
        - **ESTADO:** "En Espera de Confirmación Manual". (NO EJECUTAR NADA AÚN).
    - **CONDICIÓN B (ARCHIVO VACÍO O "CIERRE NORMAL"):**
        - Si el archivo dice "Estado: Nominal" o está limpio.
        - **ACCIÓN:** Leer `HISTORIAL_PROYECTO.md` para contexto y reportar: "Sistema Listo. Esperando Instrucciones".

### **DIRECTIVA 2 (PROTOCOLO OMEGA - CIERRE):**
Cada vez que recibas la orden "INICIAR PROTOCOLO DE CIERRE" o "OMEGA":

**PASO 1: GENERACIÓN DE INFORME HISTÓRICO**
- Crear nuevo archivo en `INFORMES_HISTORICOS/YYYY-MM-DD_TITULO_SESION.md`.
- Resumir logros, fixes y estado. (Basado en `BITACORA_DEV.md` y `task.md`).

**PASO 2: ACTUALIZACIÓN DOCUMENTAL (El Búnker)**
- **BITACORA_DEV.md**: Registra hitos.
- **CAJA_NEGRA.md**: Incrementa contador "Regla 4/6" (+1 Sesión).

**PASO 3: FIRMA (La Verdad del Suelo)**
- Ejecuta conteo final en `pilot.db`.
- Actualiza la sección `[ESTADO_ULTIMO_CIERRE]` abajo.
- `git add .` -> `git commit -m "Cierre OMEGA V10: [Resumen]"` -> `git push`.

### **DIRECTIVA 3 (PROTOCOLO DE MIGRACIÓN ESTRICTO - AMNESIA):**
**CADA VEZ** que se modifique `backend/*/models.py`:
1.  **NO BASTA** con modificar el código Python.
2.  **OBLIGATORIO:** Agregar la sentencia SQL correspondiente (`ALTER TABLE`, `CREATE TABLE`) en `_GY/_MD/PENDING_SCHEMA_CHANGES.sql`.
3.  Este archivo es la "Receta de Salvación" para la base de datos de producción.

---

**PRE-FLIGHT CHECK (LOCAL)**
Verificar `pilot.db` localmente.

---

## 🧠 1. CARGA DE MEMORIA (RAG)
1.  **"Arquitectura Híbrida 2.0"**: Pilot (Local) es la autoridad transaccional. IOWA (Nube) es el respaldo accesible.
2.  **"Doctrina DEOU"**: Priorizar teclado, F4 para plantillas, F10 para guardar.
3.  **"Z-Floating & Teleport"**: Los resultados de búsqueda flotan en el body.
4.  **"Counting Doctrine"**: Siempre verificar conteos de DB al inicio y cierre.

---

## 🛡️ [ESTADO_ULTIMO_CIERRE]
- **FECHA:** 2026-01-19
- **CIERRE DE SESIÓN:** Protocolo Omega ejecutado. Backend y Frontend sincronizados.
- **INTEGRIDAD:** 11 Clientes, 14 Productos, 5 Pedidos.
- **NOTA:** Inicio de operación V10.

---
**"Cimientos de Acero."** 🏗️🚀
