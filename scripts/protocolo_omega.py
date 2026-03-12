import sys
import os
import subprocess
from manager_status import manage, read_bits, get_current_host_bit, write_bits

def execute_omega():
    print("=== EJECUTANDO PROTOCOLO OMEGA (CIERRE) ===")
    
    # FRENO DE MANO: Autorización con PIN
    pin_ingresado = input(">> AUTORIZACIÓN REQUERIDA. Ingrese PIN de seguridad (OMEGA): ").strip()
    if pin_ingresado != "1974":
        print("[OMEGA] ACCESO DENEGADO: PIN incorrecto o cancelado. Freno de mano activado.")
        sys.exit(1)
        
    print("[OMEGA] AUTORIZACIÓN CONFIRMADA (PIN ACEPATDO). Iniciando cierre...")
    
    # 1. Auditoría de Git
    try:
        branch = subprocess.check_output(["git", "branch", "--show-current"], cwd="c:/dev/Sonido_Liquido_V5").decode().strip()
        status = subprocess.check_output(["git", "status", "--short"], cwd="c:/dev/Sonido_Liquido_V5").decode().strip()
        is_clean = len(status) == 0
        is_stable_branch = "master" in branch or "universal" in branch
    except:
        branch = "unknown"
        is_clean = False
        is_stable_branch = False

    # 2. Cálculo de Bits
    new_bits = 0
    
    # Bit de Origen (Host Actual)
    origin_bit = get_current_host_bit()
    new_bits |= (1 << origin_bit)
    
    # Bit de Estado (0: Soberano, 1: Trinchera)
    if is_stable_branch and is_clean:
        new_bits |= (1 << 0) # Soberano
        print("[OMEGA] Estado: SOBERANO")
    else:
        new_bits |= (1 << 1) # Trinchera
        print("[OMEGA] Estado: TRINCHERA (Pendientes en Git)")

    # Mantener Bit 2 (Carta) si ya está o si hay una carta reciente
    old_bits = read_bits()
    if old_bits & (1 << 2):
        new_bits |= (1 << 2)

    # 3. Persistencia
    if write_bits(new_bits):
        print(f"[OMEGA] Bits guardados: {new_bits}")
        print(f"[OMEGA] Sesión cerrada desde: {origin_bit}")
    else:
        print("[OMEGA] ERROR: No se pudieron guardar los bits.")

if __name__ == "__main__":
    execute_omega()
