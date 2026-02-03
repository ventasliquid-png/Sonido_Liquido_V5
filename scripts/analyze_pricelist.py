import pandas as pd
import os

file_path = r"c:\dev\Sonido_Liquido_V5\LISTAS_PRECIO\Celtrap (2).xlsx"

if not os.path.exists(file_path):
    print(f"File not found: {file_path}")
    exit()

try:
    xls = pd.ExcelFile(file_path)
    print("Sheets found:", xls.sheet_names)
    
    # Analyze the first few rows of the first and last sheet to understand structure
    for sheet in [xls.sheet_names[0], xls.sheet_names[-1]]:
        print(f"\n--- Analyzing Sheet: {sheet} ---")
        df = pd.read_excel(xls, sheet_name=sheet, nrows=5)
        print("Columns:", df.columns.tolist())
        print("First 2 rows:")
        print(df.head(2).to_string())
        
except Exception as e:
    print(f"Error analyzing Excel: {e}")
