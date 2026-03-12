import sys
import os
import subprocess
import re
from manager_status import read_bits, get_current_host_bit, write_bits

def check_git_weight():
    """
    Sensor de Peso: La Aduana Técnica.
    Parse git count-objects -vH and aborts if > 50MB.
    """
    try:
        output = subprocess.check_output(["git", "count-objects", "-vH"]).decode()
        # Find 'size-pack: X' and 'size: Y'
        # Example: 'size: 30.17 MiB' or 'size-pack: 0 bytes'
        size_match = re.search(r"size:\s+([\d\.]+)\s+(\w+)", output)
        pack_match = re.search(r"size-pack:\s+([\d\.]+)\s+(\w+)", output)
        
        total_kb = 0.0
        
        def to_kb(val, unit):
            u = unit.lower()
            if 'mib' in u: return val * 1024
            if 'gib' in u: return val * 1024 * 1024
            if 'kib' in u or 'kb' in u: return val
            return val / 1024 # bytes

        if size_match:
            total_kb += to_kb(float(size_match.group(1)), size_match.group(2))
        if pack_match:
            total_kb += to_kb(float(pack_match.group(1)), pack_match.group(2))
            
        return total_kb / 1024 # Return MiB
    except Exception as e:
        print(f"[ADUANA] Error calculando peso: {e}")
        return 999.0 # Fail safe: assume heavy

def execute_omega():
    print("\n=== PROTOCOLO OMEGA V2.0 (ADUANA TÉCNICA VANGUARD) ===")
    
    # 1. SENSOR DE PESO (LA ADUANA)
    repo_weight = check_git_weight()
    print(f"[ADUANA] Peso detectado: {repo_weight:.2f} MiB")
    
    if repo_weight > 50.0:
        print(f"!!!! ERROR FATAL: REPOSITORIO OBESO ({repo_weight:.2f} MiB) !!!!")
        print("[ADUANA] El umbral crítico de 50MB ha sido superado. Push bloqueado.")
        print("[ADUANA] Ejecute purga nuclear o revise archivos pesados antes de cerrar.")
        sys.exit(1)
    
    # 2. AUTORIZACIÓN (BLOQUEO DE SEGURIDAD)
    pin_ingresado = input(">> AUTORIZACIÓN REQUERIDA. Ingrese PIN de seguridad (OMEGA): ").strip()
    if pin_ingresado != "1974":
        print("[OMEGA] ACCESO DENEGADO: PIN incorrecto. Freno de mano activado.")
        sys.exit(1)
        
    print("[OMEGA] AUTORIZACIÓN CONFIRMADA. Procesando Bitmask 64-bit...")
    
    # 3. LÓGICA VANGUARD (RUTAS DINÁMICAS)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=base_dir).decode().strip()
        # [VANGUARD] git add -u (Solo archivos controlados)
        subprocess.check_call(["git", "add", "-u"], cwd=base_dir)
        status = subprocess.check_output(["git", "status", "--short"], cwd=base_dir).decode().strip()
        is_clean = len(status) == 0
        is_stable_branch = "universal" in branch or "master" in branch or "main" in branch
    except Exception as e:
        print(f"[OMEGA] Fallo en Git: {e}")
        branch = "unknown"
        is_clean = False
        is_stable_branch = False

    # 4. CÁLCULO DE BITS (64-BIT / GENOMA)
    # Python maneja BigInt de forma nativa. 1 << 63 es válido.
    new_bits = 0
    
    # Bit de Origen
    origin_bit = get_current_host_bit()
    new_bits |= (1 << origin_bit)
    
    # Bits de Estado (Genoma)
    if is_stable_branch and is_clean:
        new_bits |= (1 << 0) # SOBERANO
        print("[OMEGA] Estado: SOBERANO")
    else:
        new_bits |= (1 << 1) # TRINCHERA
        print("[OMEGA] Estado: TRINCHERA")

    # [GENOMA 64-bit] Preservar bits existentes (máscara completa)
    old_bits = read_bits()
    new_bits |= (old_bits & 0xFFFFFFFFFFFFFFFF)

    # 5. PERSISTENCIA Y CIERRE
    # manager_status.write_bits ahora persiste en 8 bytes (BigInt)
    if write_bits(new_bits):
        print(f"[OMEGA] Genoma 64-bit Actualizado: {new_bits}")
        print(f"[OMEGA] Cierre exitoso en {branch}. Listo para Push.")
        
        do_push = input(">> ¿Desea ejecutar push automático a GitHub? (S/N): ").lower().strip()
        if do_push == 's':
            print("[OMEGA] Sincronizando con Vanguard Cloud...")
            try:
                subprocess.check_call(["git", "push", "origin", branch], cwd=base_dir)
                print("[OK] Sincronización completa.")
            except:
                print("[ERROR] Falló el push. Verifique conexión.")
    else:
        print("[OMEGA] ERROR CRÍTICO: Fallo en persistencia de bits.")

if __name__ == "__main__":
    execute_omega()
