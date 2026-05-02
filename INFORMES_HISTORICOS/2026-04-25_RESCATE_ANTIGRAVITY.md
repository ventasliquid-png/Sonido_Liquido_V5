# Informe de Misión: Rescate y Blindaje de Antigravity (Gy)
**Fecha**: 2026-04-25  
**Estado**: NOMINAL GOLD  
**Autor**: Claude Code (Haiku 4.5) — análisis forense y ejecución de blindaje  

---

## 1. Objetivo de la Sesión

Gy quedó completamente bloqueado: los mensajes se enviaban en silencio (cuadradito rojo parpadeante, vuelta a flecha, cero respuesta, sin error visible en la UI). El objetivo fue diagnosticar la causa raíz, restaurar el funcionamiento y construir un sistema de prevención para que no recurriera.

---

## 2. Diagnóstico

### A. Síntoma vs. Causa Real

La UI no mostraba ningún error. El error estaba oculto en **Output → Antigravity**:

```
state syncing error: key not found
Failed to get OAuth token: error getting token source from auth provider
```

### B. Causa Raíz

El servidor Go (backend de lenguaje de Antigravity) no pudo sincronizar el token OAuth con el proceso Electron principal vía IPC. En Windows, cuando el proceso se actualiza y cambia de firma digital, el nuevo proceso no puede acceder a las llaves antiguas del Credential Manager (DPAPI). Esto desencadena un loop SIGTERM que mata y reinicia el servidor de lenguaje indefinidamente — sin ningún mensaje en la UI.

**Bug conocido:** Reportado en el foro oficial de Google AI Developers como *"Critical Bug: Total IDE lockout"*. Afecta especialmente instalaciones en Windows post-actualizaciones de abril 2026.

### C. Lo que NO funcionó

- Sign Out + Sign In (el token IPC ya estaba corrupto)
- Reload Window
- `taskkill node.exe` (funcionó solo temporalmente)
- Limpiar Cache / Local Storage / Local State individualmente con Antigravity abierto (Electron los recrea al instante porque tiene los archivos bloqueados)

### D. Causa contributiva: acumulación de sesiones

El LevelDB interno (`shared_proto_db`) se degrada con la acumulación de sesiones. Esto aumenta la probabilidad de corrupción del IPC y fue agravado por el bug recurrente del mes anterior donde Gy se agotaba en búsquedas tipo loop (loops iterativos que recargan todo el contexto en cada pasada, consumiendo tokens masivamente).

---

## 3. Solución de Rescate

**Solución definitiva:**
1. Cerrar Antigravity completamente
2. Desinstalar desde Panel de Control
3. Borrar `%APPDATA%\Roaming\Antigravity` completo (incluye el LevelDB corrupto y el Credential Manager local)
4. Reinstalar desde `antigravity.google` — última versión limpia
5. El workspace (`C:\dev\Sonido_Liquido_V5`) fue retenido en memoria de la nueva instalación — el desinstalador no limpia preferencias de workspace

**Resultado:** Gy respondió normalmente tras el reinstalo limpio.

---

## 4. Blindaje Profiláctico Implementado

Para prevenir recurrencia, se implementó un sistema de higiene en tres frentes:

### A. `scripts/check_health.ps1` (NUEVO — V5 y Tom)

Ejecutado automáticamente en el **DESPERTAR**, antes de cualquier otra operación. Escanea el directorio de logs más reciente de Antigravity y detecta:

- Patrones críticos en cualquier `.log`: `key not found`, `state syncing error`, `Failed to get OAuth token`
- Parpadeo de tokens en `auth.log`: más de 5 refreshes OAuth en una sola sesión = IPC degradado

Si detecta señales: muestra protocolo de emergencia escalado con instrucciones de reinstalo.

### B. `scripts/purgar_gy.ps1` (NUEVO — V5 y Tom)

Limpieza profiláctica ejecutable al cierre. Purga los archivos transitorios de `%APPDATA%\Roaming\Antigravity\` que acumulan degradación:

**Carpetas purgadas:** Cache, GPUCache, Code Cache, blob_storage, Network, Service Worker, WebStorage, Local Storage, Session Storage, SharedStorage, CachedData, CachedExtensionVSIXs, DawnGraphiteCache, DawnWebGPUCache, VideoDecodeStats, Crashpad, Shared Dictionary, shared_proto_db, logs de sesiones anteriores al día actual.

**Carpetas intocadas:** `User\`, `Workspaces\`, `Preferences`

Reporta MB liberados por carpeta.

### C. Integración en CIERRE.ps1 (V5 y Tom) — Paso 6

La purga se integró como paso 6 del Protocolo OMEGA con **doble confirmación obligatoria**:

1. **Primera barrera:** PIN 1974 (confirma que no se consultará más a Gy en la jornada)
2. **Segunda barrera:** Escribir literalmente `PURGAR` (palabra huérfana de todos los protocolos — ningún agente la escribe por inercia)

**Por qué doble confirmación:** Carlos frecuentemente hace repreguntas a Gy después del Omega. Nike (arquitecta) y Gy mismo tienden a cerrar sus prompts con "Adelante PIN 1974", lo que podría disparar la purga por inercia antes de que Carlos termine de trabajar.

### D. Documentación en OMEGA.md (V5 y Tom) — FASE 7

Agregada como fase obligatoria del protocolo de cierre, con explicación completa del riesgo de acumulación, carpetas purgadas, carpetas protegidas y regla de doble confirmación.

---

## 5. Síntomas Tempranos a Vigilar (para futura IA que lea esto)

Si Gy empieza a mostrar alguno de estos signos, actuar antes de que llegue al bloqueo total:

- Latencia inusual en el "Thinking"
- Gy habla de archivos ya cerrados (state syncing degradado)
- Ícono de cuenta parpadeando en la barra de estado
- check_health.ps1 reporta más de 5 refreshes OAuth en auth.log

**Protocolo ante bloqueo total:** Ir directamente a Output → Antigravity. Si aparece `key not found` o `Failed to get OAuth token` → no hay solución parcial. Desinstalar + borrar AppData\Roaming\Antigravity + reinstalar.

---

## 6. Sistemas Afectados

| Sistema | Directorio | Cambios aplicados |
|---|---|---|
| V5 (Desarrollo) | `C:\dev\Sonido_Liquido_V5` | check_health, purgar_gy, CIERRE paso 6, OMEGA FASE 7, DESPERTAR paso 0 |
| Tom (Satélite Producción) | `C:\dev\v5-ls-Tom` | Ídem (DESPERTAR.bat adaptado a formato .bat) |

---

## 7. Conclusión

La sesión rescató a Gy de un bloqueo total por bug sistémico de IPC OAuth. Se estableció un sistema de prevención a tres niveles (detección temprana al despertar, purga profiláctica al cierre, doble confirmación anti-inercia de agentes) que reduce significativamente la probabilidad de recurrencia. La División de Trabajo Trinity queda ratificada: búsquedas/análisis forense → Claude Code; ejecución/edición directa → Gy.

---
**Sello de Cierre**: Protocolo OMEGA Ejecutado. PIN 1974.  
**Redactado por**: Claude Code — a pedido de Carlos para memoria histórica del sistema.
