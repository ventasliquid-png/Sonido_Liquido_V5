import pandas as pd
import sys

# Force encoding
sys.stdout.reconfigure(encoding='utf-8')

try:
    df = pd.read_excel('pedidos_raw.xlsx', header=None)
    
    # Find Header
    header_idx = -1
    for idx, row in df.iterrows():
        txt = " ".join([str(x).lower() for x in row if pd.notna(x)])
        if 'descripcion' in txt and ('cant' in txt or 'precio' in txt or 'cod' in txt):
            header_idx = idx
            print(f"✅ PATRON DETECTADO: Encabezado en Fila {idx+1}")
            print(f"   {row.values}")
            break
            
    if header_idx != -1:
        print("\n📦 EJEMPLO DE ITEMS (Primeros 3):")
        print(df.iloc[header_idx+1:header_idx+4].to_string(index=False, header=False))
    else:
        print("⚠️ No encontré patrón 'Descripcion + Cantidad'.")

    # Find CUIT
    for idx, row in df.head(20).iterrows():
        txt = " ".join([str(x) for x in row if pd.notna(x)])
        if '30-' in txt or '20-' in txt or '27-' in txt or '23-' in txt or '30657362324' in txt: # Generic CUIT pattern
             print(f"\n🏢 DATO CLIE DETECTADO (Fila {idx+1}): {txt}")

except Exception as e:
    print(e)
