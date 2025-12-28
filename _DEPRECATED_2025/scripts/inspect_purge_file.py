import pandas as pd
import os

file_path = "productos_V5_purificado.xlsx"

if os.path.exists(file_path):
    print(f"Reading {file_path}...")
    try:
        df = pd.read_excel(file_path)
        print("Columns found:")
        print(df.columns.tolist())
        print("First 5 rows:")
        print(df.head())
        
        # Check column 7 (index 6)
        if len(df.columns) > 6:
            col_name = df.columns[6]
            print(f"\nAnalyzing column index 6: '{col_name}'")
            print(df[col_name].value_counts())
    except Exception as e:
        print(f"Error reading Excel: {e}")
else:
    print(f"File {file_path} not found.")
