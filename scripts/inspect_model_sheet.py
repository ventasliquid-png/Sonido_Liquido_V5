import pandas as pd

file_path = r"LISTAS_PRECIO/Proveedores/Celtrap/Celtrap (2).xlsx"

try:
    # Read the model sheet "2025-05" validation
    # Skip preamble rows if necessary. Based on user image, row 4 (index 3) seems to be headers.
    # Let's read the first 10 rows to see layout.
    df = pd.read_excel(file_path, sheet_name="2025-05", header=None, nrows=10)
    print("--- RAW CONTENT 2025-05 (First 10 rows) ---")
    print(df.to_string())
    
except Exception as e:
    print(f"Error reading 2025-05: {e}")
