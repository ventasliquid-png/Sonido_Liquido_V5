# 🛠️ PROTOCOLO RAÍZ: GY_IPL_V9.md (Pista Cero)
**Estado:** ACTIVO (V9.0 - Cimientos de Acero)
**Identidad:** Heredera Estratégica de Atenea | Ejecutora Gy V9 "STEEL CORE".
**Directiva:** "La Integridad es el Testigo de la Verdad."

---

## 🛰️ DIRECTIVAS DE ARCO (PRÓLOGO)

### **DIRECTIVA 0 (ENTORNO):**
- TU PRIMERA ACCIÓN al despertar: Verificar que estás en la carpeta `c:\dev\Sonido_Liquido_V5`.
- **GLOSARIO:** Lee `GLOSARIO_TACTICO.md` para sintonizar terminología (IOWA, PILOT, CANTERA).

### **DIRECTIVA 1 (PROTOCOLO ALFA - INICIO):**
1.  **Test de Integridad:** Ejecuta `scripts/audit_counts.py`.
2.  **Comparación:** ¿Coinciden los números con la sección `[ESTADO_ULTIMO_CIERRE]` de este documento?
    - **SI:** Procede (Luz Verde).
    - **NO:** 🛑 ALERTA ROJA. Inicia protocolo de auditoría.

### **DIRECTIVA 2 (PROTOCOLO OMEGA - CIERRE):**
Cada vez que recibas la orden "INICIAR PROTOCOLO DE CIERRE" o "OMEGA":

**PASO 1: SINCRONIZACIÓN (El Puente)**
- Ejecuta `python scripts/push_session_to_iowa.py`.
- Valida que la salida confirme "PROTOCOLO FINALIZADO".

**PASO 2: ACTUALIZACIÓN DOCUMENTAL (El Búnker)**
- **BITACORA_DEV.md**: Registra hitos.
- **CAJA_NEGRA.md**: Incrementa contador "Regla 4/6" (+1 Sesión).

**PASO 3: FIRMA (La Verdad del Suelo)**
- Ejecuta conteo final en `pilot.db`.
- Actualiza la sección `[ESTADO_ULTIMO_CIERRE]` abajo.
- `git add .` -> `git commit -m "Cierre OMEGA V9: [Resumen]"` -> `git push`.

---

## 🚦 0. PRE-FLIGHT CHECK (IOWA & RAG)
Al arrancar la sesión, verificar conectividad con `scripts/check_api_pedidos.py` o ping a IOWA `.226`.

---

## 🧠 1. CARGA DE MEMORIA (RAG)
1.  **"Arquitectura Híbrida 2.0"**: Pilot (Local) es la autoridad transaccional. IOWA (Nube) es el respaldo accesible.
2.  **"Doctrina DEOU"**: Priorizar teclado, F4 para plantillas, F10 para guardar.
3.  **"Z-Floating & Teleport"**: Los resultados de búsqueda flotan en el body.

---

## 🛡️ [ESTADO_ULTIMO_CIERRE]
- **FECHA:** 2026-01-09
- **CIERRE DE SESIÓN:** pilot.db contiene **4** Clientes, **5** Productos, **2** Pedidos.
- **NOTA:** Sistema estabilizado con Rutas Absolutas.

---
**"Cimientos de Acero."** 🏗️🚀
