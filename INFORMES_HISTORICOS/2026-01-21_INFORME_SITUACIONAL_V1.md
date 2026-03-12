# Informe Situacional V5 - Simulación de Sistema

**Fecha:** 21/01/2026
**Responsable:** Gy V10 "IRONCLAD"

## 1. Resumen Ejecutivo
Se ha realizado una simulación completa del sistema "Sonido Líquido V5", recorriendo los módulos principales (Clientes, Productos, Pedidos) y verificando la integridad de los flujos de datos y la interfaz de usuario.

**Estado General:** **OPERATIVO / ESTABLE**
El núcleo transaccional (Pedidos) funciona correctamente, incluyendo la creación táctica y la edición con recuperación de datos (hidratación corregida).

## 2. Auditoría de Módulos (ABM)

### 🟢 Módulo Clientes (`HaweClientCanvas.vue`)
- **Estado:** Operativo.
- **Funcionalidades Verificadas:**
    - Alta/Edición: Funcional (Ventana Satélite 1700px).
    - Validaciones: Activas (CUIT, Cond. IVA).
    - Integración Logística: Domicilios y Transportes se cargan correctamente.
    - **Observación:** La interfaz "Tokyo" está implementada y es consistente.

### 🟢 Módulo Productos (`ProductosView.vue`)
- **Estado:** Operativo.
- **Funcionalidades Verificadas:**
    - Listado: Grilla dinámica con filtros y ordenamiento.
    - Cantera: Integración para importar productos desde la nube activa.
    - Edición: Ventana satélite funcional.

### 🟢 Módulo Pedidos (`PedidoList.vue` -> `PedidoCanvas.vue`)
- **Estado:** Operativo (Con corrección reciente).
- **Flujo Simulado:**
    1.  **Creación:** POST correcto a `/pedidos/tactico`. Se guardan `domicilio_entrega_id` y `transporte_id`.
    2.  **Listado:** Muestra los pedidos correctamente.
    3.  **Edición:** `PedidoCanvas` hidrata correctamente los ítems, incluyendo descuentos (`descuento_porcentaje`, `descuento_importe`) y la selección logística específica del pedido.
    4.  **Logística:** La lógica de listeners (`watch`) en el frontend setea correctamente los defaults del cliente, pero la hidratación (`loadPedido`) sobreescribe con los datos reales del pedido si existen. **FIX VERIFICADO.**

### 🟡 Módulos Secundarios & Mockups Detectados
- **Segmentos (`SegmentoList.vue`)**: Operativo. CRUD básico funcional.
- **Rubros (`RubrosView.vue`)**: Operativo. Flat View funcional.
- **Agenda (`ContactosView.vue`)**: Operativo. Sidebar y filtros activos.
- **Inspector Panel (`InspectorPanel.vue`)**: **MOCKUP DETECTADO.**
    - Este componente (`src/components/canvas/InspectorPanel.vue`) tiene data estática ("María González", "Via Cargo", Saldos $0.00).
    - Se usa actualmente como panel lateral en algunas vistas (ej. `ClientCanvas` zone 2, aunque en el código analizado de `ClientCanvas` parece estar comentado o reemplazado por `live-audit`).
    - **Acción Recomendada:** Si se planea usar, debe conectarse a `store` real. Si no, marcar como Deprecated.

## 3. Estado de Base de Datos (Modelos)
- **Pedidos (`backend/pedidos/models.py`)**: Schema V5.6 correcto. Soporta `domicilio_entrega_id` y `descuento_global`.
- **Integridad:** Las relaciones (ForeignKeys) están bien definidas.

## 4. Conclusiones y Próximos Pasos
El sistema está listo para operación real en sus circuitos principales.
El "Ciclo de Vida del Pedido" está cerrado y verificado.

**Sugerencias:**
1.  **Limpieza:** Definir el destino de `InspectorPanel.vue` (Conectar o Borrar).
2.  **Dashboard:** El inicio (`HaweView.vue`) es el próximo candidato lógico para revisión si se busca impacto visual inmediato.

---
**Firma:** Gy V10 "IRONCLAD"
