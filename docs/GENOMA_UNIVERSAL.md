# GENOMA_UNIVERSAL.md
**Documento Canónico — Arquitectura de Máscaras de Bits (64-bits)**
*Última actualización: Sesión 806 (Carlos + Claude Sonnet + Nike Arq 5.5)*
*Estado: NOMINAL GOLD — PIN 1974*

## REGLAS GLOBALES DEL GENOMA
Las siguientes banderas son inmutables y atraviesan horizontalmente a **todas** las entidades del ecosistema Sonido Líquido V5:

*   **Bit 0 (Valor 1) — `EXISTENCE`**: Registro activo lógicamente. (ACTIVO)
*   **Bit 1 (Valor 2) — `HAS_ACTIVITY / VIRGINITY`**: Nace encendido (2 = Virgen / Borrado físico permitido). Se apaga con la primera operación comercial (0 = Tocado / Bloqueado, solo baja lógica). *Resolución de ambigüedad (Sesión 2026-05-04): Se confirma que LAVIMAR (13) tiene el bit 1 apagado, validando su madurez.*
*   **Bit 10 (Valor 1024) — `V15_STRUCT`**: Marca de agua arquitectónica. (INTOCABLE)
*   **Bit 13 (Valor 8192) — `COLISIÓN LAVIMAR`**: Protegido por razones históricas. (PROHIBIDO)

---

## 1. GENOMA_CLIENTES (`clientes.flags_estado`)
*Códice Arlequín V2 — Jerarquía y Colorimetría*

| Bit | Valor | Nombre Canónico | Semántica | Estado | Sesión Origen |
|:---|:---|:---|:---|:---|:---|
| 0 | 1 | `EXISTENCE` | El registro existe lógicamente. | ACTIVO | Base V14 |
| 1 | 2 | `HAS_ACTIVITY` | 1=Virgen, 0=Operado. Define protección de borrado. | ACTIVO | 2026-05-04 CA |
| 2 | 4 | `GOLD_ARCA` | Datos homologados por satélite RAR (ARCA). | ACTIVO | V14 / Arlequín |
| 3 | 8 | `V14_STRUCT` | Cumple arquitectura 32/64 bits (Color Amarillo = 9). | ACTIVO | V14 Base |
| 4 | 16 | `OPERATOR_OK` | Sello Rosa (Validación manual del operador). | ACTIVO | Arlequín V2 |
| 5 | 32 | `MULTI_CUIT` | Sello Azul (Permite CUIT compartido / Sucursales). | ACTIVO | Arlequín V2 |
| 6 | 64 | `TRUSTED_MANUAL` | Rosa Fucsia (Corporativo informal, ej. Luvianka). | ACTIVO | Arlequín V2 |
| 10 | 1024 | `V15_STRUCT` | Reserva estructural global. | INTOCABLE | Global |
| 13 | 8192 | `PROHIBIDO` | Colisión LAVIMAR. | PROHIBIDO | Global |

---

## 2. GENOMA_PRODUCTOS (`productos.flags_estado`)
*Catálogo y Control de Manufactura*

| Bit | Valor | Nombre Canónico | Semántica | Estado | Sesión Origen |
|:---|:---|:---|:---|:---|:---|
| 0 | 1 | `EXISTENCE` | El registro existe lógicamente. | ACTIVO | Base V14 |
| 1 | 2 | `HAS_ACTIVITY` | 1=Virgen, 0=Operado (Bloquea hard_delete). | ACTIVO | 2026-05-04 CA |
| 2 | 4 | `GOLD_CATALOGED` | SKU Catalogado y validado en la maestra. | ACTIVO | V14 Base |
| 3 | 8 | `EXPATRIADO` | Producto huérfano (rubro eliminado, en Purgatorio). | ACTIVO | V5.9 |
| 4 | 16 | `HAS_COST` | Tiene costo de reposición cargado. | ACTIVO | V14 Base |
| 5 | 32 | `HAS_SUPPLIER` | Tiene proveedor asignado. | ACTIVO | V14 Base |
| 6 | 64 | `IS_KIT` | Es un producto compuesto/kit. | ACTIVO | V14 Base |
| 10 | 1024 | `V15_STRUCT` | Reserva estructural global. | INTOCABLE | Global |
| 13 | 8192 | `PROHIBIDO` | Colisión LAVIMAR. | PROHIBIDO | Global |
| *X* | *TBD* | `RENOMBRADO` | *Roadmap V6: Bifurcación SKU y linaje SCD.* | RESERVADO | 2026-05-05 |

---

## 3. GENOMA_PEDIDOS (`pedidos.flags_estado`)
*El Documento Madre Orquestador*

