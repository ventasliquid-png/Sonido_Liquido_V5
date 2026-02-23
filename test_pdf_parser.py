import sys
import os
import asyncio

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.remitos.pdf_parser import extract_text_from_pdf, parse_invoice_data

def test_parser(pdf_path):
    print(f"--- Probando Parser Sabueso V2 con: {pdf_path} ---")
    
    if not os.path.exists(pdf_path):
        print(f"Error: Archivo no encontrado en {pdf_path}")
        return

    try:
        with open(pdf_path, 'rb') as f:
            file_bytes = f.read()
            
        print("1. Extrayendo texto (pdfplumber)...")
        text = extract_text_from_pdf(file_bytes)
        print(f"Texto extraído: {len(text)} caracteres")
        
        print("2. Parseando datos de factura...")
        data = parse_invoice_data(text)
        
        print("\n--- RESULTADO DE PARSEO ---")
        import json
        with open("parsed.json", "w", encoding="utf-8") as out:
            json.dump(data, out, indent=4, ensure_ascii=False)
            
        with open("raw_text.txt", "w", encoding="utf-8") as out_txt:
            out_txt.write(text)
        print("Guardado en parsed.json y raw_text.txt")
        
    except Exception as e:
        print(f"Excepción general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    pdf_file = "30715603973_001_00001_00002489 Lavimar.pdf" 
    full_path = os.path.join(os.getcwd(), pdf_file)
    test_parser(full_path)
