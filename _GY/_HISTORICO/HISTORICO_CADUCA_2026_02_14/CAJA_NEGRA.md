# 🛸 CAJA NEGRA (BLACK BOX) - DASHBOARD TÁCTICO
**Última Actualización:** 13-Ene-2026 (Release V1.1)

---

## 📡 CONECTIVIDAD
| Nodo | Host | Estado |
| :--- | :--- | :--- |
| **IOWA (Cloud)** | `104.197.57.226` | 🟢 ONLINE (Sync Capable) |
| **PILOT (Local)** | `backend/pilot.db` | 🟢 ONLINE |

## 🛡️ CREDENCIALES ACTIVAS
*   **User:** `postgres`
*   **Pass:** `SonidoV5_2025`
*   **DB:** `postgres`

## ⏳ ESTADO DE PRESERVACIÓN (Regla 4/6)
*   **Días sin Backup Profundo:** 4
*   **Sesiones sin Backup Profundo:** 2
*   **Estado:** 🟡 ALERTA BAJA

> **Nota:** El contador se reinicia al ejecutar `dump_cantera.py` (o `db_dump_to_json.py`).

## 🧰 HERRAMIENTAS CRÍTICAS
*   **Sync Script:** `python scripts/push_session_to_iowa.py`
*   **Schema Reset:** `python scripts/force_init_schema.py`
*   **Log Archive:** `ARCHIVE_LOGS_LEGACY.md`

## 🧩 METADATA DEL PROYECTO
*   **Versión Core:** V1.1 (Release Update)
*   **Doctrina:** "La Verdad es el Conteo."
