"""
backup_db.py — Backup DB V5 con rotación dinámica por antigüedad
Reemplaza el mecanismo POLIZON (binarios .bak en git).

ESQUEMA DE SLOTS (por DB: MAESTRO y DESARROLLO)
  Slot 1  } ventana rodante de 3 días:
  Slot 2  }   nuevo día  → desplazar 2→3, 1→2; escribir nuevo en slot1
  Slot 3  }   mismo día  → sobreescribir slot1 si hash cambió, sino skip
  Slot 4    se refresca cuando (hoy - fecha_slot4) >= 14 días
  Slot 5    cascade desde slot4 si además (hoy - fecha_slot5) >= 35 días

GUARD DE HASH
  Slots 1-3: no se escribe el archivo fuente→slot1 si el hash no cambió
              (en nuevo día: aun así se desplazan 2→3 y 1→2 para mantener invariante)
  Slot 4:    no se reescribe si hash fuente == hash almacenado en slot4;
              solo se actualiza la fecha
  Slot 5:    no se reescribe si hash slot4 == hash almacenado en slot5;
              solo se actualiza la fecha (cascade de metadatos)

USO:
  python "Q:\\Mi unidad\\V5_Silo_Claude\\backup_db.py"
  python backup_db.py --forzar-historico
"""

import hashlib
import json
import shutil
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# ── Rutas ─────────────────────────────────────────────────────────────────────
SILO        = Path(r"Q:\Mi unidad\V5_Silo_Claude")
ROTATIVO    = SILO / "BACKUPS_DB" / "ROTATIVO"
HISTORICO   = SILO / "BACKUPS_DB" / "HISTORICO"
LOCAL_BIMES = Path(r"C:\V5_Backups_Bimestral")
ESTADO_FILE = SILO / "BACKUPS_DB" / "estado_backup.json"

FUENTES = {
    # V5_LS_MASTER.db vive en el Silo Drive en MC (el .env de v5-ls-Tom apunta a pilot_v5x.db).
    # Cuando se sincroniza desde MT, el destino canónico es esta ruta.
    "MAESTRO":    SILO / "V5_LS_MASTER.db",
    "DESARROLLO": Path(r"C:\dev\Sonido_Liquido_V5\pilot_v5x.db"),
}

MIN_BYTES      = 100 * 1024  # 100 KB — guard de placeholder vacío
DIAS_BIMESTRAL = 60


# ── Utilidades ─────────────────────────────────────────────────────────────────

def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def dias_desde(fecha_str, hoy: date):
    """Retorna días entre fecha_str (ISO) y hoy, o None si fecha_str es None."""
    if not fecha_str:
        return None
    return (hoy - date.fromisoformat(fecha_str)).days


def slot_path(nombre: str, n: int) -> Path:
    return ROTATIVO / f"{nombre}_{n:02d}.db"


def mb(path: Path) -> float:
    return path.stat().st_size / 1_048_576


def estado_vacio() -> dict:
    slots = {}
    for nombre in FUENTES:
        slots[nombre] = {
            str(n): {"fecha": None, "hash": None} for n in range(1, 6)
        }
    return {"slots": slots, "historico": {"ultimo_snapshot": None}}


def cargar_estado() -> dict:
    if ESTADO_FILE.exists():
        return json.loads(ESTADO_FILE.read_text(encoding="utf-8"))
    return estado_vacio()


