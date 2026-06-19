"""
migrate_safe.py — Orquestador de Migraciones V5
================================================
Detecta y aplica migraciones pendientes sobre la DB correcta.
Hace backup automático antes de tocar nada. Rollback automático si falla.

Uso:
    python scripts/migrate_safe.py --check    # solo verifica, no aplica
    python scripts/migrate_safe.py            # aplica pendientes
    python scripts/migrate_safe.py --db PATH  # override de path de DB

Integración con ARRANQUE_V5.bat:
    python scripts/migrate_safe.py --check > nul 2>&1
    if errorlevel 1 -> ejecutar sin --check antes de levantar uvicorn
"""

import sqlite3
import os
import sys
import shutil
import argparse
from datetime import datetime

# ── REGISTRO DE MIGRACIONES ───────────────────────────────────────────────────
NRO_SESION = 830

MIGRATIONS = [
    {
        "id": "032_contacto_responsable_id",
        "description": "Card #75 — contacto_responsable_id en pedidos (FK -> vinculos.id)",
        "table": "pedidos",
        "column": "contacto_responsable_id",
        "sql": "ALTER TABLE pedidos ADD COLUMN contacto_responsable_id TEXT REFERENCES vinculos(id)",
    },
    {
        "id": "033_nodo_transporte_id",
        "description": "Card #76 — nodo_transporte_id en pedidos (FK -> nodos_transporte.id)",
        "table": "pedidos",
        "column": "nodo_transporte_id",
        "sql": "ALTER TABLE pedidos ADD COLUMN nodo_transporte_id TEXT REFERENCES nodos_transporte(id)",
    },
]

# ── PATHS ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
LOG_FILE = os.path.join(SCRIPT_DIR, "migration_log.txt")


# ── HELPERS ───────────────────────────────────────────────────────────────────

def log(msg: str, check_only: bool = False):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    if not check_only:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")


def resolve_db(db_override: str = None) -> str:
    if db_override:
        return os.path.abspath(db_override)

    # Mismo mecanismo que database.py — respetar DATABASE_URL si está definida
    env_url = os.environ.get("DATABASE_URL", "")
    if env_url.startswith("sqlite:///"):
        path = env_url.replace("sqlite:///", "")
        if not os.path.isabs(path):
            path = os.path.join(PROJECT_ROOT, path)
        return os.path.abspath(path)

    # Detección por ruta del script: D vs P
    if "Sonido_Liquido_V5" in PROJECT_ROOT:
        return os.path.join(PROJECT_ROOT, "pilot_v5x.db")
    else:
        return os.path.join(PROJECT_ROOT, "V5_LS_MASTER.db")


def backup_db(db_path: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = os.path.splitext(db_path)[0]
    backup_path = f"{base}_backup_{ts}.db"
    shutil.copy2(db_path, backup_path)
    return backup_path


def restore_db(backup_path: str, db_path: str):
    shutil.copy2(backup_path, db_path)


def ensure_control_table(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (
            id VARCHAR PRIMARY KEY,
            nro_sesion INTEGER,
            aplicada_en DATETIME DEFAULT (datetime('now'))
        )
    """)
    conn.commit()


def is_applied(conn: sqlite3.Connection, migration_id: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (migration_id,)
    ).fetchone()
    return row is not None


def column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(col[1] == column for col in cols)


def get_pending(conn: sqlite3.Connection) -> list:
    return [m for m in MIGRATIONS if not is_applied(conn, m["id"])]


def apply_migration(conn: sqlite3.Connection, m: dict):
    try:
        conn.execute(m["sql"])
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            # Columna ya existe por otro medio — registrar y seguir
            pass
        else:
            raise
    conn.execute(
        "INSERT OR IGNORE INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)",
        (m["id"], NRO_SESION),
    )


def verify_migration(conn: sqlite3.Connection, m: dict):
    if not column_exists(conn, m["table"], m["column"]):
        raise RuntimeError(
            f"VERIFY FAIL — columna '{m['column']}' no encontrada en '{m['table']}' "
            f"tras aplicar {m['id']}"
        )


# ── ORQUESTADOR ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Orquestador de migraciones V5")
    parser.add_argument("--check", action="store_true", help="Solo verifica pendientes, no aplica")
    parser.add_argument("--db", dest="db_path", default=None, help="Override path de DB")
    args = parser.parse_args()

    check_only = args.check
    db_path = resolve_db(args.db_path)

    if not os.path.exists(db_path):
        msg = f"ERROR — DB no encontrada: {db_path}"
        log(msg, check_only)
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    ensure_control_table(conn)
    pending = get_pending(conn)
    conn.close()

    # ── MODO CHECK ────────────────────────────────────────────────────────────
    if check_only:
        if pending:
            ids = ", ".join(m["id"] for m in pending)
            print(f"[migrate_safe] PENDING: {ids}")
            sys.exit(1)
        else:
            print("[migrate_safe] OK — sin migraciones pendientes")
            sys.exit(0)

    # ── MODO APPLY ────────────────────────────────────────────────────────────
    if not pending:
        log(f"OK — sin migraciones pendientes. DB: {db_path}")
        sys.exit(0)

    ids = ", ".join(m["id"] for m in pending)
    log(f"DB: {db_path}")
    log(f"PENDING: {ids}")

    backup_path = backup_db(db_path)
    log(f"Backup: {os.path.basename(backup_path)}")

    conn = sqlite3.connect(db_path)
    try:
        for m in pending:
            log(f"APPLY {m['id']} — {m['description']}")
            apply_migration(conn, m)
            verify_migration(conn, m)
            log(f"VERIFY {m['id']} — OK")
        conn.commit()
        log(f"SUCCESS — {len(pending)} migracion(es) aplicada(s)")
    except Exception as e:
        log(f"FAILURE: {e}")
        conn.close()
        restore_db(backup_path, db_path)
        log("Backup restaurado — DB sin cambios")
        sys.exit(1)
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
