# INFORME HISTÓRICO: SESIÓN LOGÍSTICA TÁCTICA V7 (SPLIT)

**Fecha:** 2026-02-04
**Foco:** Logística Táctica, Arquitectura de Remitos, Limpieza Legacy.
**Resultado:** ÉXITO (Protocolo Omega Ejecutado).

## 🎯 OBJETIVO ESTRATÉGICO
Implementar soporte para **"Split Orders"** (Entregas Parciales), superando la limitación "1 Pedido = 1 Transporte". Se requería una solución que permitiera asignar mercadería a diferentes viajes sin romper la integridad financiera (Reserva de Stock) ni operativa (Descuento de Stock Físico).

## 🛠️ INTERVENCIONES

### 1. Backend (Core V7)
*   **Nueva Arquitectura:** Implementados modelos `Remito` y `RemitoItem`.
*   **Lógica de Stock ("Gato de Schrödinger"):**
    *   `Pedido`: Reserva stock virtual (`stock_reservado`).
    *   `Remito`: Al despachar, decrementa `stock_reservado` y `stock_fisico`.
*   **Endpoints:** `POST /remitos/`, `POST /remitos/{id}/items` (hotfix), `POST /despachar`.

### 2. Frontend (UX LogisticaSplitter)
*   **Dashboard Bipanel:**
    *   **Izquierda:** Pool de Pendientes con barra de progreso.
    *   **Derecha:** Tarjetas de Remitos Activos.
*   **Drag & Drop:** Interacción fluida para asignar ítems.
*   **Gatekeeper Visual:** Alerta si el pedido no está liberado financieramente (`liberado_despacho`).
*   **Branding:** Template de impresión HTML/PDF con datos legales.

### 3. Limpieza Forense (V5 Legacy)
*   **Auditoría:** Se detectó referencia muerta a `tipo_entrega` en `excel_export.py`.
*   **Reparación:** Se implementó lógica dinámica ("Multiplex") para informar en el Excel si la logística es simple o compleja, garantizando que la "red de seguridad" siga funcionando.

## 📊 MÉTRICAS DE IMPACTO
*   **Seguridad de Stock:** Control absoluto de lo reservado vs entregado.
*   **Flexibilidad:** Un pedido ahora puede despachar 10 cajas por "La Sevillanita" y 5 por "Retira Cliente".
*   **Integridad de Datos:** Eliminado riesgo de error 500 en exportación.

## 📝 CONCLUSIÓN
El sistema ha evolucionado de un modelo logístico monolítico a uno fragmentado (Split), alineándose con la realidad operativa de múltiples puntos de entrega. La base está lista para la fase de "Agenda Global N:M".
