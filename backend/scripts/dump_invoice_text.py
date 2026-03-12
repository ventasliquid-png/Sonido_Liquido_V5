import sys
import os
from pypdf import PdfReader

# Adjust path to find the file in root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
PDF_PATH = os.path.join(PROJECT_ROOT, "30715603973_001_00001_00002489 Lavimar.pdf")

def dump_text():
    if not os.path.exists(PDF_PATH):
        print(f"Error: File not found at {PDF_PATH}")
        return

    print(f"--- DUMPING TEXT FROM: {PDF_PATH} ---")
    try:
        reader = PdfReader(PDF_PATH)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"
        
        print(full_text)
    except Exception as e:
        print(f"Error reading PDF: {e}")

if __name__ == "__main__":
    dump_text()
