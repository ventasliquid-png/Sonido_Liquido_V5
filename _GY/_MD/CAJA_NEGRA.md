# 🛸 CAJA NEGRA (BLACK BOX) - DASHBOARD TÁCTICO V2
Open Editor
Comment on files
Select text within files to leave a comment for the agent.

Dismiss
16
Workspaces
Sonido_Liquido_V5


Playground

Sonido_Liquido_V5
/
Contacts UI & Data Integrity

**Última Actualización:** 30-Ene-2026 (Protocolo Multiplex N:M)
**Sesiones Completadas:** +3 (Regla 5/6)
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
| **Clientes** | 🟢 OPTIMIZADO | UX V5.4 (Ficha Unificada). |
| **Contactos** | 🟢 N:M MULTIPLEX | Protocolo Multiplex (Backend/Frontend/QA) Completado. |
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

## [2026-01-30] INCIDENTE: La Paradoja de Pedro
- **Síntoma**: Imposibilidad de asignar múltiples roles a una misma persona en distintas empresas sin duplicar el registro.
- **Diagnóstico**: Arquitectura de base de datos 1:1 (Legacy) acoplada.
- **Solución**: Reingeniería completa N:M (Multiplex). `Persona` desacoplada de `Vinculo`. Implementación de Search & Link para prevención de duplicados.

