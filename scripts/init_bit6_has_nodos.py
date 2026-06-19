"""
init_bit6_has_nodos.py — Inicialización Bit 6 (HAS_NODOS=64) en empresas_transporte
======================================================================================
Setea flags_estado bit 6 (valor 64) en todas las empresas que tienen al menos
un nodo_transporte asociado.

Uso:
    python scripts/init_bit6_has_nodos.py                  # auto-detecta DB
    python scripts/init_bit6_has_nodos.py --db PATH/a/db   # override de path

Idempotente: no modifica empresas que ya tienen el bit seteado.
"""

import sqlite3
import os
import sys
import argparse
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))


def resolve_db(db_override=None):
    if db_override:
        return os.path.abspath(db_override)
    env_url = os.environ.get("DATABASE_URL", "")
    if env_url.startswith("sqlite:///"):
        path = env_url.replace("sqlite:///", "")
        if not os.path.isabs(path):
            path = os.path.join(PROJECT_ROOT, path)
        return os.path.abspath(path)
    if "Sonido_Liquido_V5" in PROJECT_ROOT:
        return os.path.join(PROJECT_ROOT, "pilot_v5x.db")
    else:
        return os.path.join(PROJECT_ROOT, "V5_LS_MASTER.db")


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")


def main():
    parser = argparse.ArgumentParser(description="Inicializa Bit 6 HAS_NODOS en empresas_transporte")
    parser.add_argument("--db", dest="db_path", default=None, help="Override path de DB")
    args = parser.parse_args()

    db_path = resolve_db(args.db_path)

    if not os.path.exists(db_path):
        log(f"ERROR — DB no encontrada: {db_path}")
        sys.exit(1)

    log(f"DB: {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()

        cur.execute("""
            UPDATE empresas_transporte
            SET flags_estado = flags_estado | 64
            WHERE id IN (
                SELECT DISTINCT empresa_id FROM nodos_transporte
            )
            AND (flags_estado & 64) = 0
        """)
        filas = cur.rowcount
        conn.commit()

        if filas > 0:
            log(f"OK — {filas} empresa(s) actualizadas con Bit 6 (HAS_NODOS=64)")
        else:
            log("OK — Sin cambios (todas las empresas ya tienen Bit 6 seteado o no aplica)")

    except Exception as e:
        log(f"ERROR: {e}")
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
