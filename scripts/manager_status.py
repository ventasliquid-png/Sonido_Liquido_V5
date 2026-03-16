import sys
import os
import socket

# CONFIGURACIÓN DE GEOMETRÍA LÓGICA
REPOSITORIO_BITS = r"C:\dev\session_status.bit"

# Mapeo de COMPUTERNAME a Bits de Origen (5, 6, 7)
# Bit 5 (32): OFICINA
# Bit 6 (64): CASA
# Bit 7 (128): NOTEBOOK
HOST_MAPPING = {
    "OFICINA-PC": 5,    # Ejemplo, se ajustará con detección real
    "DESKTOP-CASA": 6,  # Ejemplo
    "NOTEBOOK-GY": 7    # Ejemplo
}

BIT_MAP = {
    0: "SOBERANO (Master)",
    1: "TRINCHERA (Chernobyl)",
    2: "CARTA (Momento Cero)",
    3: "CRÍTICO (Bloqueo)",
    4: "PARIDAD_DB (Check Drive)",
    5: "ORIGEN_OF",
    6: "ORIGEN_CA",
    7: "ORIGEN_NB",
    8: "SABUESO_READY (Injectado)",
    9: "SABUESO_TOKEN (AFIP Active)",
    13: "HISTORIA (Desvirgado)",
    15: "VIRGEN (Sin Movimientos)",
    16: "MULTI_DESTINO (Check UI)",
    20: "PENDIENTE_REVISION (Faltan Datos)",
    30: "CH_TIENDANUBE",
    31: "CH_MLIBRE",
    32: "CH_GOOGLE",
    33: "CH_RRSS (Instagram/FB)"
}

def get_current_host_bit():
    host = os.environ.get("COMPUTERNAME", socket.gethostname()).upper()
    # Lógica heurística de detección si no hay mapeo exacto
    if "CASA" in host or "HOME" in host or "USUARIO" in host: # Fallback común en este entorno
        return 6
    if "OFIC" in host or "WORK" in host:
        return 5
    if "NB" in host or "LAPTOP" in host or "NOTE" in host:
        return 7
    return 6 # Default a Casa si no se reconoce

def read_bits():
    if not os.path.exists(REPOSITORIO_BITS):
        return 0
    try:
        with open(REPOSITORIO_BITS, "rb") as f:
            # [GENOMA 64-bit] Reading 8 bytes for BigInt support
            data = f.read(8)
            return int.from_bytes(data, byteorder="big") if data else 0
    except:
        return 0

def write_bits(value):
    try:
        with open(REPOSITORIO_BITS, "wb") as f:
            # [GENOMA 64-bit] Persisting 8 bytes (BigInt) as per Vanguard Doctrine
            f.write(value.to_bytes(8, byteorder="big"))
        return True
    except Exception as e:
        print(f"Error escribiendo bits: {e}")
        return False

def manage(action, bit_index=None):
    current = read_bits()
    
    if action == "set" and bit_index is not None:
        current |= (1 << bit_index)
        write_bits(current)
    elif action == "clear" and bit_index is not None:
        current &= ~(1 << bit_index)
        write_bits(current)
    elif action == "read":
        # Detección de Host
        host_now = os.environ.get("COMPUTERNAME", socket.gethostname())
        bit_now = get_current_host_bit()
        
        # Identificar origen guardado
        saved_origin_bit = None
        for b in [5, 6, 7]:
            if current & (1 << b):
                saved_origin_bit = b
        
        status_desc = []
        for b, desc in BIT_MAP.items():
            if current & (1 << b):
                status_desc.append(desc)
        
        print(f"VALUE:{current}")
        print(f"HOST_ACTUAL:{host_now}")
        print(f"BIT_ACTUAL:{bit_now}")
        print(f"ORIGEN_GUARDADO:{saved_origin_bit if saved_origin_bit else 'N/A'}")
        print(f"STATUS_STR:{' | '.join(status_desc) if status_desc else 'LIMPIO'}")
        
        # Alerta de Desincro
        if saved_origin_bit and saved_origin_bit != bit_now:
            print("ALERT:DESINCRO_DETECTADA")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: manager_status.py [read|set|clear] [bit_index]")
        sys.exit(1)
        
    cmd = sys.argv[1].lower()
    idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
    manage(cmd, idx)
