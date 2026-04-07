import sys
import os
import subprocess
from manager_status import read_bits, get_current_host_bit, write_bits

def omega_manual():
    print("--- PROTOCOLO OMEGA (AUTOMATIZADO V5.7) ---")
    branch = "main"
    is_clean = True
    
    # 1. Calcular Bits
    new_bits = 0
    origin_bit = get_current_host_bit()
    new_bits |= (1 << origin_bit)
    new_bits |= (1 << 0) # SOBERANO
    
    old_bits = read_bits()
    new_bits |= (old_bits & 0xFFFFFFFFFFFFFFFF)
    
    # 2. Persistencia
    if write_bits(new_bits):
        print(f"[OK] Genoma 64-bit Actualizado: {new_bits}")
        print("[OK] Protocolo Omega Completado (Estado NOMINAL GOLD)")
    else:
        print("[ERR] Fallo al actualizar bits")

if __name__ == "__main__":
    omega_manual()
