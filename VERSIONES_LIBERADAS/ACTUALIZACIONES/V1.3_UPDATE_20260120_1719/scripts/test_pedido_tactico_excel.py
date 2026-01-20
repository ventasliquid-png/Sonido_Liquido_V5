
import sys
import os
import pandas as pd
from io import BytesIO

# Agregar raíz al path
sys.path.append(os.getcwd())

def test_excel_generation():
    print("Testing Pandas/Openpyxl Excel Generation...")
    
    items_excel_data = [
        {
            "Fecha": "12/12/2025",
            "Cliente": "Cliente Test S.A.",
            "CUIT": "30-12345678-9",
            "Producto": "Producto Prueba",
            "SKU": "12345",
            "Cantidad": 10,
            "Precio Unitario": 1500.50,
            "Subtotal": 15005.00,
            "Nota": "Nota de prueba"
        }
    ]

    try:
        df = pd.DataFrame(items_excel_data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Pedido')
        
        output.seek(0)
        content = output.getvalue()
        
        print(f"SUCCESS: Generated Excel file of {len(content)} bytes.")
        
        # Opcional: Guardar en disco para ver si abre
        with open("test_pedido.xlsx", "wb") as f:
            f.write(content)
        print("Saved 'test_pedido.xlsx' for manual inspection.")
        
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_excel_generation()
