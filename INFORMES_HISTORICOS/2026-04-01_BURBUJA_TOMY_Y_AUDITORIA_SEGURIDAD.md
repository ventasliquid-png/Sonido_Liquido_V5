# INFORME HISTÓRICO DE SESIÓN: 2026-04-01
## Misión: BURBUJA TOMY — AISLAMIENTO V5-LS Y AUDITORÍA DE SEGURIDAD NPM

### 🟡 ESTADO FINAL: ALERTA CONTROLADA
> Sistema operativo. Burbuja V5-LS funcional en código. Pendiente `npm run build` antes de despliegue efectivo para Tomy.

---

### 📊 ACTIVIDAD TÉCNICA

#### 1. Auditoría de Seguridad — Incidente npm Claude Code v2.1.88
El 31 de marzo de 2026, Anthropic publicó accidentalmente la versión 2.1.88 de Claude Code en npm con un archivo `cli.js.map` de ~60 MB que contenía el código fuente completo (source map). El incidente fue confirmado por Anthropic: error humano de empaquetado, sin exposición de credenciales ni datos de clientes.

- **Vector de riesgo reportado**: Posible distribución de una versión troyanizada de `axios` (1.14.1 / 0.30.4) con RAT en la ventana 00:21–03:29 UTC del 31/03.
- **Resultado para esta instalación**: **LIMPIA**.
  - Instalación: nativa (`.local/bin/claude.exe`), **no vía npm** → vector de cadena de suministro npm no aplicable.
  - Versión activa: `2.1.89` (auto-actualización previa al incidente o post-patch).
  - `axios` en proyecto: `1.13.2` → no troyanizado.
  - `plain-crypto-js`: no encontrado.
  - Procesos node.exe activos: pertenecen a Adobe Creative Cloud exclusivamente.
  - Registro HKCU/HKLM Run: sin entradas relacionadas con Claude/Anthropic/node.
  - Tareas programadas: sin referencias sospechosas.
- **Acción ejecutada**: Eliminación del binario obsoleto `claude.exe.old.*` en `~/.local/bin/`.

#### 2. Fixes Dev — Sesión 2026-03-31 (versionados hoy)
Tres correcciones críticas desarrolladas por Gy el 31/03 que quedaron sin commitear, versionadas en este cierre:

- **ClientCanvas.vue — UUID nulo al crear cliente** (`línea 1532`):
  - Antes: `emit('save', resCreated?.data || payload)` → emitía formulario sin ID del servidor.
  - Después: `emit('save', resCreated || payload)` → propaga el objeto completo con UUID asignado.

- **PedidoCanvas.vue — F10 bloqueado en modal de cliente** (`línea 1564`):
  - Causa: `PedidoCanvas` ejecutaba `e.preventDefault()` antes de que `ClientCanvas` pudiera capturar F10.
  - Fix: Guarda `if (showClientModal.value) return;` antes del `preventDefault`.

- **Login.vue — Endpoint hardcodeado al puerto 8000**:
  - Antes: `axios.post('http://${hostname}:8000/auth/token')` → puerto incorrecto, no pasa por proxy Vite.
  - Después: `api.post('/auth/token')` → usa proxy, funciona en LAN desde cualquier host.
  - Bonus: Agregado `text-gray-900 bg-white` a inputs → texto visible (era blanco sobre blanco).

#### 3. Blindaje Burbuja Tomy — V5-LS Puerto Unificado 8090
**Diagnóstico del problema:** La arquitectura anterior levantaba dos procesos independientes: backend FastAPI en 8090 y `python -m http.server 5174` para los estáticos. El servidor HTTP simple no hace proxy, por lo que las llamadas API del frontend (a `/auth`, `/clientes`, etc.) llegaban al 5174 y morían sin respuesta.

**Solución implementada:** El backend ya tenía soporte SPA incorporado en `main.py` (montaje de `/assets` + catch-all para `index.html`). Solo había un bug de path que impedía encontrar los archivos compilados:

- **`current/backend/main.py`** — `static_dir` corregido:
  - Antes: `os.path.join(..., "..", "static")` → resolvía a `current/static/` (inexistente).
  - Después: `os.path.join(..., "..", "..", "static")` → resuelve a `V5-LS/static/` ✅

- **`LANZAR_V5_SOBERANA.bat`** — Eliminado el paso `python -m http.server 5174`. Un solo proceso en 8090 sirve API + SPA.

- **`SATELITE_TOMY.bat`** — Actualizado de puerto 5174 a 8090.

- **`current/frontend/src/views/Login.vue`** (V5-LS) — Aplicados los mismos fixes que en dev: endpoint `api.post('/auth/token')` y visibilidad de texto en inputs.

- **`ALFA.md`, `CLAUDE.md`, `OMEGA.md`** — Agregados al repo V5-LS (faltaban).

---

### 🛡️ AUDITORÍA DE SEGURIDAD
- **Git Status (dev)**: Commiteado. Pendiente push.
- **Git Status (V5-LS)**: Commiteado (`b7215a2`). Pendiente push.
- **File Audit**: Sin binarios, sin .db en staging, <20 archivos en cada commit.
- **Health Check**: ALERTA CONTROLADA — sistema funcional, burbuja Tomy operativa en código, pendiente build frontend.

---

### 🔮 DEUDA TÉCNICA / PRÓXIMOS PASOS
1. **CRÍTICO — npm run build en V5-LS** antes de que Tomy use el sistema:
   ```cmd
   cd C:\dev\V5-LS\current\frontend
   npm run build
   xcopy /E /Y dist\* ..\..\static\
   ```
2. `historial_cache` en fichas de clientes muestra datos MOCK hardcodeados (agua mineral, pedidos falsos) — decidir si conectar a pedidos reales o vaciar.
3. `transporte_habitual_id` existe en schema pero 0/32 clientes tienen valor asignado.

---

**Firma**: Claude Code (Anthropic CLI)
**Protocolo**: OMEGA 2.1. PIN 1974.
**Marcador de Auditoría**: 2026-04-01_BURBUJA_TOMY_V5LS_GOLD
