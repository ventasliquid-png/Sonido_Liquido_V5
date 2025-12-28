import pandas as pd
import os

file_path = r"c:\dev\Sonido_Liquido_V5\pedidos_raw.xlsx"

def inspect_excel(path):
    if not os.path.exists(path):
        print(f"Error: File not found at {path}")
        return

    print(f"--- Ficha Técnica: {os.path.basename(path)} ---")
    
    try:
        xls = pd.ExcelFile(path)
        print(f"Hojas encontradas: {xls.sheet_names}")
        
        for sheet_name in xls.sheet_names:
            print(f"\n\n=== ANÁLISIS HOJA: '{sheet_name}' ===")
            # Leemos sin header primero para ver crudo qué hay
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None, nrows=10)
            print("Primeras 5 filas (crudo):")
            print(df.head(5).to_string())
            
            # Intento de inferencia de columnas basado en tipos de datos
            # El usuario dice:
            # Viejo: Desc | Cant | Costo | Total Costo | ... | Venta | Total Venta
            # Nuevo: Desc | Cant | Venta | Total Venta | ... | Costo | Total Costo
            
            # Vamos a intentar leer con header en fila 0 a ver si tiene titulos
            df_h = pd.read_excel(xls, sheet_name=sheet_name, nrows=5)
            print("\nPosibles Encabezados detectados:")
            print(df_h.columns.tolist())
            
    except Exception as e:
        print(f"Error reading Excel: {e}")

if __name__ == "__main__":
    inspect_excel(file_path)