| Bit | Valor | Nombre Canónico | Semántica | Estado | Sesión Origen |
|:---|:---|:---|:---|:---|:---|
| 0 | 1 | `EXISTENCE` | El pedido existe (Verde PENDIENTE implícito). | ACTIVO | Sesión 798 |
| 1 | 2 | `HAS_ACTIVITY` | 1=Virgen, 0=Tocado (Vinculado a Logística/Factura). | ACTIVO | Sesión 798 |
| 2 | 4 | `PRESUPUESTO` | Cotización formal con IVA proyectado (Púrpura). | ACTIVO | Sesión 798 |
| 3 | 8 | `CUMPLIDO` | Ciclo cerrado (Amarillo). | ACTIVO | Sesión 798 |
| 4 | 16 | `ANULADO` | Baja lógica (Rojo). | ACTIVO | Sesión 798 |
| 5 | 32 | `LIBERADO_DESPACHO` | Gatekeeper financiero superado. | ACTIVO | Sesión 798 |
| 9 | 512 | `INGESTA_CON_CORR.` | Espejo de PRC: Factura originaria corregida post-OCR. | ACTIVO | 800-CA |
| 10 | 1024 | `V15_STRUCT` | Reserva estructural global. | INTOCABLE | Global |
| 12 | 4096 | `NO_FISCAL_FORCE` | Motor Bipolar (Sin IVA, desconecta ARCA). | ACTIVO | Sesión 798 |
| 13 | 8192 | `PROHIBIDO` | Colisión LAVIMAR. | PROHIBIDO | Global |
| 14 | 16384 | `TIENE_CORRECCION` | NC/ND asociada; bloquea cierre si balance != 0. | ACTIVO | Sesión 798 |

---

## 4. GENOMA_FACTURAS
*Debido a la arquitectura de "Esclusa de Verdad" (Sesión 800-OF), la ingesta fiscal se divide en el contenedor RAW y el Procesado (PRC). La tabla madre de facturas consolida la doctrina final.*

### A. Facturas Madre (`facturas.flags_estado`) - *Canon Base y Zona V6*
| Bit | Valor | Nombre Canónico | Semántica | Estado | Sesión Origen |
|:---|:---|:---|:---|:---|:---|
| 0 | 1 | `EXISTENCE` | Factura existe lógicamente. | ACTIVO | May 7 |
| 1 | 2 | `HAS_ACTIVITY` | 1=Virgen, 0=Tocado. | ACTIVO | May 7 |
| 2 | 4 | `HAS_REMITO` | Tiene remito vinculado. | ACTIVO | May 7 |
| 3 | 8 | `ACTIVE` | No anulada. | ACTIVO | May 7 |
| 10 | 1024 | `V15_STRUCT` | Reserva estructural global. | INTOCABLE | Global |
| 13 | 8192 | `PROHIBIDO` | Colisión LAVIMAR. | PROHIBIDO | Global |
| 15 | 32768 | `PASADO_A_PEDIDO` | Generó pedido exitosamente. | ACTIVO | May 7 |
| 16 | 65536 | `EN_CUARENTENA` | Requiere revisión de supervisor. | ACTIVO | May 7 |
| 17 | 131072 | `TIENE_NC` | Se emitió NC hija sobre esta factura madre. | ACTIVO | May 7 |
| 18 | 262144 | `TIENE_ND` | Se emitió ND hija sobre esta factura madre. | ACTIVO | May 7 |
| 19 | 524288 | `ES_NC` | El documento actual ES una Nota de Crédito. | ACTIVO | May 7 |
| 20 | 1048576 | `ES_ND` | El documento actual ES una Nota de Débito. | ACTIVO | May 7 |
| 21 | 2097152 | `AUDITADA` | Revisada por supervisor humano. | ACTIVO | May 7 |

### B. Sabueso Ingesta RAW (`facturas_raw.flags_estado`)
| Bit | Valor | Nombre Canónico | Semántica | Estado | Sesión Origen |
|:---|:---|:---|:---|:---|:---|
| 0 | 1 | `EXISTENCE` | El PDF crudo fue ingresado. | ACTIVO | 800-OF |
| 1 | 2 | `HAS_ACTIVITY` | Ley de Virginidad estándar. | ACTIVO | 800-OF |
| 2 | 4 | `EN_CUARENTENA` | Señal de humo: Consultar espejo PRC por detalles. | ACTIVO | 800-OF |
| 3 | 8 | `CON_PROBLEMAS` | Técnico: Falla de OCR profundo, CAE mal formado. | ACTIVO | 800-OF |
| 4 | 16 | `PROCESADA` | Encendido por Pedidos al confirmar gemelo PRC sano. | ACTIVO | 800-OF |
| 10 | 1024 | `V15_STRUCT` | Reserva estructural global. | INTOCABLE | Global |
| 13 | 8192 | `PROHIBIDO` | Colisión LAVIMAR. | PROHIBIDO | Global |

