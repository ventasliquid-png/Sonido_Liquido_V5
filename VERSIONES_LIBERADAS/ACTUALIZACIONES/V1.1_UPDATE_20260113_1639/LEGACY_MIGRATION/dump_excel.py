import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
df = pd.read_excel('pedidos_raw.xlsx', header=None)

print("--- RAW DUMP TOP 25 ROWS ---")
for i, row in df.head(25).iterrows():
    # Filter NaNs
    vals = [str(x) for x in row if pd.notna(x)]
    if vals:
        print(f"Row {i+1}: {' | '.join(vals)}")
