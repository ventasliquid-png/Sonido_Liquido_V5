# CLAUDE.md — Briefing de Proyecto: Sonido Líquido V5

> Este archivo es leído automáticamente por Claude Code al iniciar.
> Proporciona contexto esencial del proyecto, arquitectura y protocolos operativos.
> Los protocolos ALFA y OMEGA son compartidos con Gy — modificar solo en `ALFA.md` y `OMEGA.md`.

---

## 0. SECUENCIA DE DESPERTAR (EJECUTAR PRIMERO)

Al iniciar sesión, antes de cualquier otra acción, preguntar:

> **"¿Hace falta reposición de GIT? (S/N)"**

- **Si S:** Proponer ejecución de `git pull origin [rama_actual]` y mostrar el mensaje:
  > *"No olvides descargar la base de datos de tu Drive si no es actual la que tenés."*
- **Si N:** Continuar con el despertar normalmente.

---

## 1. Identidad del Proyecto

**Sistema:** Sonido Líquido V5 — ERP/Logística para empresa argentina de distribución  
**Operador:** Carlos (arquitecto y decisor final de todas las acciones)  
**Estado actual:** Inauguración de producción en curso

---

## 2. Entornos

| Entorno | Directorio | Base de datos | Rama Git |
|---|---|---|---|
| Desarrollo | `C:\dev\Sonido_Liquido_V5` | `pilot_v5x.db` | `stable-v5-of-20260330` |
| Producción | `C:\dev\V5-LS` | `V5_LS_MASTER.db` | `stable-v5-of-20260330` |

**Regla crítica:** Las bases de datos (`.db`) están en `.gitignore` y NO se versionan.  
La base de producción es `V5_LS_MASTER.db` — 32 registros gold, schema certificado.

---

## 3. Stack Tecnológico

- **Backend:** FastAPI + SQLAlchemy + SQLite (puerto 8080)
- **Frontend:** Vue.js 3 + Pinia (puerto 5173 o Vite default)
- **Lenguaje:** Python (backend), JavaScript (frontend)
- **Control de versiones:** Git con múltiples ramas y remotos

---

## 4. Arquitectura de Agentes (Trinity + Atenea)

Carlos opera con una estructura de IAs colaborativas. Claude Code es uno de los nodos.

| Agente | Plataforma | Rol |
|---|---|---|
| **Gy** | Antigravity (Gemini CLI/IDE) | Ejecución táctica, refactors, código directo |
| **Atenea** | Claude (arquitecta) | Consejera arquitectónica, segunda opinión |
| **Nike** | — | Protocolo/operaciones |
| **Almirante** | — | Supervisión estratégica |
| **Claude Code** | Anthropic CLI | Análisis forense, consultoría, segunda opinión |

**Carlos actúa como cartero estrella** — intermedia entre agentes, porta contexto entre sesiones.

---

## 5. Protocolos Operativos

### Protocolo ALFA — Inicio de sesión
El ALFA **no es texto, es ejecución**. Antes de cualquier trabajo, se corre el Canario:

```cmd
python scripts/canario_v2.py
```

El Canario verifica:
1. ¿Existe la base de datos? ¿Tiene el schema correcto?
2. ¿Existe el registro LAVIMAR (UUID de calibración)?
3. ¿`flags_estado` de LAVIMAR tiene el valor nominal?

**Resultado esperado:** `INTEGRITY: NOMINAL GOLD` con `flags_estado = 8205`  
Si el Canario falla → **no se opera**. Se diagnostica primero.

### Registro de calibración LAVIMAR
- **UUID:** `e1be0585cd3443efa33204d00e199c4e`
- **`flags_estado` nominal (V15):** `8205`
- **`flags_estado` legacy (V14):** `13` ← valor histórico, no usar como referencia en V15

> Scripts de diagnóstico alternativos (versiones anteriores, no canónicas):
> `canary_alfa.py`, `verify_alfa.py`, `verify_alfa_integrity.py`, `audit_alfa.py`

### Protocolo OMEGA — Cierre de sesión
- Consolidar trabajo realizado
- Documentar cambios
- Ejecutar `git add / commit` con mensaje que incluya PIN 1974 si es entrega crítica

### PIN de autorización
Ciertas acciones críticas requieren el PIN `1974` como confirmación explícita de Carlos.

---

## 6. Arquitectura de Datos Clave

### `flags_estado` (bitmask)
Campo crítico presente en múltiples tablas. **Atención semántica:**
- **V14:** Bit 20 con semántica directa
- **V15:** Bit 20 con inversión semántica (cambio crítico)

No asumir comportamiento de bits sin verificar la versión del esquema.

### Sistema de domicilios (en transición)
- **Legacy:** modelo `Domicilio`
- **Nuevo:** modelo `VinculoGeografico`
- Coexisten durante la transición arquitectónica — no es un bug, es diseño intencional

---

## 7. Modo de Operación de Claude Code

- ✅ Puede leer y analizar el código libremente
- ✅ Puede sugerir cambios, refactors y mejoras
- ⚠️ Acciones destructivas (sobrescribir bases, eliminar archivos) requieren confirmación explícita de Carlos
- ❌ No ejecutar migraciones de schema sin autorización
- ❌ No modificar `V5_LS_MASTER.db` sin PIN 1974

---

## 8. Locaciones Físicas

| Código | Descripción |
|---|---|
| **OF** | Oficina (locación actual) |
| **CA** | Casa |

El repo se sincroniza entre locaciones via Git. Las bases de datos se respaldan manualmente en Google Drive.

---

## 9. Notas para Claude Code

- El proyecto está en un estado de transición deliberada ("Cubo Rubik") — aparente desorden que responde a una secuencia de movimientos planificada
- Algunos `print()` de debug son intencionales durante la transición
- Las discrepancias entre modelos ORM y schema SQLite son el problema más frecuente — siempre verificar con `check_model_discrepancies.py` ante errores 500
- Gy (Antigravity) es el agente de ejecución primario — Claude Code opera como consultor y segunda opinión

---

*Última actualización: 2026-03-31 — OF*
