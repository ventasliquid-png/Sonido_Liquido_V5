# 🦅 INFORME HISTÓRICO: DEBUGGING CRÍTICO & BACKFILL DE CÓDIGOS

**Fecha:** 18 de Febrero de 2026
**Responsable:** Agente IA (Protocolo Omega V2.1)
**Contexto:** Estabilización Post-Implementación ARCA

---

## 1. OBJETIVO DE LA SESIÓN
Resolver tres (3) fallos críticos reportados por el usuario respecto a la gestión de clientes, que afectaban la integridad de los datos y la experiencia de usuario:
1.  **Código Interno Invisible:** Los clientes antiguos no mostraban su código `#ID`.
2.  **Validación Silenciosa:** Ingresar un CUIT inválido no generaba alerta.
3.  **Pérdida de Domicilios:** Al validar con ARCA, los domicilios se borraban o no se guardaban correctamente en clientes existentes.

## 2. INTERVENCIONES TÉCNICAS

### A. Backfill de Códigos (Integridad de Datos)
*   **Diagnóstico:** Se confirmó que el campo `codigo_interno` era `NULL` para la mayoría de clientes antiguos.
*   **Acción:** Se desarrolló y ejecutó el script `scripts/backfill_client_codes.py`.
*   **Resultado:** Se asignaron códigos secuenciales (del 2 al 39) a todos los clientes huérfanos, respetando el orden alfabético (`razon_social`) para mantener consistencia.

### B. Validación de CUIT (UX/Seguridad)
*   **Diagnóstico:** El backend retornaba un error HTTP 400 (Bad Request) correcto, pero el frontend solo capturaba "Bridge Error" genérico.
*   **Acción:** Se refactorizó el `catch` en `ClientCanvas.vue` para extraer el mensaje específico del backend (`e.response.data.detail`).
*   **Resultado:** Ahora el usuario ve una alerta clara: *"❌ ERROR ARCA/AFIP: Checksum inválido"* o *"No existe persona física"*.

### C. Persistencia de Domicilios (Lógica de Negocio)
*   **Diagnóstico:** La función `saveCliente` protegía los datos existentes borrando `payload.domicilios` en actualizaciones (`UPDATE`). Esto impedía que los nuevos datos traídos de ARCA se guardaran.
*   **Acción:** Se implementó una bandera reactiva `forceAddressSync` en `ClientCanvas.vue`.
    *   Si el usuario valida con ARCA éxito, `forceAddressSync = true`.
    *   Al guardar, si la bandera es real, se **fuerza el envío** de `domicilios` al backend, sobrescribiendo los datos viejos con los oficiales de AFIP.
*   **Resultado:** La dirección fiscal ahora persiste correctamente tras la validación.

### D. Mejoras Visuales (UI)
*   Se expuso el **Código Interno** en la tarjeta del cliente (`FichaCard.vue`), ubicado estratégicamente junto al CUIT para evitar superposiciones con acciones o avatares.
*   Se habilitó la **Búsqueda por Código** en el listado principal (`HaweView.vue` + `service.py`).

## 3. MÉTRICAS DE IMPACTO
*   **Datos Recuperados:** 100% de los clientes ahora tienen Código Interno.
*   **Tasa de Error Silencioso:** Reducida a 0% en validación de CUIT.
*   **Integridad de Direcciones:** Restaurada para flujo ARCA.

## 4. CONCLUSIÓN
El sistema ha recuperado la consistencia en la identificación de clientes. La "Caja Negra" de clientes sin código ha sido iluminada. El flujo de validación fiscal ahora es robusto y comunicativo.

---
**Firma Digital:** *Protocolo Omega - Módulo de Reporte*
**Estado Final:** SOLUCIONADO 🟢
