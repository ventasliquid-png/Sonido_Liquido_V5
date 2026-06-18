"""
generar_contexto_cs.py — Genera paquete de contexto para CS nuevo
Uso: python scripts/generar_contexto_cs.py
"""
import json
from datetime import datetime
from pathlib import Path

SILO = Path(r"Q:\Mi unidad\V5_Silo_Claude")
REPO_D = Path(r"C:\dev\Sonido_Liquido_V5")

def leer_ultimas_filas(path, n=10):
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        return "\n".join(lines[-n:])
    except:
        return "(no disponible)"

def leer_archivo(path):
    try:
        return path.read_text(encoding="utf-8")
    except:
        return "(no disponible)"

def leer_status_of():
    try:
        status = json.loads((SILO / "SISTEMA_STATUS.json").read_text(encoding="utf-8"))
        of = status.get("maquinas", {}).get("OF", {})
        return f"""version: {status.get('version')}
banderas_rojas_activas: {status.get('banderas_rojas_activas')}
cherry_pendiente_MT_a_D: {status.get('cherry_pendiente_MT_a_D')}
OF:
  omega_cerrado: {of.get('omega_cerrado')}
  fecha_ultimo_omega: {of.get('fecha_ultimo_omega')}
  hash_D: {of.get('hash_D')}
  hash_P: {of.get('hash_P')}
  cs_checkpoint: {of.get('cs_checkpoint')}
  system_flags: {of.get('system_flags')}"""
    except:
        return "(no disponible)"

# --- Main ---
ahora = datetime.now().strftime("%Y-%m-%d_%H-%M")
salida = SILO / f"CONTEXTO_CS_{ahora}.md"

contenido = f"""# CONTEXTO PARA CS NUEVO — {ahora}
Generado por: generar_contexto_cs.py
Instrucción: subí este archivo + PROMPT_INSTALACION_CLAUDE_V4.0.md a la nueva sesión de CS.

---

## SESION_NEXT.md

{leer_archivo(SILO / "SESION_NEXT.md")}

---

## BITACORA_VIVA.md (ultimas 10 filas)

{leer_ultimas_filas(SILO / "BITACORA_VIVA.md")}

---

## SISTEMA_STATUS.json (OF)

{leer_status_of()}

---

## INSTRUCCION PARA CS NUEVO

Sos el arquitecto de sesion (CS) de Sonido Liquido V5.
El estado del sistema esta arriba. La proxima tarea esta en SESION_NEXT.md.
La bitacora viva muestra las ultimas instrucciones ejecutadas.
Q: no esta disponible desde claude.ai — toda la informacion necesaria esta en este archivo.
Esperando instruccion de Carlos.
"""

salida.write_text(contenido, encoding="utf-8")
print(f"Contexto generado: {salida}")
