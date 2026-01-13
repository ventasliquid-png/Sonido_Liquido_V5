import pandas as pd
import os

FILE_PATH = 'pedidos_raw.xlsx'

def analyze_excel():
    if not os.path.exists(FILE_PATH):
        print(f"❌ Error: No encontré el archivo '{FILE_PATH}' en la raíz.")
        return

    print(f"🕵️‍♂️ Analizando: {FILE_PATH}...\n")
    
    try:
        xls = pd.ExcelFile(FILE_PATH)
        print(f"📂 Hojas encontradas: {xls.sheet_names}")
        
        for sheet_name in xls.sheet_names:
            print(f"\n--- Analizando Hoja: '{sheet_name}' ---")
            df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            
            # 1. Exploración visual de las primeras filas (Contexto)
            print("👁️ Primeras 15 filas (Estructura Cruda):")
            print(df.head(15).to_string(index=True, header=False, na_rep='.'))
            
            # 2. Búsqueda de Cabeceras de Tabla
            # Buscamos filas que contengan palabras clave de items
            keywords_items = ['codigo', 'código', 'cod', 'descripcion', 'descripción', 'producto', 'detalle', 'cant', 'cantidad', 'precio', 'unitario', 'total']
            
            header_row_idx = -1
            for idx, row in df.iterrows():
                # Convert row to string, lowercase
                row_str = " ".join([str(x).lower() for x in row if pd.notna(x)])
                matches = [key for key in keywords_items if key in row_str]
                if len(matches) >= 3: # Si tiene al menos 3 de estas palabras, es muy probable que sea el header
                    header_row_idx = idx
                    print(f"\n📍 Detecté posible ENCABEZADO DE ITEMS en fila {idx+1}:")
                    print(f"   {row.values}")
                    print(f"   (Palabras clave: {matches})")
                    break
            
            if header_row_idx != -1:
                print(f"\n📉 Datos probables (primeras 5 filas post-encabezado):")
                print(df.iloc[header_row_idx+1:header_row_idx+6].to_string(index=True, header=False, na_rep='.'))
            else:
                print("\n⚠️ No detecté una estructura de tabla de items clara (Headers estándar).")

            # 3. Búsqueda de Metadatos (Cliente, Fecha)
            print("\n🔍 Buscando Metadatos (Cliente / Fecha / Totales):")
            found_meta = []
            for idx, row in df.head(15).iterrows(): # Generalmente arriba
                 row_str = " ".join([str(x) for x in row if pd.notna(x)])
                 if any(x in row_str.lower() for x in ['cliente', 'razon', 'señores', 'sres', 'fecha', 'cuit', 'pedido']):
                     found_meta.append((idx, row_str))
            
            for idx, txt in found_meta:
                 print(f"   Fila {idx+1}: {txt[:100]}...")

    except Exception as e:
        print(f"❌ Error crítico leyendo el archivo: {e}")

if __name__ == "__main__":
    analyze_excel()
