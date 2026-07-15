"""
generar_contexto_cs.py — Genera puntero mínimo de contexto para CS nuevo
Uso: python scripts/generar_contexto_cs.py
"""
import json
import re
from datetime import datetime
from pathlib import Path

PATRON_FECHA = re.compile(r'^\d{4}-\d{2}-\d{2}_')

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
    """
    Solo considera archivos con convencion de fecha YYYY-MM-DD_ al inicio del
    nombre -- otros .md sueltos en la carpeta (handoffs, mensajes, sesiones
    transitorias archivadas por nombre propio) rompen el orden alfabetico
    simple si ordenamos por nombre completo (S850: 'SESION_TRANSITORIA...'
    quedaba "primero" porque 'S' > '2' en ASCII, pese a ser de junio).
    """
    carpeta = SILO / "INFORMES_HISTORICOS"
    archivos = sorted(
        (f for f in carpeta.glob("*.md") if PATRON_FECHA.match(f.name)),
        reverse=True,
    )
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
