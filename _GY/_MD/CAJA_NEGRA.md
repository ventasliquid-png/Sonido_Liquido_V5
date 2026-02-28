**Última Actualización:** 27-Feb-2026 (Refactorización ClientCanvas y Fix Remitos)
**Sesiones Completadas:** +14 (Ciclo de Estabilización)
**Rol:** Tablero de Control y Estado de Salud del Sistema.

---

## 📡 CONECTIVIDAD & INFRAESTRUCTURA
| Nodo | Host | Estado |
| :--- | :--- | :--- |
| **IOWA (Cloud)** | `104.197.57.226` | 🟢 ONLINE (Sync Capable) |
| **PILOT (Local)** | `backend/pilot.db` | 🟢 ONLINE (SQLite) |
| **GIT (Repo)** | `Sonido_Liquido_V5` | 🟢 SINCRONIZADO (Protocolo 4-Bytes v14-B) |
| **SITUATION (Bit)** | `session_status.bit` | 🟢 ACTIVO (Status: 69 - CASA) |

## 🛡️ CREDENCIALES & ACCESOS
*   **DB User:** `postgres` / `SonidoV5_2025` (Legacy/Ref)
*   **Admin PIN:** `1234` (Bypass visual activo)
*   **IOWA Sync:** `scripts/push_session_to_iowa.py`

## 🧩 ESTADO DEL NÚCLEO (V6.3)
| Módulo | Estado | Notas Técnicas |
| :--- | :--- | :--- |
| **Clientes** | 🟢 ENIGMA STABLE | Bitmask (V14.5) + Validación ARCA + UX Tuning. |
| **Contactos** | 🟢 OPTIMIZADO (V6.1) | Role Persistence & Schema Fix (01-02). |
| **Pedidos** | 🟢 V5.7 (CONECTADO) | Ingesta PDF Automática + Despacho. |
| **Productos** | 🟡 V5.5 (STANDALONE) | Aislado de Agenda V6. "Roca" de Precios OK. |
| **Transportes** | 🟡 V5.1 (TRANSICIÓN) | Nodos planos. Espejo Despacho OK. |
| **Proveedores** | 🟡 V5.0 (AISLADO) | Sin Agenda Global. Requiere Migración. |
| **Vendedores** | 🟡 V5.0 (AISLADO) | Sin Agenda Global. Requiere Migración. |
| **Listas Precios** | 🟢 V6.0 (LAB) | Sistema Estanco. Inyección de Templates. |
| **Despliegue** | 🟢 V1.4 STABLE | Bootloader V2 + fpdf2 Lib. |

## ⏳ INTEGRIDAD Y PRESERVACIÓN
*   **Doctrina Activa:** V14 "VANGUARD" (Anticipación).
*   **Bootloader:** V2 (Auto-Sync).

## 🧰 COMANDOS DE MANTENIMIENTO
*   **Sync Cloud:** `python scripts/push_session_to_iowa.py`
*   **Reset Schema:** `python scripts/force_init_schema.py` (PELIGRO)
*   **Dump Cantera:** `python backend/scripts/dump_cantera.py`

---
**Instrucción de Mantenimiento:** Actualizar este tablero al CERRAR la sesión (Protocolo Omega).

## [2026-02-15] STABILIZATION: AFIP BRIDGE
- **Incidente**: Error 400 aleatorio y datos vacíos al validar CUIT.
- **Causa**: Falta de librerías `zeep/lxml` en venv y error de parsing JS (`res` vs `res.data`).
- **Resolución**: Hotfix de dependencias y refactor de manejo de respuesta en Frontend.
- **Estado**: Sistema Validado.

## [2026-02-15] REFINAMIENTO ARCA & BATCH
- **Hito**: Ejecución exitosa de validación masiva (`validate_arca_batch.py`) sobre `pilot.db`.
- **UX**: Implementado Foco Automático, Eliminación de Redundancia y Mapeo Fuzzy de IVA en `ClientCanvas`.
- **Integridad**: Lógica de "Preservación de Identidad" para casos UBA/Sucursales (mismo CUIT, distinto nombre).
- **Estado**: Clientes V6.3 FULL OPERATIVO (Validado ARCA).

## [2026-02-16] ANÁLISIS ESTRATÉGICO: DIGESTO SISTÉMICO
- **Hito**: Generación de `DIGESTO_SISTEMA_SL.txt` ("Cerebro de Proyecto").
- **Alcance**: Consolidación documental de Arquitectura V5 (Híbrida), Satélite RAR (WSMTXCA) y Lógica de Negocio (Precios/Clientes).
- **Objetivo**: Alimentar sistemas de razonamiento externos para reducir deuda técnica cognitiva.
- **Estado**: Documento generado y persistido en `INFORMES_HISTORICOS`.

