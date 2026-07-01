"""
generar_contexto_cs.py — Genera puntero mínimo de contexto para CS nuevo
Uso: python scripts/generar_contexto_cs.py
"""
import json
from datetime import datetime
from pathlib import Path

SILO = Path(r"Q:\Mi unidad\V5_Silo_Claude")
REPO_D = Path(r"C:\dev\Sonido_Liquido_V5")
IDENTIDAD = (REPO_D / ".gy_identity").read_text().strip()

BITS_SEMAFORO = {16: "VERDE", 17: "AMARILLO", 18: "ROJO"}

def leer_maquina():
    status = json.loads((SILO / "SISTEMA_STATUS.json").read_text(encoding="utf-8"))
    return status.get("maquinas", {}).get(IDENTIDAD, {})

def color_semaforo(system_flags):
    for bit, nombre in BITS_SEMAFORO.items():
        if system_flags & (1 << bit):
            return nombre
    return "VERDE"  # default si ningun bit fue escrito aun

def ultimo_informe_historico():
    carpeta = SILO / "INFORMES_HISTORICOS"
    archivos = sorted(carpeta.glob("*.md"), reverse=True)
    return archivos[0].name if archivos else "(sin informes)"

# --- Main ---
ahora = datetime.now().strftime("%Y-%m-%d_%H-%M")
CARPETA_CS = SILO / "CONTEXTO_CS"
CARPETA_CS.mkdir(exist_ok=True)

# Limpiar anteriores
for viejo in CARPETA_CS.glob("CONTEXTO_CS_*.md"):
    viejo.unlink()

maquina = leer_maquina()
sf = maquina.get("system_flags", 0)
color = color_semaforo(sf)
informe = ultimo_informe_historico()

salida = CARPETA_CS / f"CONTEXTO_CS_{ahora}.md"

contenido = f"""# CONTEXTO_CS — puntero minimo
Generado: {ahora}
Maquina: {IDENTIDAD}

## Semaforo heredado
{color}

## Donde esta el resto
Informe Historico del dia: INFORMES_HISTORICOS/{informe}
-> seccion "DESTILADO CS" al final de ese archivo.
"""

salida.write_text(contenido, encoding="utf-8")
print(f"Contexto minimo generado: {salida} | Maquina: {IDENTIDAD} | Semaforo: {color}")
