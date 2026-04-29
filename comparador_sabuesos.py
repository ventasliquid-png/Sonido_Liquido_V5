
import os
import sys
import json
import pdfplumber
import re

# Importar el Sabueso Actual (Heurístico)
sys.path.append(os.path.join(os.getcwd(), 'backend'))
try:
    from remitos.pdf_parser import parse_invoice_data, extract_text_from_pdf
except ImportError:
    # Fallback si el path no engancha
    sys.path.append(os.path.join(os.getcwd()))
    from backend.remitos.pdf_parser import parse_invoice_data, extract_text_from_pdf

def test_pdfplumber_strategy(file_path):
    """
    Estrategia nueva usando tablas estructurales de pdfplumber.
    """
    results = {
        "cliente": "No detectado",
        "cuit": "No detectado",
        "items": []
    }
    
    try:
        with pdfplumber.open(file_path) as pdf:
            first_page = pdf.pages[0]
            
            # 1. Intentar extraer el CUIT y Cliente (Metadatos/Texto)
            text = first_page.extract_text()
            # CUIT receptor en facturas Sonido Liquido suele estar despues del primer CUIT (emisor)
            cuits = re.findall(r"(\d{2}-?\d{8}-?\d{1})", text)
            if len(cuits) > 1:
                results["cuit"] = cuits[1].replace("-", "")
            elif len(cuits) == 1:
                results["cuit"] = cuits[0].replace("-", "")
            
            # 2. Extraer Tablas (Corazón de pdfplumber)
            tables = first_page.extract_tables()
            for table in tables:
                for row in table:
                    # Filtro: Buscamos filas que tengan contenido
                    clean_row = [str(cell).strip().replace('\n', ' ') for cell in row if cell]
                    if not clean_row: continue
                    
                    row_str = " ".join(clean_row).lower()
                    # Heurística: si tiene unidades o algo que parezca cantidad + precio
                    if ("unidades" in row_str or "un " in row_str) and len(clean_row) >= 4:
                        results["items"].append(clean_row)
            
            return results
    except Exception as e:
        return {"error": str(e)}

def run_comparison(invoice_name):
    base_path = r"c:\dev\Sonido_Liquido_V5\INGESTA_FACTURAS"
    file_path = os.path.join(base_path, invoice_name)
    
    if not os.path.exists(file_path):
        print(f"ERROR: No se encuentra el archivo en {file_path}")
        return

    print(f"\n=== COMPARACIÓN PARA: {invoice_name} ===")
    
    # --- MÉTODO A: SABUESO ACTUAL ---
    print("\n--- [A] SABUESO ACTUAL (Heurístico/Regex) ---")
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        text_raw = extract_text_from_pdf(content)
        actual_data = parse_invoice_data(text_raw)
        
        print(f"Cliente: {actual_data['cliente'].get('razon_social', '???')}")
        print(f"CUIT: {actual_data['cliente'].get('cuit', '???')}")
        print(f"Items encontrados: {len(actual_data['items'])}")
        for i in actual_data['items']:
            print(f"  - DEBUG RAW: {i}")
            print(f"  - {i['cantidad']} x {i['descripcion'][:40]}... @ ${i.get('precio_unitario_neto', 'MISSING')}")
    except Exception as e:
        print(f"Error Sabueso A: {e}")

    # --- MÉTODO B: PDFPLUMBER ---
    print("\n--- [B] ARQUITECTO PDFPLUMBER (Tablas Estructurales) ---")
    plumber_data = test_pdfplumber_strategy(file_path)
    
    if "error" in plumber_data:
        print(f"ERROR: {plumber_data['error']}")
    else:
        print(f"CUIT Detectado: {plumber_data['cuit']}")
        print(f"Filas de tabla (brutas) detectadas: {len(plumber_data['items'])}")
        for idx, i in enumerate(plumber_data['items']):
            print(f"  [{idx+1}] {i}")

if __name__ == "__main__":
    # Probamos con Gelato y Lácteos
    targets = [
        "30715603973_001_00001_00002368 Gelato.pdf",
        "30715603973_001_00001_00002369 Lácteos.pdf"
    ]
    for t in targets:
        run_comparison(t)
