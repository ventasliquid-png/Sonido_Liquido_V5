import os
import sys

# Add backend to path to use parser
sys.path.append(os.path.join(os.getcwd(), "backend"))
from remitos.pdf_parser import parse_afip_pdf_offline

SEARCH_DIRS = [os.getcwd(), os.path.join(os.getcwd(), "INGESTA_FACTURAS")]

def find_2492():
    for directory in SEARCH_DIRS:
        print(f"Searching in {directory}...")
        for file in os.listdir(directory):
            if file.lower().endswith(".pdf"):
                path = os.path.join(directory, file)
                try:
                    with open(path, "rb") as f:
                        content = f.read()
                        result = parse_afip_pdf_offline(content)
                        num = result.get("numero", "")
                        if "2492" in num:
                            print(f"FOUND INVOICE 2492: {path}")
                            print(f"Data: {result}")
                            return path, result
                except Exception as e:
                    pass
    print("Invoice 2492 not found.")
    return None, None

if __name__ == "__main__":
    find_2492()
