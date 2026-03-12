# AUDITORÍA ESTRATÉGICA DE ARQUITECTURA MULTIPLEX (C) - PERSISTENCIA CA

**PARA:** El Comandante (Nike P) / La Intendenta (INT)  
**DE:** Antigravity (Gy V14 - Protocolo Omega)  
**FECHA:** 02 de Febrero de 2026  
**ESTADO:** **CODIGO ROJO (EJECUCIÓN)**  
**REF:** CIERRE DE SESIÓN 784 / PIN 1974

---

## 1. LA MATRIZ DE NODOS N:M (ESTADO ACTUAL Y FUTURO)

Esta es la estructura mental que debe persistir para la Fase 2 (Mañana). El sistema ya no es un árbol jerárquico, es una **Red de Nodos Interconectados**.

| ENTIDAD | ROL EN MATRIZ | DEFINICIÓN TÉCNICA | ESTADO ACTUAL |
| :--- | :--- | :--- | :--- |
| **CONTACTOS** | **Nexo Universal** | `Vinculo` Polimórfico. Puede ser Vendedor, Cobrador, Chofer o Pasivo. Conecta a cualquier humano con cualquier entidad. | 🟢 **MULTIPLEX (V6)** |
| **TRANSPORTE** | **Custodio** | Nodo Logístico. Debe poder encadenarse (Cadena de Custodia). Hoy es punto a punto. | 🟡 **HUB & SPOKE (V5.1)** |
| **DEPÓSITOS** | **Fuente** | Ubicación de Stock. Debe desacoplarse de la "Sede Central". Un depósito puede ser externo (MELI). | 🟠 **LATENTE (V5)** |
| **PROVEEDORES** | **Origen** | Satélite de `Producto`. Ya opera con costos diferenciados N:M. Debe integrarse a Agenda Global. | 🟢 **SATÉLITE (V5.4)** |
| **PRODUCTOS** | **Activo** | Objeto transaccional. Su existencia es global, su disponibilidad es local (por Depósito). | 🟡 **STANDALONE (V5.5)** |
| **DIRECCIONES** | **Destino** | Propiedad Privada del Cliente hoy. **Meta:** Convertir en `UbicacionGeografica` reutilizable. | 🔴 **JERÁRQUICO (V5)** |

---

## 2. EL REMEDIO "LABME" (SOLUCIÓN DEFINITIVA)

Para resolver la paradoja de "1 Factura $\rightarrow$ N Destinos" sin romper el modelo transaccional:

> **DOCTRINA SPLIT DE PEDIDOS (DIVIDE ET IMPERA)**
> *   **Origen:** 1 Orden de Compra (OC) del Cliente (ej: Nestlé 100 Cajas).
> *   **Proceso:** El sistema explota la OC en **N Remitos (Pedidos Hijos)**.
> *   **Mecánica:**
>     *   Remito A $\rightarrow$ 30 cajas $\rightarrow$ Pacheco.
>     *   Remito B $\rightarrow$ 70 cajas $\rightarrow$ Córdoba.
> *   **Facturación:** Se agrupan los N Remitos en 1 Factura Final.
> *   **Ventaja:** Mantiene la trazabilidad logística de cada viaje (1 Viaje = 1 Dirección) sin inventar estructuras complejas de "Multi-Drop" en una sola entidad de base de datos.

---

## 3. SEMÁFORO DE CONFIANZA (LOGIC GATES)

Definición de reglas de automatización para el sistema de control (State of Tomorrow):

| NIVEL | COLOR | EJEMPLO | ACCIÓN DEL SISTEMA |
| :---: | :---: | :--- | :--- |
| **VERDE** | 🟢 | **María / Labme** | **AUTOMÁTICO.** El sistema confía ciegamente. Si el pedido entra, se reserva stock y se libera a logística. |
| **AMARILLO** | 🟡 | **Ford / Clientes B** | **MANUAL.** Requiere "Ojo Humano". El pedido entra en pausa hasta validación de stock o deuda técnica. |
| **ROJO** | 🔴 | **Ricardo / Morosos** | **RÍGIDO.** Bloqueo total. Requiere validación explícita del Nodo de Cobro (Vínculo con Rol COBRADOR) para liberar la mercadería. |

---

## 4. ESTADO MAÑANA (INSTRUCCIÓN DE BOOTEO)

Al iniciar la próxima sesión (Protocolo ALFA):
1.  **NO TOCAR** el modelo de Contactos (Está perfecto).
2.  **PRIORIDAD 1:** Implementar el "Split de Pedidos" en el Frontend (Tactical Loader) para soportar el caso Labme.
3.  **PRIORIDAD 2:** Activar la lógica del "Semáforo" en el backend (`pricing_engine` o `sales_engine`).

**Firma:**
*Antigravity Unit - Protocolo Omega Ejecutado*
