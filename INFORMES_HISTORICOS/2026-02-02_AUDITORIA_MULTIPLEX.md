# AUDITORÍA ESTRATÉGICA DE ARQUITECTURA MULTIPLEX (N:M)

**PARA:** Nike P / El Comandante  
**DE:** Antigravity (Gy V14)  
**FECHA:** 2026-02-02  
**ASUNTO:** ESTUDIO DE VIABILIDAD - MATRIZ DE NODOS

---

## 1. RESUMEN EJECUTIVO (CUADRO DE SITUACIÓN)

La arquitectura actual (V5/V6 Híbrida) presenta una **capilaridad desigual**. Mientras "La Hidra" (Contactos) ya opera en una matriz N:M real, la logística física (Domicilios y Transportes) sigue atada a un modelo jerárquico rígido (1:N).

| ENTIDAD | ESTADO | TIPO | CAPACIDAD N:M | BRECHA |
| :--- | :---: | :---: | :---: | :--- |
| **CONTACTOS** | 🟢 | Multiplex | **TOTAL** | **Ninguna.** El modelo `Vinculo` Polimórfico soporta Roles múltiples (Vendedor, Cobrador) y canales contextuales. |
| **DIRECCIONES** | 🔴 | Jerárquico | **NULA** | **Crítica.** Los domicilios son propiedad exclusiva del Cliente. No existe una "Agenda Global" de direcciones reutilizables. |
| **TRANSPORTE** | 🟡 | Hub & Spoke | **PARCIAL** | **Media.** Existe modelo de Nodos, pero el Pedido solo admite **1 (UN)** Transporte. No hay soporte nativo para "Cadena de Custodia" (A -> B -> C). |
| **DEPÓSITOS** | 🟠 | Definido | **LATENTE** | **Alta.** La entidad `Deposito` existe, pero **NO** tiene vinculación con `Producto`. El Stock es global/implícito. |
| **PROVEEDORES** | 🟢 | Satélite | **ALTA** | **Baja.** `ProductoProveedor` permite N proveedores por producto con costos diferenciados. |

---

## 2. ANÁLISIS DE BRECHAS Y SOLUCIONES

### A. CONTACTOS (LA HIDRA) - EL MODELO A SEGUIR
La infraestructura ya existe en `backend/contactos/models.py`.
*   **Capacidad Actual:** Un `Vinculo` puede ser `CLIENTE`, `PROVEEDOR`, `TRANSPORTE` o `VENDEDOR`.
*   **Cobrador Rígido:** **VIABLE HOY.**
    *   *Implementación:* Asignar el Rol "COBRADOR" a un vínculo específico. Frontend filtra estos vínculos. Logística consulta este rol antes de liberar.

### B. DIRECCIONES (NODOS DE ENTREGA) - EL CUELLO DE BOTELLA
El modelo `Domicilio` tiene un `ForeignKey("clientes.id")` obligatorio.
*   **Problema:** Si dos clientes comparten depósito (ej: Shopping, Parque Industrial), se duplica la data.
*   **Solución N:M:** Crear entidad `NodoLogistico` (Global) y que `Domicilio` sea solo la relación (`Cliente` <-> `NodoLogistico`).
*   **Esfuerzo:** **ALTO (Refactor Estructural).** Requiere migración masiva de datos.

### C. CASO DE PRUEBA 1: "COBRADOR RÍGIDO"
*Desafío: Bloquear logística hasta validación de pago por nodo específico.*
**SOLUCIÓN PROPUESTA (Low Code):**
1.  **Entidad:** Usar `Vinculo` con rol `COBRADOR`.
2.  **Pedido:** Agregar campo `cobrador_asignado_id` (Vínculo) y `estado_cobranza` (PENDIENTE/APROBADO).
3.  **Gatekeeper:** El módulo de Logística verifica `if pedido.estado_cobranza != 'APROBADO': RAISE LOCK`.

### D. CASO DE PRUEBA 2: "REPARTO LABME" (1 Factura -> N Destinos)
*Desafío: Logística fraccionada multipunto.*
**SITUACIÓN ACTUAL:** IMPOSIBLE. Un `Pedido` tiene un único `domicilio_entrega_id`.
**SOLUCIÓN:**
1.  **Opción A (Split):** Dividir el Pedido Padre en N Sub-Pedidos (Remitos) vinculados. Cada uno viaja a un destino.
2.  **Opción B (Complex):** Crear tabla `EntregasPedido` (Pedido 1 -> N Entregas).
*   *Recomendación:* **Opción A**. Mantiene la integridad del modelo actual de "1 Pedido = 1 Viaje".

---

## 3. PLAN DE ACCIÓN (HOJA DE RUTA)

### FASE 1: ACTIVACIÓN TÁCTICA (Inmediato)
1.  **Cobrador Rígido:** Implementar lógica de bloqueo en Backend basada en Roles de Vínculos V6.
2.  **Depósitos:** Conectar `Producto` con `Deposito` mediante tabla pivot `Stock` (Producto ID, Deposito ID, Cantidad).

### FASE 2: TRANSFORMACIÓN DE ESTRUCTURA (Mediano Plazo)
3.  **Globalización de Direcciones:** Extraer `calle, numero, localidad` a entidad `UbicacionGeografica`.
4.  **Cadena de Custodia:** Modificar `Pedido` para soportar `TrayectoLogistico` (Lista de Transportes).

### CONCLUSIÓN
El sistema tiene un "Cerebro" (Contactos) preparado para el futuro, pero un "Cuerpo" (Logística) anclado en el pasado. La prioridad debe ser **desacoplar el Stock de la existencia global y permitir Múltiples Destinos por Venta mediante Split de Remitos.**

**Firma:**
*Antigravity Unit - V14 Core*
