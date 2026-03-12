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

    print("Iniciando Cosechadora de Datos (Modo: Sin Precios - Hasta Columna H)...")
    xls = pd.ExcelFile(INPUT_FILE)
    
    clientes_found = [] # Lista de dicts {Nombre, Cuit, Origen}
    productos_found = [] # Lista de dicts {Nombre, Frecuencia, Origen}

    for sheet in xls.sheet_names:
        print(f"Procesando hoja: {sheet}")
        try:
            # Leemos SOLO hasta columna H (Excel A:H = pandas usecols="A:H")
            # Pero pandas usecols toma letras o indices. H es la 8va (index 7).
            # Simplificación: leemos todo y trunamos en memoria para evitar lios de parseo
            df = pd.read_excel(xls, sheet_name=sheet, header=None, dtype=str)
            
            # Cortar en columna H (8 columnas max)
            df = df.iloc[:, :8]
            
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
                                    
                        if cliente_candidato and len(cliente_candidato) > 2:
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
                        
                        # Identificar columnas
                        for r_scan in range(r, min(r+5, rows)):
                             for c_scan in range(c, min(c+6, cols)): # Scan reducido
                                 val_scan = normalize_text(df.iat[r_scan, c_scan]).lower()
                                 if "producto" in val_scan or "descripci" in val_scan:
                                     start_row_items = r_scan + 1
                                     item_col_idx = c_scan
                        
                        # Extraer items hasta encontrar fila vacia o nuevo pedido
                        # OJO: Los pedidos Viejos suelen tener items en la misma columna hacia abajo
                        if item_col_idx != -1:
                            for r_item in range(start_row_items, rows):
                                if r_item >= rows: break
                                
                                prod_name = normalize_text(df.iat[r_item, item_col_idx])
                                
                                # Condicion de parres: Vacío o Nuevo Header o "Total"
                                if not prod_name or is_pedido_header(prod_name) or "total" in prod_name.lower() or "son pesos" in prod_name.lower():
                                    break
                                
                                # Filtrar basura (headers repetidos, lineas vacias)
                                if len(prod_name) > 3 and "producto" not in prod_name.lower():
                                    productos_found.append({
                                        "nombre": prod_name,
                                        "hoja": sheet
                                    })

        except Exception as e:
            print(f"Error en hoja {sheet}: {e} (Continuando...)")

    # Guardar en CSV
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    # --- PROCESAR CLIENTES ---
    if clientes_found:
        df_cli = pd.DataFrame(clientes_found)
        # Limpieza basica
        df_cli['nombre'] = df_cli['nombre'].str.upper().str.strip()
        
        df_cli_grouped = df_cli.groupby('nombre').agg({
            'cuit': lambda x: next((i for i in x if i), None), # Tomar primer CUIT no vacio
            'hoja': 'count' # Contar frecuencia
        }).rename(columns={'hoja': 'frecuencia'}).reset_index()
        
        # Ordenar por importancia (frecuencia)
        df_cli_grouped = df_cli_grouped.sort_values(by='frecuencia', ascending=False)
        
        path_cli = os.path.join(OUTPUT_DIR, "clientes_candidatos.csv")
        df_cli_grouped.to_csv(path_cli, index=False, encoding='utf-8-sig') # utf-8-sig para que Excel abra bien las tildes
        print(f"✅ Clientes exportados: {path_cli} ({len(df_cli_grouped)} registros)")
    else:
        print("⚠️ No se encontraron clientes.")

    # --- PROCESAR PRODUCTOS ---
    if productos_found:
        df_prod = pd.DataFrame(productos_found)
        df_prod['nombre'] = df_prod['nombre'].str.strip() # Respetar Case? Mejor Upper para agrupar
        df_prod['nombre_upper'] = df_prod['nombre'].str.upper()
        
        df_prod_grouped = df_prod.groupby('nombre_upper').agg({
            'nombre': 'first', # Mantener una grafía original
            'hoja': 'count'
        }).rename(columns={'hoja': 'frecuencia'}).reset_index()
        
        df_prod_grouped = df_prod_grouped.sort_values(by='frecuencia', ascending=False)
        
        path_prod = os.path.join(OUTPUT_DIR, "productos_candidatos.csv")
        # Solo guardar columnas relevantes
        df_prod_grouped[['nombre', 'frecuencia']].to_csv(path_prod, index=False, encoding='utf-8-sig')
        print(f"✅ Productos exportados: {path_prod} ({len(df_prod_grouped)} registros)")
    else:
        print("⚠️ No se encontraron productos.")
    
    print("Cosecha finalizada.")

if __name__ == "__main__":
    harvest_data()
