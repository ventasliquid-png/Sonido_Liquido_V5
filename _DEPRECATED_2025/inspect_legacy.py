import pandas as pd
import os

FILE_PATH = r"C:\Users\USUARIO\Downloads\clientes discovery.xls"

def inspect():
    if not os.path.exists(FILE_PATH):
        print("f❌ File not found: {FILE_PATH}")
        return

    try:
        # Read header=None to see grid
        df = pd.read_excel(FILE_PATH, header=None, nrows=20)
        print("--- GRID VIEW (First 20 Rows) ---")
        print(df.to_string())
    except Exception as e:
        print(f"❌ Error reading Excel: {e}")

if __name__ == "__main__":
    inspect()
