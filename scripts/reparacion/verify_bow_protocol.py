# scripts\reparacion\verify_bow_protocol.py
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.clientes.service import ClienteService

casos = [
    ("El Taller SRL", "SRL El Taller"),
    ("Inapyr S.R.L.", "Inapyr SRL"),
    ("Carlos Gomez", "GOMEZ CARLOS"),
    ("La Gran Manzana", "MANZANA LA GRAN")
]

print("--- [TEST] Protocolo de Tokenización Alfabética (Bag of Words) ---")
for c1, c2 in casos:
    can1 = ClienteService.normalize_name(c1)
    can2 = ClienteService.normalize_name(c2)
    match = "MATCH" if can1 == can2 else "FAIL"
    print(f"[{match}]")
    print(f"  A: '{c1}' -> {can1}")
    print(f"  B: '{c2}' -> {can2}")
