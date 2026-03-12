import pandas as pd
import os
from openpyxl import load_workbook

def update_excel_pricelist():
    excel_path = r"LISTAS_PRECIO/Proveedores/Celtrap/Celtrap (2).xlsx"
    csv_path = r"LISTAS_PRECIO/Proveedores/Celtrap/comparativa_precios_celtrap.csv"
    
    if not os.path.exists(excel_path):
        print(f"Error: No se encuentra el Excel: {excel_path}")
        return
    if not os.path.exists(csv_path):
        print(f"Error: No se encuentra el CSV: {csv_path}")
        return

    print(f"Leyendo CSV: {csv_path}")
    df_new = pd.read_csv(csv_path)

    # --- APLICAR REGLA DE NEGOCIO (Camilleros 301) ---
    # Logica: Si Codigo es 301, el Costo Nuevo es Costo Anterior * 1.10
    
    # Asegurar tipos numericos
    df_new['Codigo'] = pd.to_numeric(df_new['Codigo'], errors='coerce')
    df_new['Costo Anterior (2025)'] = pd.to_numeric(df_new['Costo Anterior (2025)'], errors='coerce').fillna(0)
    df_new['Costo Nuevo (Feb 2026)'] = pd.to_numeric(df_new['Costo Nuevo (Feb 2026)'], errors='coerce').fillna(0)

    # Identificar fila 301
    mask_301 = df_new['Codigo'] == 301
    
    if mask_301.any():
        print("Aplicando Regla Camilleros (301) -> +10%")
        # Calcular nuevo costo
        costo_anterior_301 = df_new.loc[mask_301, 'Costo Anterior (2025)']
        nuevo_costo_calc = costo_anterior_301 * 1.10
        
        # Actualizar dataframe
        df_new.loc[mask_301, 'Costo Nuevo (Feb 2026)'] = nuevo_costo_calc
        df_new.loc[mask_301, '% Aumento'] = 10.0
        df_new.loc[mask_301, 'Moneda'] = 'ARS (Regla 10%)'

    # --- ESCRIBIR EN EXCEL ---
    sheet_name = "2026-02"
    print(f"Agregando pestaña '{sheet_name}' a {excel_path}...")

    try:
        # Usar ExcelWriter con engine='openpyxl' y mode='a' (append)
        with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_new.to_excel(writer, sheet_name=sheet_name, index=False)
            
        print("✅ Excel actualizado exitosamente.")
        
    except Exception as e:
        print(f"Error al escribir Excel: {e}")

if __name__ == "__main__":
    update_excel_pricelist()
