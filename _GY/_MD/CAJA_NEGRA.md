# 🛸 CAJA NEGRA (BLACK BOX) - DASHBOARD TÁCTICO V2
**Última Actualización:** 28-Ene-2026 (Fix Transporte & Frankenstein Cleanup)
**Sesiones Completadas:** +1 (Regla 4/6)
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
| **Clientes** | 🟢 OPTIMIZADO | UX V5.4 (Ficha Unificada). Agenda en Desarrollo. |
| **Pedidos** | 🟢 OPERATIVO | Ciclo Completo. *Schema Drift (Nulls) Resuelto [27-01].* |
| **Productos** | 🟢 OPERATIVO | ABM Completo + Clonado. |
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

## [2026-01-28] INCIDENTE: La Legión de Fantasmas
- **Síntoma**: UI mostraba 527 contactos vacíos in-cliqueables.
- **Diagnóstico**: El Frontend pedía /api/contactos (inexistente). El Backend, por regla catch-all SPA, devolvía index.html. Vue parseaba el HTML char-by-char.
- **Solución**: 1) Proxy Vite /contactos. 2) Store API_URL /contactos/ (trailing slash). 3) Exclusión explícita en Backend SPA handler.
