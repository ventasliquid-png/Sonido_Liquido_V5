
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from remitos.pdf_parser import extract_text_from_pdf, parse_invoice_data

pdf_path = r"c:\dev\Sonido_Liquido_V5\INGESTA_FACTURAS\30715603973_001_00001_00002368 Gelato.pdf"

with open(pdf_path, "rb") as f:
    content = f.read()

text = extract_text_from_pdf(content)
print("--- RAW TEXT (PIPES) ---")
print(text)
print("\n--- PARSED DATA ---")
import json
data = parse_invoice_data(text)
print(json.dumps(data, indent=2))
