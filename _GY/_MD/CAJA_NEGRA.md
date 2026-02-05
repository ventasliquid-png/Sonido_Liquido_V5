# 🛸 CAJA NEGRA (BLACK BOX) - DASHBOARD TÁCTICO V2

**Última Actualización:** 04-Feb-2026 (Logística Split & Remitos)
**Sesiones Completadas:** +6 (Regla 6/6 - CICLO COMPLETO)
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

## 🧩 ESTADO DEL NÚCLEO (V5.6)
| Módulo | Estado | Notas Técnicas |
| :--- | :--- | :--- |
| **Clientes** | 🟢 V6 NATIVE (HÍBRIDO) | Persistencia Pipe Logic (Domicilios) OK. |
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

## [2026-02-01] INCIDENTE: La Persistentia de Maria
- **Síntoma**: Error 500 al listar contactos y cargos que volvían a "Nuevo Rol".
- **Diagnóstico**: Desajuste entre el código (V6) y la base de datos local (V5) + Desvinculación de ID y Nombre en el frontend.
- **Solución**: Migración SQLite Express + Sincronización de Label/ID en `ContactCanvas` + Adaptación Reactiva en `ContactosView`.

## [2026-02-02] UX UPDATE: AUTOMATIZACIÓN CLIENTES
- **Mejora**: Implementada "Ley de Conservación Fiscal" con menú contextual para baja segura.
- **Automatización**: Lógica cruzada CUIT <-> Consumidor Final en alta de clientes.
- **Estabilidad**: Corregido crash de ordenamiento (localeCompare) y refresco de lista tras alta.

## [2026-02-03] LABORATORIO DE PRECIOS (ESTANCO)
- **Hito**: Implementación de sistema de gestión de listas aislado (Scripts Python).
- **Logro**: Generación automática de Excel Versionado (`Celtrap (3)`) clonando estructura visual histórica.
- **Regla**: Aplicación de lógica comercial "Camilleros (+10%)" y fórmulas de markup vivas.

## [2026-02-04] LOGÍSTICA TÁCTICA V7 (SPLIT ORDERS)
- **Hito**: Implementación del sistema de entregas parciales y múltiples destinos por pedido.
- **Backend**: Separación de stocks (`stock_reservado` vs `stock_fisico`). Gatekeeper financiero en despacho.
- **Frontend**: Componente `LogisticaSplitter` con Drag & Drop. Branding de Remitos HTML/PDF.
- **Limpieza**: Amputación de código zombie en exportación Excel (`tipo_entrega` -> `Multiplex`).

## [2026-02-04] DEUDA TÉCNICA: DOMICILIOS V7
- **Hallazgo**: Uso de "Pipes" (`|`) para concatenar piso/depto en campo `numero`.
- **Riesgo**: Dificulta queries SQL y validación.
- **Plan**: **Saneamiento Definitivo V7**. Restitución de columnas nativas y migración de datos.
- **Ref**: `INFORMES_HISTORICOS/2026-02-04_PLAN_TECNICO_SPLIT_V7.md`.