## [2026-02-18] CLIENTES HÍBRIDOS & PROTOCOLO BLINDADO
- **Hito**: Implementación de Arquitectura de Clientes Informales ("Rosa Chicle") sin CUIT obligatorio.
- **UX**: Auto-Fill inteligente en Domicilio Split (Fiscal desde Entrega) y Transición automática Informal->Formal vía ARCA.
- **Integridad**: Refuerzo de Protocolos ALFA (Read-Only DB) y OMEGA (4-Byte Flags Check) con Freno de Mano PIN 1974.
- **Estado**: Sistema Validado y Documentado (V14 Vanguard).

## [2026-02-19] DEBUG CRÍTICO & BACKFILL
- **Incidente**: Pérdida de Domicilios tras validación ARCA y falta de Códigos Internos.
- **Causa**: Lógica de protección en `saveCliente` (UPDATE) y datos legacy `NULL`.
- **Resolución**: Implementado bandera `forceAddressSync` y script de Backfill (SQL).
- **Estado**: Sistema Estabilizado y Consistente.

## [2026-02-19] IMPLEMENTACIÓN UPSERT INTELIGENTE (MINER PDF)
- **Hito**: Backend Script (`miner.py`) refactorizado con `pdfplumber` y regex boundary-aware.
- **Lógica**: Upsert de Clientes existentes (Flag 15 -> 13) y Creación de Nuevos (Flag 13 + 'PENDIENTE_AUDITORIA').
- **Incidente**: Falla en Ingesta Web (`pdf_parser.py`) por uso de librería `pypdf` (obsoleta para estos layouts).
- **Resolución**: Script verificado OK. Pendiente portar lógica al endpoint API.
- **Estado**: Script Operativo / Frontend Pendiente.


## [2026-02-20] ESTABILIZACIÓN STAGE 5: PROTOCOLO ENIGMA
- **Hito**: Definición de la "Cinta Perforada" (Bitmask de Flags de Estado) en `ENIGMA_BLUEPRINT.md`.
- **Lógica**: Unificación de criterios visuales (Colores) y jerarquía comercial (Virgen/Activo/Gold).
- **IPL**: Vinculación obligatoria del Blueprint en la secuencia de arranque del sistema (V14.5).
- **Estado**: Estabilización Sistémica Alcanzada.
## [2026-02-21] ESTABILIZACIÓN ENIGMA V14.5 (BITMASK)
- **Hito**: Implementación plena del Protocolo Bitmask (32 bits) para identidad de clientes.
- **UX**: Refactorizado `ClienteInspector.vue` con reactividad garantizada tras guardado (Watcher modelValue).
- **Logística**: Implementado Toggle 'Retira' bidireccional y seguro.
- **Integridad**: "Escudo de Virginidad" (Preservación de Bit 1) funcional durante infiltración ARCA.
- **Backend**: Sincronización total de constantes bitwise en `constants.py`.
- **Estado**: Sistema Estabilizado y Auditado.

## [2026-02-26] SINCRONIZACIÓN CA-OF & 4-BYTES
- **Hito**: Resolución de desincronización crítica de ramas entre Casa y Oficina.
- **Doctrina**: Implementado Protocolo de Estados de 4-Bytes con detección de host (`manager_status.py`).
- **Integridad**: Verificada Paridad de DB CASA-OFICINA (428 KB) y activada Carta Momento Cero.
- **Estado**: Sistema Multiplex V14-B Nominal.

## [2026-02-27] INTEGRACIÓN SABUESO PDF & WORKFLOW ABM
- **Hito**: Porting finalizado del extractor de Facturas (RAR) a Sistema V5.
- **Heurística**: Ajustes de Regex (Lookahead activo) para superar ruidos de formato AFIP (`pdf_parser.py`).
- **UX Segura**: Workflow ABM instanciado vía frontend (`IngestaFacturaView.vue`). Todo cliente anómalo o inexistente dispara modal obligatorio del inspector.
- **Doctrina**: Test de mutación 15->13 ejecutado. Clientes Vírgenes pierden el flag tras primer Remito (ORM backend).
- **Estado**: Base de Datos Estática Confirmada (428 KB). Sabueso Operativo.

## [2026-02-27] REFACTORIZACIÓN DUAL CLIENTCANVAS & UX
- **Hito**: Solución de Regresión UI (Restauración de lista de Remitos en módulo Logística).
- **UX Segura**: Modalización del componente `ClientCanvas.vue` (Ficha Original) para reemplazar a `ClienteInspector.vue` en IngestaFacturaView, PedidoTacticoView, PedidoCanvas y HaweView.
- **Doctrina**: Cumplimiento de directiva de acceso a validación ARCA/AFIP (Lupa) directa desde el flujo asistido de Alta/Edición en ingesta.
- **Estado**: UI Component Tree simplificado y unificado bajo un único estándar interactivo.
