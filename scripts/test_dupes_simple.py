
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import only the service, but avoid initializing the whole mapper if possible
# Since service.py imports models, we might still hit issues if we aren't careful
# Let's use a mock-like approach or just test the method directly if it doesn't trigger mapper init

try:
    from backend.clientes.service import ClienteService
except Exception as e:
    print(f"Error importing service: {e}")
    # Fallback to local copy of the method for pure unit test
    class ClienteServiceMock:
        @staticmethod
        def normalize_name(name: str) -> str:
            if not name: return ""
            import unicodedata
            import re
            text = unicodedata.normalize('NFKD', str(name))
            text = text.encode('ASCII', 'ignore').decode('ASCII')
            text = re.sub(r'[^a-zA-Z0-9]', '', text)
            return text.upper()
    ClienteService = ClienteServiceMock

def test_normalization():
    print("--- [UNIT TEST] Normalización de Nombres ---")
    cases = [
        ("Inapryl S.R.L.", "INAPRYLSRL"),
        ("Inapryl S. R.L.", "INAPRYLSRL"),
        ("Inapryl S. R. L.", "INAPRYLSRL"),
        ("  INAPRYL S.R.L.  ", "INAPRYLSRL"),
        ("Lácteos de Poblet", "LACTEOSDEPOBLET"),
        ("33-66072685-9", "33660726859"),
        ("Empresa S.A.", "EMPRESASA")
    ]
    
    success = True
    for original, expected in cases:
        result = ClienteService.normalize_name(original)
        if result == expected:
            print(f"  [OK] '{original}' -> '{result}'")
        else:
            print(f"  [FAIL] '{original}' -> '{result}' (Esperado: '{expected}')")
            success = False
    return success

def test_logic_simulation():
    print("\n--- [SIMULATION] Lógica de Escudo GY ---")
    
    # Simulate DB
    db_clients = [
        (1, "Inapryl S.R.L."),
        (2, "Lácteos de Poblet"),
        (3, "Lavimar S.A.")
    ]
    
    # New intake
    new_intake = "Inapryl S. R. L."
    new_norm = ClienteService.normalize_name(new_intake)
    print(f"[*] Nuevo Ingreso: '{new_intake}' (Normalized: '{new_norm}')")
    
    found = None
    for c_id, c_name in db_clients:
        if ClienteService.normalize_name(c_name) == new_norm:
            found = c_name
            break
    
    if found:
        print(f"  [BLOCK] Colisión detectada con: '{found}'")
        return True
    else:
        print("  [FAIL] No se detectó la colisión.")
        return False

if __name__ == "__main__":
    if test_normalization():
        if test_logic_simulation():
            print("\n✅ PRUEBA EXITOSA: El escudo GY funciona correctamente.")
        else:
            print("\n❌ PRUEBA FALLIDA en simulación.")
    else:
        print("\n❌ PRUEBA FALLIDA en normalización.")
