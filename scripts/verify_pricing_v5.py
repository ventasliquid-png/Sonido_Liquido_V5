
import sys
import os
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.pricing_engine import calculate_lists, smart_round, get_virtual_price

def test_smart_rounding():
    print("\n--- TEST: Smart Rounding ---")
    cases = [
        (Decimal("7.892"), Decimal("7.89")),   # Range A
        (Decimal("99.994"), Decimal("99.99")), # Range A
        (Decimal("150.50"), Decimal("151")),   # Range B
        (Decimal("150.49"), Decimal("150")),   # Range B
        (Decimal("4150.00"), Decimal("4200")), # Range C
        (Decimal("4149.00"), Decimal("4100")), # Range C
        (Decimal("22400.00"), Decimal("22000")), # Range D
        (Decimal("22600.00"), Decimal("23000")), # Range D
    ]
    
    for val, expected in cases:
        result = smart_round(val)
        status = "✅" if result == expected else f"❌ (Expected {expected})"
        print(f"Input: {val:<10} | Result: {result:<10} | {status}")

def test_cascade_barbijos():
    print("\n--- TEST: Cascade (Barbijos Example) ---")
    costo = Decimal("5.1725")
    rent = Decimal("30")
    
    listas = calculate_lists(costo, rent)
    
    # Validation
    # L1 Raw: 5.1725 * 1.3 = 6.72425
    # L2 Raw: 6.72425 * 1.105 = 7.43029625
    
    print(f"Costo: {costo}, Rent: {rent}%")
    for k, v in listas.items():
        if k.startswith("_"): continue
        print(f"{k}: {v}")
        
    # Check L1
    l1_expected = Decimal("6.72")
    if listas['lista_1'] == l1_expected:
        print(f"✅ Lista 1 Correct ({l1_expected})")
    else:
        print(f"❌ Lista 1 Failed (Expected {l1_expected}, Got {listas['lista_1']})")

def test_client_logic():
    print("\n--- TEST: Client DNA ---")
    
    class MockSegment:
        def __init__(self, n): self.nivel = n
        
    class MockCliente:
        def __init__(self, nivel): self.segmento = MockSegment(nivel)
        
    class MockProductoCosto:
        def __init__(self, c, r):
            self.costo_reposicion = c
            self.rentabilidad_target = r
            
    prod_costos = MockProductoCosto(Decimal("100"), Decimal("30")) # L1 Raw = 130
    
    # Test Levels 1 to 7
    for nivel in range(1, 8):
        cliente = MockCliente(nivel)
        res = get_virtual_price(prod_costos, cliente)
        precio = res['precio']
        print(f"Cliente Nivel {nivel} -> Precio: {precio}")

if __name__ == "__main__":
    test_smart_rounding()
    test_cascade_barbijos()
    test_client_logic()
