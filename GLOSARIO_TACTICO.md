# 🧠 GLOSARIO TÁCTICO V1.0

Terminología estandarizada para operaciones "Sonido Líquido V5".

---

## 🌍 INFRAESTRUCTURA

### ☁️ IOWA
*   **Definición:** Entorno de Producción en Nube (Google Cloud SQL - Postgres).
*   **IP:** `104.197.57.226`
*   **Rol:** "La Verdad Remota". Repositorio final de datos seguros y accesibles para la fuerza de venta móvil.
*   **Política:** Wipe & Replace desde LOCAL (por ahora).

### 🏠 CANTERA
*   **Definición:** `backend/data/cantera.db` (SQLite) + JSONs.
*   **Rol:** "Reserva Estratégica". Contiene datos maestros históricos o importados masivamente.
*   **Política:** Solo Lectura / Referencia. No se opera transaccionalmente aquí.

### ⚓ PILOT
*   **Definición:** `root/pilot.db` (SQLite).
*   **Rol:** "Campo de Batalla". Base de datos operativa de la sesión actual. Aquí se crean pedidos, se editan clientes y se prueba código.
*   **Ubicación Crítica:** **RAÍZ DEL PROYECTO** (`c:\dev\Sonido_Liquido_V5\pilot.db`).

---

## 📜 PROTOCOLOS

### REGLA 4/6 (Preservación)
*   **Lema:** "4 Días, 6 Sesiones".
*   **Directiva:** Si el contador llega a 4 días o 6 sesiones sin backup profundo, se declara **ALERTA NARANJA**.
*   **Acción:** Ejecutar backup completo de JSONs (`dump_cantera.py`) y commit a Git.

### PROTOCOLO ALFA (Inicio)
1.  Lectura de `GY_IPL.md`.
2.  Verificación de Entorno (`.env`, Rutas).
3.  Conteo de Munición (Script `audit_counts.py`) vs Registro Anterior.

### PROTOCOLO OMEGA (Cierre)
1.  Ejecución de `push_session_to_iowa.py` (Sync).
2.  Conteo final de registros.
3.  Actualización de `GY_IPL.md` con nuevos números.
4.  Git Commit & Push.

---

## 🚦 ESTADOS DE ALERTA

*   🟢 **VERDE:** Sistemas Nominales. Rutas OK. IOWA Sync OK.
*   🟡 **AMARILLO:** Schema Drift leve. Diferencia de conteos no crítica.
*   🔴 **ROJO:** `pilot.db` vacío (0 registros). Desconexión de IOWA. Pérdida de datos.
