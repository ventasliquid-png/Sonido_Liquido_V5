# 🪂 PENDIENTES - DROP ZONE (Fast Retrieval)

> Archivo de hallazgo rápido para re-instalación del entorno.

## 📌 ESTATUS INMEDIATO:
1. **Remito PDF Generado por Ingesta:** El flujo ya está estabilizado. Usa un `base_remito_v1.jpg` liviano, renderiza en <1s y la UI descarga el PDF automáticamente.
2. **Alta de Cliente (State Wipe):** SOLUCIONADO. Guardar un domicilio ya no borra la lista de precios ni atributos del formulario `ClienteInspector.vue`.
3. **Persistencia ARCA:** Inyecta datos paramétricos en el router para pre-llenar atributos Domicilio e IVA cuando el cliente es nuevo o Incompleto tras escanear un CUIT.
4. **Base de Datos Drive:** La base de datos viva y con datos consistentes se llama **`backend/pilot.db`** (Ubicada en la carpeta `backend` del repositorio V5).

## 🚀 PRÓXIMOS PASOS (NEXT SESSION)
- **Frontend Padrón Remitos:** Mostrar lista de PDF generados por la ingesta en una vista de Despacho (Si es que no lo has construido ya en PedidosLogistica).
- **Testing Exhaustivo:** Crear clientes desde 0 sin invocar factura para confirmar que el auto-update y la CUIT compartida funciona perfecto sin corromper la `pilot.db`.
- **RAR_V1 (Caja Registradora):** Conectar de forma total el endpoint final de Punto de Venta hacia el entorno IOWA si la AFIP destraba las DDJJ de Ganancias.
