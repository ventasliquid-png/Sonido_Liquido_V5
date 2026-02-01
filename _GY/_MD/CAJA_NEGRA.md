# 🛸 CAJA NEGRA (BLACK BOX) - DASHBOARD TÁCTICO V2

**Última Actualización:** 01-Feb-2026 (Protocolo Omega V6.1)
**Sesiones Completadas:** +4 (Regla 5/6)
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
