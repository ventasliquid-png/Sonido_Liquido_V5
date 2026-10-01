# [IDENTIDAD] - scripts/backup_semanal.py
# S876 (2026-10-01) -- cierra el rojo P4 de ALFA ("producción no tiene backup periódico en el Silo")
"""
Backup semanal automático de la base de producción, pensado para correr en cada arranque
(`scripts\\ARRANQUE_V5.bat`, paso 1.4, ANTES de aplicar migraciones).

Si el último respaldo guardado tiene más de DIAS_MAXIMOS días, copia la base con la API de backup
de SQLite (consistente aunque esté en modo WAL y con el servidor andando), corre PRAGMA
integrity_check sobre la copia y la deja en el Silo (Drive). Si el Silo no está montado, la deja en
data\\backups_locales\\ y avisa. NUNCA frena el arranque: pase lo que pase sale con código 0.

No borra copias viejas: avisa cuando pasan de AVISO_CANTIDAD y decide Carlos (misma regla que
backup_produccion.py, que es la copia por red que se hace desde OF al cierre de cada sesión; los dos
comparten carpeta, así que una copia de OF de hace tres días cuenta como respaldo reciente).

USO:
  python scripts/backup_semanal.py                       (lo que corre el lanzador)
  python scripts/backup_semanal.py --forzar              (guarda aunque haya un respaldo reciente)
  python scripts/backup_semanal.py --db RUTA --destino CARPETA --dias 7   (pruebas)
"""

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path

DB_DEFECTO = Path("data") / "V5_LS_MASTER.db"          # relativo al directorio del lanzador (la raíz de P)
DESTINO_SILO = Path("Q:/Mi unidad/V5_Silo_Claude/BACKUPS_DB/PRODUCCION_P")
DIAS_MAXIMOS = 7
AVISO_CANTIDAD = 15
PREFIJO = "PRODUCCION_P"


def _ultimo_respaldo(carpeta: Path):
    """Devuelve (ruta, edad_en_dias) del respaldo .db más nuevo de la carpeta, o (None, None)."""
    if not carpeta.is_dir():
        return None, None
    copias = [p for p in carpeta.glob(f"{PREFIJO}*.db") if p.is_file()]
    if not copias:
        return None, None
    nueva = max(copias, key=lambda p: p.stat().st_mtime)
    return nueva, (time.time() - nueva.stat().st_mtime) / 86400.0


def _respaldar(origen: Path, destino_dir: Path) -> Path:
    """Copia consistente con la API de backup de SQLite, la verifica y devuelve la ruta final."""
    destino_dir.mkdir(parents=True, exist_ok=True)
    nombre = f"{PREFIJO}_semanal_al_{datetime.now():%Y%m%d_%H%M%S}.db"   # con segundos: dos corridas seguidas no se pisan
    final = destino_dir / nombre
    parcial = destino_dir / (nombre + ".parcial")
    # Conexión normal (no solo lectura): una base en WAL con restos de un cierre sucio necesita poder recuperarse para leerse.
    # La API de backup no escribe en la base de origen.
    src = sqlite3.connect(str(origen), timeout=30)
    dst = sqlite3.connect(str(parcial))
    try:
        src.backup(dst)
        dst.commit()
        ok = dst.execute("PRAGMA integrity_check").fetchone()[0]
    except Exception:
        dst.close()
        src.close()
        parcial.unlink(missing_ok=True)   # nunca dejar una copia a medias en la carpeta de respaldos
        raise
    dst.close()
    src.close()
    if ok != "ok":
        parcial.unlink(missing_ok=True)
        raise RuntimeError(f"la copia no pasó integrity_check: {ok}")
    os.replace(parcial, final)
    return final


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", type=Path, default=DB_DEFECTO)
    ap.add_argument("--destino", type=Path, default=DESTINO_SILO)
    ap.add_argument("--dias", type=float, default=DIAS_MAXIMOS)
    ap.add_argument("--forzar", action="store_true", help="guardar aunque haya un respaldo reciente")
    args = ap.parse_args(argv)

    print("[BACKUP SEMANAL] revisando respaldo de la base...")
    try:
        if not args.db.is_file():
            print(f"[BACKUP SEMANAL] No se encontró la base ({args.db}). No se hace nada.")
            return 0

        # Silo montado = la carpeta de BACKUPS_DB existe (la subcarpeta de producción se crea si falta).
        destino = args.destino
        silo_ok = destino.is_dir() or destino.parent.is_dir()
        if not silo_ok:
            destino = args.db.resolve().parent / "backups_locales"
            print(f"[BACKUP SEMANAL] AVISO: el Silo no está montado; el respaldo va a {destino}")

        ultimo, edad = _ultimo_respaldo(destino)
        if ultimo is not None and edad < args.dias and not args.forzar:
            print(f"[BACKUP SEMANAL] Último respaldo hace {edad:.1f} días ({ultimo.name}): no hace falta otro.")
            return 0

        cuando = "no hay ninguno" if ultimo is None else f"el último tiene {edad:.1f} días"
        print(f"[BACKUP SEMANAL] {cuando}: respaldando {args.db} ...")
        final = _respaldar(args.db, destino)
        print(f"[BACKUP SEMANAL] OK: {final} ({final.stat().st_size / 1e6:.1f} MB, integridad ok)")

        try:  # bitácora mínima de la última corrida; si falla, no importa
            (destino / "estado_semanal.json").write_text(
                json.dumps({"ultimo": final.name, "fecha": datetime.now().isoformat(timespec="seconds")}, indent=2),
                encoding="utf-8")
        except Exception:
            pass

        cantidad = len(list(destino.glob(f"{PREFIJO}*.db")))
        if cantidad > AVISO_CANTIDAD:
            print(f"[BACKUP SEMANAL] AVISO: hay {cantidad} copias en {destino}; avisar a Carlos para que decida cuáles borrar.")
    except Exception as e:  # el backup NUNCA frena el arranque de producción
        print(f"[BACKUP SEMANAL] ERROR (no frena el arranque): {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