def guardar_estado(estado: dict) -> None:
    ESTADO_FILE.write_text(
        json.dumps(estado, indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ── Slots 1-3: ventana rodante de 3 días ──────────────────────────────────────

def manejar_slots_1_3(nombre: str, fuente: Path, slots: dict, hoy: date, hash_vivo: str) -> None:
    hoy_str     = hoy.isoformat()
    s1          = slots["1"]
    cambio_dia  = s1["fecha"] != hoy_str
    hash_cambio = hash_vivo != s1["hash"]

    if not cambio_dia and not hash_cambio:
        print(f"  [SKIP] {nombre} slots 1-3: mismo día, DB sin cambios")
        return

    if cambio_dia:
        # Desplazar archivos físicos 2→3 y 1→2 (mantiene invariante archivo↔hash)
        p1 = slot_path(nombre, 1)
        p2 = slot_path(nombre, 2)
        if p2.exists():
            shutil.copy2(p2, slot_path(nombre, 3))
        if p1.exists():
            shutil.copy2(p1, slot_path(nombre, 2))
        # Desplazar metadata
        slots["3"] = dict(slots["2"])
        slots["2"] = dict(slots["1"])

        if hash_cambio:
            shutil.copy2(fuente, p1)
            slots["1"] = {"fecha": hoy_str, "hash": hash_vivo}
            print(f"  [OK]   {nombre} slots 1-3 rotados — nuevo día, DB actualizada ({mb(fuente):.1f} MB)")
        else:
            # Archivo slot1 ya tiene el hash correcto; no se reescribe
            slots["1"]["fecha"] = hoy_str
            print(f"  [OK]   {nombre} slots 1-3 rotados — nuevo día, DB sin cambios (fecha actualizada)")
    else:
        # Mismo día, hash cambió → sobreescribir slot1
        shutil.copy2(fuente, slot_path(nombre, 1))
        slots["1"] = {"fecha": hoy_str, "hash": hash_vivo}
        print(f"  [OK]   {nombre} slot1 sobrescrito — mismo día, DB actualizada ({mb(fuente):.1f} MB)")


# ── Slots 4-5: umbrales de días con cascade 4→5 ───────────────────────────────

def manejar_slots_4_5(nombre: str, fuente: Path, slots: dict, hoy: date, hash_vivo: str) -> None:
    hoy_str = hoy.isoformat()
    s4      = slots["4"]
    s5      = slots["5"]
    dias4   = dias_desde(s4["fecha"], hoy)
    dias5   = dias_desde(s5["fecha"], hoy)
    umbral4 = dias4 is None or dias4 >= 14
    umbral5 = dias5 is None or dias5 >= 35

    if not umbral4:
        print(f"  [SKIP] {nombre} slot4: faltan {14 - dias4} día(s) para umbral (14 días)")
        return

    # Evaluar cascade slot4 → slot5 ANTES de refrescar slot4
    p4 = slot_path(nombre, 4)
    p5 = slot_path(nombre, 5)

    if umbral5:
        if p4.exists() and s4["hash"] is not None:
            if s4["hash"] != s5["hash"]:
                shutil.copy2(p4, p5)
                print(f"  [CASCADE] {nombre} slot4 -> slot5 ({mb(p4):.1f} MB)")
            else:
                print(f"  [SKIP cascade] {nombre} slot5: contenido identico a slot4 (fecha actualizada)")
            slots["5"] = {"fecha": hoy_str, "hash": s4["hash"]}
        else:
            print(f"  [SKIP cascade] {nombre} slot5: slot4 vacio o sin hash, nada que cascadear")
    else:
        print(f"  [SKIP] {nombre} slot5: faltan {35 - dias5} día(s) para umbral (35 días)")

    # Refrescar slot4 desde DB en vivo
    if hash_vivo != s4["hash"]:
        shutil.copy2(fuente, p4)
        slots["4"] = {"fecha": hoy_str, "hash": hash_vivo}
        print(f"  [OK]   {nombre} slot4 << DB actualizada ({mb(fuente):.1f} MB)")
    else:
        slots["4"]["fecha"] = hoy_str
        print(f"  [SKIP] {nombre} slot4: DB sin cambios (fecha actualizada)")


# ── Snapshot bimestral ────────────────────────────────────────────────────────

def snapshot_bimestral(nombre: str, fuente: Path, hoy: date) -> None:
    if not fuente.exists() or fuente.stat().st_size < MIN_BYTES:
        print(f"  [SKIP] {nombre}: fuente no disponible o placeholder vacío")
        return
    stamp      = hoy.strftime("%Y%m%d")
    dest_silo  = HISTORICO   / f"{nombre}_{stamp}.db"
    dest_local = LOCAL_BIMES / f"{nombre}_{stamp}.db"
    LOCAL_BIMES.mkdir(parents=True, exist_ok=True)
    shutil.copy2(fuente, dest_silo)
    shutil.copy2(fuente, dest_local)
    print(f"  [OK]   {nombre} -> HISTORICO/{dest_silo.name} ({mb(dest_silo):.1f} MB)")
    print(f"  [OK]   {nombre} -> C:\\V5_Backups_Bimestral\\{dest_local.name} (redundancia local)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    forzar_historico = "--forzar-historico" in sys.argv
    ahora = datetime.now()
    hoy   = ahora.date()
    estado = cargar_estado()

    print("=" * 58)
    print("  BACKUP V5 — OMEGA RITUAL")
    print(f"  {ahora.strftime('%Y-%m-%d %H:%M')}")
    print("=" * 58)

    for nombre, fuente in FUENTES.items():
        print(f"\n[{nombre}]")
        if not fuente.exists():
            print(f"  [SKIP] Fuente no encontrada: {fuente}")
            continue
        if fuente.stat().st_size < MIN_BYTES:
            print(f"  [SKIP] Fuente < {MIN_BYTES // 1024} KB — placeholder vacío")
            continue

        hash_vivo = md5_file(fuente)
        slots     = estado["slots"][nombre]

        manejar_slots_1_3(nombre, fuente, slots, hoy, hash_vivo)
        manejar_slots_4_5(nombre, fuente, slots, hoy, hash_vivo)

    # Bimestral
    print("\n[HISTORICO]")
    hist      = estado["historico"]
    dias_hist = dias_desde(hist.get("ultimo_snapshot"), hoy)
    hacer_hist = forzar_historico or dias_hist is None or dias_hist >= DIAS_BIMESTRAL

    if hacer_hist:
        if forzar_historico:
            razon = "--forzar-historico"
        elif dias_hist is None:
            razon = "primer snapshot"
        else:
            razon = f"{dias_hist} días desde el último ({hist['ultimo_snapshot']})"
        print(f"  Disparando snapshot histórico ({razon})")
        for nombre, fuente in FUENTES.items():
            snapshot_bimestral(nombre, fuente, hoy)
        hist["ultimo_snapshot"] = hoy.isoformat()
        proximo = hoy + timedelta(days=DIAS_BIMESTRAL)
        print(f"  Próximo bimestral: {proximo.isoformat()}")
    else:
        proximo = date.fromisoformat(hist["ultimo_snapshot"]) + timedelta(days=DIAS_BIMESTRAL)
        print(f"  [SKIP] Faltan {DIAS_BIMESTRAL - dias_hist} días (próximo: {proximo.isoformat()})")

    guardar_estado(estado)

    print("\n" + "=" * 58)
    print("  BACKUP COMPLETADO")
    print("=" * 58)


if __name__ == "__main__":
    main()
