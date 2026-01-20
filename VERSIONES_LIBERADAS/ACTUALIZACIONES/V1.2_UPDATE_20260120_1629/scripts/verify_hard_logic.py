
import sys
import os
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.pricing_engine import get_virtual_price

class MockListaPrecios:
    def __init__(self, orden):
        self.orden_calculo = orden

class MockCliente:
    def __init__(self, lista=None, segmento=None):
        self.lista_precios = lista
        self.segmento = segmento

class MockProductoCosto:
    def __init__(self, c, r):
        self.costo_reposicion = c
        self.rentabilidad_target = r

def verify_hard_logic():
    print("\n--- TEST: Hard Logic (ListaPrecios) ---")
    
    # Costo 100, Rent 30% -> L1=130
    # L2 = 130 * 1.105 = 143.65 -> 144
    # L3 = 143.65 * 1.105 = 158.73 -> 159
    prod = MockProductoCosto(Decimal("100"), Decimal("30"))
    
    # Case 1: Client with List 3 (Distribuidor)
    lista_distrib = MockListaPrecios(3)
    cliente_distrib = MockCliente(lista=lista_distrib) # No segment logic needed if List is present
    
    res = get_virtual_price(prod, cliente_distrib)
    
    print(f"Propósito: Cliente con Lista Orden 3 debe recibir precio L3.")
    print(f"Resultado: ${res['precio']} (Lista Origen: {res['lista_origen']})")
    
    expected = Decimal("159")
    if res['precio'] == expected and res['lista_origen'] == 3:
        print("✅ SUCCESS: Hard Logic Working.")
    else:
        print(f"❌ FAIL: Expected {expected} from List 3.")

if __name__ == "__main__":
    verify_hard_logic()
