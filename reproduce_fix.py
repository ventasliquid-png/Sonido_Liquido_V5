from decimal import Decimal

# Simulate the failing scenario
class MockProduct:
    def __init__(self, stock_reservado):
        self.stock_reservado = stock_reservado

def test_decimal_addition():
    # Initial state (from Numeric/Decimal in DB)
    stock = Decimal("10.0")
    producto = MockProduct(stock)
    
    # Value from frontend (float)
    cantidad_float = 5.5
    
    print(f"Initial Stock: {producto.stock_reservado} ({type(producto.stock_reservado)})")
    print(f"Quantity to add: {cantidad_float} ({type(cantidad_float)})")
    
    # This would fail: producto.stock_reservado += cantidad_float
    try:
        producto.stock_reservado += Decimal(str(cantidad_float))
        print(f"New Stock: {producto.stock_reservado} ({type(producto.stock_reservado)})")
        assert producto.stock_reservado == Decimal("15.5")
        print("FIX VERIFIED: Addition works correctly with Decimal(str(float))")
    except TypeError as e:
        print(f"FIX FAILED: Still getting TypeError: {e}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_decimal_addition()
