import pandas as pd
import os
import re

INPUT_FILE = r"c:\dev\Sonido_Liquido_V5\pedidos_raw.xlsx"
OUTPUT_DIR = r"c:\dev\Sonido_Liquido_V5\BUILD_PILOTO\data"

def normalize_text(text):
    if pd.isna(text): return ""
    return str(text).strip()

def is_pedido_header(cell_value):
    s = normalize_text(cell_value).lower()
    return "pedido n" in s or "pedido  n" in s

def harvest_data():
    if not os.path.exists(INPUT_FILE):
        print("No se encontró el archivo de entrada.")
        return

    print("Iniciando Cosechadora de Datos...")
    xls = pd.ExcelFile(INPUT_FILE)
    
    clientes_found = [] # Lista de dicts {Nombre, Cuit, Origen}
    productos_found = [] # Lista de dicts {Nombre, PrecioRef, Origen}

    for sheet in xls.sheet_names:
        print(f"Procesando hoja: {sheet}")
        try:
            # Leemos todo como string para facilitar busqueda
            df = pd.read_excel(xls, sheet_name=sheet, header=None, dtype=str)
            
            # Barrido de celdas
            rows, cols = df.shape
            
            for r in range(rows):
                for c in range(cols):
                    val = df.iat[r, c]
                    if is_pedido_header(val):
                        # Encontramos un bloque de pedido!
                        # Intentamos extraer Cliente (suele estar en r, c+2 o c+3)
                        cliente_candidato = ""
                        cuit_candidato = ""
                        
                        # Estrategia heurística de busqueda de Cliente
                        # Miramos a la derecha en la misma fila
                        if c+2 < cols: cliente_candidato = normalize_text(df.iat[r, c+2])
                        
                        # Busqueda de CUIT (Suele estar fila siguiente)
                        if r+1 < rows:
                            # Buscamos en toda la fila de abajo algo que parezca cuit
                            for c_search in range(c, min(c+5, cols)):
                                val_down = normalize_text(df.iat[r+1, c_search])
                                if "cuit" in val_down.lower():
                                    # El valor suele estar en la celda siguiente a la palabra CUIT
                                    if c_search+1 < cols:
                                        cuit_candidato = normalize_text(df.iat[r+1, c_search+1])
                                    break
                                    
                        if cliente_candidato:
                            clientes_found.append({
                                "nombre": cliente_candidato,
                                "cuit": cuit_candidato,
                                "hoja": sheet
                            })

                        # Ahora intentamos extraer PRODUCTOS
                        # Bajamos hasta encontrar "descripcion" o "producto"
                        start_row_items = r + 2
                        # Buscamos header de items
                        item_col_idx = c # Asumimos que la lista arranca alineada al pedido
                        price_col_idx = -1
                        
                        # Identificar columnas
                        for r_scan in range(r, min(r+5, rows)):
                             for c_scan in range(c, min(c+10, cols)):
                                 val_scan = normalize_text(df.iat[r_scan, c_scan]).lower()
                                 if "producto" in val_scan or "descripci" in val_scan:
                                     start_row_items = r_scan + 1
                                     item_col_idx = c_scan
                                 if "precio de venta" in val_scan or "costo unitario" in val_scan:
                                     # Priorizamos precio venta si existe
                                     price_col_idx = c_scan
                        
                        # Extraer items hasta encontrar fila vacia o nuevo pedido
                        if item_col_idx != -1:
                            for r_item in range(start_row_items, rows):
                                prod_name = normalize_text(df.iat[r_item, item_col_idx])
                                
                                # Condicion de parres: Vacío o Nuevo Header
                                if not prod_name or is_pedido_header(prod_name) or "total" in prod_name.lower():
                                    break
                                    
                                precio = "0"
                                if price_col_idx != -1:
                                    precio = normalize_text(df.iat[r_item, price_col_idx])
                                
                                # Filtrar basura
                                if len(prod_name) > 3:
                                    productos_found.append({
                                        "nombre": prod_name,
                                        "precio": precio,
                                        "hoja": sheet
                                    })

        except Exception as e:
            print(f"Error en hoja {sheet}: {e}")

    # Guardar en CSV
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    df_cli = pd.DataFrame(clientes_found)
    # Agrupar por nombre para limpiar duplicados brutos
    df_cli_grouped = df_cli.groupby('nombre').agg({
        'cuit': 'first', # Tomar el primer cuit que encuentre
        'hoja': 'count' # Contar frecuencia
    }).rename(columns={'hoja': 'frecuencia'}).reset_index()
    
    df_cli_grouped.to_csv(os.path.join(OUTPUT_DIR, "clientes_raw.csv"), index=False)
    
    df_prod = pd.DataFrame(productos_found)
    df_prod_grouped = df_prod.groupby('nombre').agg({
        'precio': 'last', # Tomar ultimo precio
        'hoja': 'count'
    }).rename(columns={'hoja': 'frecuencia'}).reset_index()
    
    df_prod_grouped.to_csv(os.path.join(OUTPUT_DIR, "productos_raw.csv"), index=False)
    
    print(f"Cosecha finalizada. Encontrados {len(df_cli_grouped)} clientes y {len(df_prod_grouped)} productos únicos.")

if __name__ == "__main__":
    harvest_data()
