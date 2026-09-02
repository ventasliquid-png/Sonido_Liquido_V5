# [IDENTIDAD] - scripts/auto_migrar.py
"""
Actualizacion automatica de esquema al arranque (Card #123, S859).

Detecta migraciones pendientes (comparando MIGRATION_ID de cada migrate_*.py contra
_migraciones_aplicadas), hace un backup de seguridad SOLO si hay algo para aplicar,
y las corre en orden. Pensado para que un operador sin conocimiento tecnico (Tomy)
nunca vea un 500 por una migracion que se quedo pendiente entre el codigo y el dato --
mismo modelo que una actualizacion de OS: silenciosa si no hay nada que hacer, un
aviso simple mientras corre, y frena con instrucciones claras si algo falla en vez
de arrancar el servidor sobre una base a medio migrar.

Reusa _env_db.detectar_entorno_db() (misma funcion que ya usan canario_v2.py y
exportar_pedidos_excel.py) en vez de reinventar la deteccion de ruta/entorno.
"""
import glob
import os
import re
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime

from _env_db import detectar_entorno_db

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))


def migraciones_disponibles():
    """Lee MIGRATION_ID de cada migrate_*.py sin ejecutarlo -- solo texto."""
    archivos = sorted(glob.glob(os.path.join(SCRIPTS_DIR, "migrate_*.py")))
    resultado = []
    for path in archivos:
        with open(path, "r", encoding="utf-8") as f:
            contenido = f.read()
        # findall + ultimo match, no el primero: migrate_000 tiene un
        # MIGRATION_ID de ejemplo en su docstring antes de la asignacion real.
        matches = re.findall(r'MIGRATION_ID\s*=\s*"([^"]+)"', contenido)
        if matches:
            resultado.append((matches[-1], path))
    return resultado


def ids_aplicadas(db_path):
    if not os.path.exists(db_path):
        return set()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='_migraciones_aplicadas'"
    )
    if not cur.fetchone():
        conn.close()
        return set()
    cur.execute("SELECT id FROM _migraciones_aplicadas")
    ids = {row[0] for row in cur.fetchall()}
    conn.close()
    return ids


def main():
    db_path, entorno = detectar_entorno_db()

    if not os.path.exists(db_path):
        print(f"[auto_migrar] Base no encontrada en {db_path} -- nada que verificar.")
        return 0

    disponibles = migraciones_disponibles()
    aplicadas = ids_aplicadas(db_path)
    pendientes = [(mid, path) for mid, path in disponibles if mid not in aplicadas]

    if not pendientes:
        return 0

    print("--- [ACTUALIZACION] Preparando actualizacion del sistema... ---")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA wal_checkpoint(FULL)")
    conn.close()
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.pre_auto_migrar_{fecha}.bak"
    shutil.copy(db_path, backup_path)
    print(f"--- [ACTUALIZACION] Backup de seguridad: {os.path.basename(backup_path)} ---")

    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path}"

    for mid, path in pendientes:
        print(f"--- [ACTUALIZACION] Aplicando {mid}... ---")
        resultado = subprocess.run(
            [sys.executable, path], env=env, capture_output=True, text=True
        )
        if resultado.stdout:
            print(resultado.stdout.strip())
        if resultado.returncode != 0:
            print("=" * 60)
            print("[ACTUALIZACION] ERROR -- no se pudo aplicar una actualizacion del sistema.")
            print(f"Migracion afectada: {mid}")
            print(resultado.stderr.strip())
            print(f"Backup de seguridad disponible en: {backup_path}")
            print("No se inicio el servidor. Avisar a Carlos antes de reintentar.")
            print("=" * 60)
            return 1

    print("--- [ACTUALIZACION] Sistema actualizado correctamente. ---")
    return 0


if __name__ == "__main__":
    sys.exit(main())
