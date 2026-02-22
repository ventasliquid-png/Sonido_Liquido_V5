**Última Actualización:** 22-Feb-2026 (Reloj Táctico / Contingencia)
**Sesiones Completadas:** +13 (Confinamiento Táctico)
**Rol:** Tablero de Control y Estado de Salud del Sistema.

---

## 📡 CONECTIVIDAD & INFRAESTRUCTURA
| Nodo | Host | Estado |
| :--- | :--- | :--- |
| **IOWA (Cloud)** | `104.197.57.226` | 🟢 ONLINE (Sync Capable) |
| **PILOT (Local)** | `backend/pilot.db` | 🟢 ONLINE (SQLite) |
| **GIT (Repo)** | `Sonido_Liquido_V5` | 🟢 SINCRONIZADO (Protocolo V14 Bootloader) |

## 🛡️ CREDENCIALES & ACCESOS
*   **DB User:** `postgres` / `SonidoV5_2025` (Legacy/Ref)
*   **Admin PIN:** `1234` (Bypass visual activo)
*   **IOWA Sync:** `scripts/push_session_to_iowa.py`

## 🧩 ESTADO DEL NÚCLEO (V6.3)
| Módulo | Estado | Notas Técnicas |
| :--- | :--- | :--- |
| **Clientes** | 🟢 ENIGMA STABLE | Bitmask (V14.5) + Validación ARCA + UX Tuning. |
| **Contactos** | 🟢 OPTIMIZADO (V6.1) | Role Persistence & Schema Fix (01-02). |
| **Pedidos** | 🟢 V5.6 (CONECTADO) | Semáforo Fiscal + Modo Zen. |
| **Productos** | 🟡 V5.5 (STANDALONE) | Aislado de Agenda V6. "Roca" de Precios OK. |
| **Transportes** | 🟡 V5.1 (TRANSICIÓN) | Nodos planos. Espejo Despacho OK. |
| **Proveedores** | 🟡 V5.0 (AISLADO) | Sin Agenda Global. Requiere Migración. |
| **Vendedores** | 🟡 V5.0 (AISLADO) | Sin Agenda Global. Requiere Migración. |
| **Listas Precios** | 🟢 V6.0 (LAB) | Sistema Estanco. Inyección de Templates. |
| **Despliegue** | 🟢 V1.3 STABLE | Bootloader V2 Integrado. |

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
## [2026-02-22] CONTINGENCIA TÁCTICA: INTERCEPTOR 429
- **Hito**: Implementado interceptor de cuota (Reloj Táctico) para Gemini.
- **Limpieza**: Ejecutado "Confinamiento" del taller. `App.vue` restaurado. Reloj confinado en `AteneaChat.vue`.
- **Backend Fix**: Reparado routing SPA y forward reference error en `main.py`.
- **Estado**: Sistema Purificado e Impecable.
