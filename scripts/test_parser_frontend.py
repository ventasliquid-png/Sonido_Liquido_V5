
import io
import re
from pypdf import PdfReader
import os

PDF_PATH = r"c:\dev\Sonido_Liquido_V5\INGESTA_FACTURAS\LAVIMAR S.A. F 001_00001_00002436.pdf"

def test_pypdf():
    data = {"cliente": {}, "factura": {}, "items": []}
    
    if not os.path.exists(PDF_PATH):
        print(f"File not found: {PDF_PATH}")
        return

    print(f"Testing pypdf on {PDF_PATH}...")
    try:
        with open(PDF_PATH, "rb") as f:
            file_bytes = f.read()
            
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        if len(reader.pages) > 0:
            text = reader.pages[0].extract_text() or ""
        
        print("--- EXTRACTED TEXT START ---")
        print(text[:500])
        print("--- EXTRACTED TEXT END ---")
        
        # TEST CUIT REGEX FROM pdf_parser.py
        clean_text = text.replace("\n", " ")
        cuits = re.findall(r"\b(20|23|27|30|33|24)[-]?(\d{8})[-]?(\d{1})\b", text)
        print(f"Cuits found: {cuits}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pypdf()
