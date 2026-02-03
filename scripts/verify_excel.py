import pandas as pd
import os
import time

file_path = r"LISTAS_PRECIO/Proveedores/Celtrap/Celtrap (2).xlsx"

if os.path.exists(file_path):
    print(f"File found: {file_path}")
    print(f"Size: {os.path.getsize(file_path)} bytes")
    print(f"Last modified: {time.ctime(os.path.getmtime(file_path))}")
    
    try:
        xls = pd.ExcelFile(file_path)
        print("Sheets in file:", xls.sheet_names)
        if "2026-02" in xls.sheet_names:
            print("✅ SUCCESS: Sheet '2026-02' exists.")
        else:
            print("❌ FAILURE: Sheet '2026-02' NOT found.")
    except Exception as e:
        print(f"Error reading Excel: {e}")
else:
    print(f"File NOT found at {file_path}")
