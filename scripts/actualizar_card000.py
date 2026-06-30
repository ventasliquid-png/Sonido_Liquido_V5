"""
actualizar_card000.py — Card #70 Paso 5
Actualiza Card #000 en BOARD_V5.xlsx con el estado actual del ecosistema.
Enciende/apaga Bit 7 (BOARD_PENDIENTE) en SISTEMA_STATUS.json según cards PENDIENTE.
Usar en OMEGA antes del commit.
"""
import subprocess, json, openpyxl
from datetime import date
from pathlib import Path

SILO = Path(r"Q:\Mi unidad\V5_Silo_Claude")
BOARD = SILO / "BOARD_V5.xlsx"
STATUS = SILO / "SISTEMA_STATUS.json"
REPO_D = Path(r"C:\dev\Sonido_Liquido_V5")
REPO_P = Path(r"C:\dev\v5-ls-Tom\current")
IDENTIDAD = (REPO_D / ".gy_identity").read_text().strip()

def git_hash(repo):
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                          cwd=repo, capture_output=True, text=True)
        return r.stdout.strip()
    except:
        return "unknown"

def git_sesion():
    """Lee número de sesión desde Caja Negra."""
    caja = REPO_D / "_GY/_MD/CAJA_NEGRA.md"
    try:
        for line in caja.read_text(encoding="utf-8").splitlines():
            if "sesion" in line.lower() or "sesión" in line.lower():
                nums = [s for s in line.split() if s.isdigit()]
                if nums:
                    return nums[-1]
    except:
        pass
    return "???"

def leer_status():
    try:
        return json.loads(STATUS.read_text(encoding="utf-8"))
    except:
        return {}

def semaforo(status):
    maq = status.get("maquinas", {}).get(IDENTIDAD, {})
    sf = maq.get("system_flags", 0)
    ESPEJO = (1 << 60) | (1 << 61) | (1 << 62)
    TERMICA = 1
    if sf & TERMICA:
        return "🔴 TORMENTA", "[ROJO] TORMENTA"
    if status.get("banderas_rojas_activas", 0) > 0:
        return "🔴 BANDERAS ROJAS", "[ROJO] BANDERAS ROJAS"
    if (sf & ESPEJO) == ESPEJO:
        return "🟢 NOMINAL", "[VERDE] NOMINAL"
    return "🟡 ALERTA", "[AMARILLO] ALERTA"

def contar_pendientes(ws):
    """Cuenta cards con estado PENDIENTE en Board V5."""
    header_row = None
    for r in range(1, 10):
        if ws.cell(row=r, column=1).value == "ID":
            header_row = r
            break
    if header_row is None:
        return 0
    estado_col = None
    for idx, cell in enumerate(ws[header_row]):
        if cell.value == "Estado":
            estado_col = idx + 1
            break
    if estado_col is None:
        return 0
    return sum(
        1 for r in range(header_row + 1, ws.max_row + 1)
        if ws.cell(row=r, column=estado_col).value == "PENDIENTE"
    )


def actualizar_bit7(status, count_pendientes):
    """Enciende Bit 7 (BOARD_PENDIENTE=128) si hay cards PENDIENTE; lo apaga si no.
    Escribe SISTEMA_STATUS.json en el lugar."""
    BIT_BOARD_PENDIENTE = 1 << 7
    sf = status.get("maquinas", {}).get(IDENTIDAD, {}).get("system_flags", 0)
    if count_pendientes > 0:
        sf |= BIT_BOARD_PENDIENTE
    else:
        sf &= ~BIT_BOARD_PENDIENTE
    status["maquinas"][IDENTIDAD]["system_flags"] = sf
    STATUS.write_text(json.dumps(status, indent=2, ensure_ascii=False), encoding="utf-8")
    return sf


# --- Main ---
hash_d = git_hash(REPO_D)
hash_p = git_hash(REPO_P)
sesion = git_sesion()
status = leer_status()
estado, estado_log = semaforo(status)
hoy = date.today().isoformat()

wb = openpyxl.load_workbook(BOARD)
ws = wb["Board V5"]

# Contar pendientes y actualizar Bit 7 en SISTEMA_STATUS
pendientes = contar_pendientes(ws)
sf_final = actualizar_bit7(status, pendientes)

# Card #000 siempre en fila 2
ws["J2"] = f"Hash D: {hash_d} | Hash P: {hash_p}"
ws["K2"] = hoy
ws["I2"] = f"Sesión {sesion} | {IDENTIDAD} | {estado}"

wb.save(BOARD)
print(f"Card #000 actualizada -- {estado_log} | D={hash_d} P={hash_p} | Sesion {sesion} | Pendientes={pendientes}")
