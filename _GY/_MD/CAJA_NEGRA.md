# 🛸 CAJA NEGRA (BLACK BOX) - DASHBOARD TÁCTICO V2
**Última Actualización:** 25-Ene-2026 (Sentinel V13 Update)
**Rol:** Tablero de Control y Estado de Salud del Sistema.

---

## 📡 CONECTIVIDAD & INFRAESTRUCTURA
| Nodo | Host | Estado |
| :--- | :--- | :--- |
| **IOWA (Cloud)** | `104.197.57.226` | 🟢 ONLINE (Sync Capable) |
| **PILOT (Local)** | `backend/pilot.db` | 🟢 ONLINE (SQLite) |
| **GIT (Repo)** | `Sonido_Liquido_V5` | 🟢 SINCRONIZADO (Protocolo V13) |

## 🛡️ CREDENCIALES & ACCESOS
*   **DB User:** `postgres` / `SonidoV5_2025` (Legacy/Ref)
*   **Admin PIN:** `1234` (Bypass visual activo)
*   **IOWA Sync:** `scripts/push_session_to_iowa.py`

## 🧩 ESTADO DEL NÚCLEO (V5.3)
| Módulo | Estado | Notas Técnicas |
| :--- | :--- | :--- |
| **Clientes** | 🟢 OPTIMIZADO | UX V5.4 (Ficha Unificada/Refactor). 1 Planta=1 Cliente. |
| **Pedidos** | 🟢 OPERATIVO | Ciclo Completo (Alta/Edición). Logística integrada. |
| **Productos** | 🟢 OPERATIVO | ABM Completo + Clonado. |
| **Despliegue** | 🟢 V1.3 STABLE | Proxy FE/BE relativo. Fix Teleport. |

## ⏳ INTEGRIDAD Y PRESERVACIÓN
*   **Ultimo Backup Profundo:** *Requiere Actualización*
*   **Sesiones sin Backup:** *Requiere Actualización*
*   **Doctrina Activa:** V13 "Sentinel" (Sync First).

## 🧰 COMANDOS DE MANTENIMIENTO
*   **Sync Cloud:** `python scripts/push_session_to_iowa.py`
*   **Reset Schema:** `python scripts/force_init_schema.py` (PELIGRO)
*   **Dump Cantera:** `python backend/scripts/dump_cantera.py`

---
**Instrucción de Mantenimiento:** Actualizar este tablero al CERRAR la sesión (Protocolo Omega).
