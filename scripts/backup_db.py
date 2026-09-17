"""
backup_db.py (copia de D) — DELEGADOR, sin lógica propia (Card #137, S868).

La versión mantenida vive en el Silo: Q:\\Mi unidad\\V5_Silo_Claude\\backup_db.py
Esta copia había quedado vieja (sin la guarda anti-regresión de la Card #131, sin el Board
y sin la copia segura para bases en modo WAL), y OMEGA.md apuntaba a ella. Ahora solo
ejecuta la del Silo con los mismos argumentos. Si el Silo no está, falla: nunca se hace
backup con una copia desactualizada.
"""

import runpy
import sys
from pathlib import Path

SILO = Path(r"Q:\Mi unidad\V5_Silo_Claude\backup_db.py")

if not SILO.is_file():
    sys.exit(f"[ERROR] No se encuentra {SILO}. Q: no esta montado? No se hace backup con una copia vieja.")

sys.argv[0] = str(SILO)
runpy.run_path(str(SILO), run_name="__main__")