### C. Sabueso Ingesta PRC (`facturas_procesadas.flags_estado`)
| Bit | Valor | Nombre Canónico | Semántica | Estado | Sesión Origen |
|:---|:---|:---|:---|:---|:---|
| 0 | 1 | `EXISTENCE` | Entidad procesada activa. | ACTIVO | 800-OF |
| 1 | 2 | `HAS_ACTIVITY` | Ley de Virginidad estándar. | ACTIVO | 800-OF |
| 2 | 4 | `TIENE_NC` | Correcciones detectadas en ingesta. | ACTIVO | 800-OF |
| 3 | 8 | `TIENE_ND` | Débitos detectados en ingesta. | ACTIVO | 800-OF |
| 4 | 16 | `AUDITADA` | Revisión humana OK. | ACTIVO | 800-OF |
| 5 | 32 | `VINCULADA_PEDIDO` | Asociado al documento madre (Conserje V2). | ACTIVO | 800-OF |
| 6 | 64 | `RAW_CON_PROBLEMAS` | Errores arrastrados del parser. | ACTIVO | 800-OF |
| 7 | 128 | `SIN_STOCK` | Factura validada, pero quiebre en inventario. | ACTIVO | 800-OF |
| 8 | 256 | `SIN_AUTORIZACION` | Bloqueo por CC, activa CUARENTENA en RAW. | ACTIVO | 800-OF |
| 9 | 512 | `CORRECCION_OCR` | Intervención humana: Parser erró, operador corrigió. | ACTIVO | 800-CA |
| 10 | 1024 | `V15_STRUCT` | Reserva estructural global. | INTOCABLE | Global |
| 11 | 2048 | `DISCREPANCIA_FISC` | Error humano en ARCA original (requiere NC/ND externa). | ACTIVO | 800-CA |
| 13 | 8192 | `PROHIBIDO` | Colisión LAVIMAR. | PROHIBIDO | Global |

---

## 5. GENOMA_REMITOS (`remitos.flags_estado`)
*ESTADO: PENDIENTE DE DEFINICIÓN CANÓNICA V6 COMPLETA.*
Actualmente, hereda estrictamente las leyes universales. El diseño logístico futuro (Logística N:M) colonizará los bits restantes.

| Bit | Valor | Nombre Canónico | Semántica | Estado | Sesión Origen |
|:---|:---|:---|:---|:---|:---|
| 0 | 1 | `EXISTENCE` | Documento existe. | ACTIVO | Universal |
| 1 | 2 | `HAS_ACTIVITY` | 1=Borrador (editable), 0=Emitido/Cerrado. | ACTIVO | Universal |
| 10 | 1024 | `V15_STRUCT` | Reserva estructural global. | INTOCABLE | Global |
| 13 | 8192 | `PROHIBIDO` | Colisión LAVIMAR. | PROHIBIDO | Global |

---

## RESOLUCIÓN DE CONTRADICCIONES FORENSES

1.  **Herejía del Bit 10 en Pedidos:** El código previo asignaba erróneamente `NO_FISCAL_FORCE` al Bit 10 (1024). Este documento certifica, bajo la auditoría de hoy, que el Bit 10 es **`V15_STRUCT`** (INTOCABLE) globalmente. `NO_FISCAL_FORCE` reside canónicamente en el **Bit 12 (4096)**.
2.  **La Semántica de Virginidad (Bit 1):** Queda unificada y sellada para todos los módulos que el estado natural de nacimiento es el Bit Encendido (**Valor 2**), lo que permite operaciones físicas de borrado. La operación y cruce comercial apagan el bit (**Valor 0**), forzando baja lógica inquebrantable.
3.  **Genoma Base de Facturas vs Ingesta:** El Genoma original de `facturas` dictado el 7 de mayo desplazó sus bits de negocio hacia la "Zona V6" (Bits 15 en adelante). Los contenedores `RAW` y `PRC` definidos en la Sesión 800-OF/CA poseen sus propios dominios locales para controlar el ciclo de cuarentena sin contaminar la matriz fiscal madre.

---

**Sello de Auditoría:** Este documento debe inyectarse inmediatamente en la rama principal. Ningún `constants.py` podrá divergir de estos mapas de bits de ahora en adelante.
