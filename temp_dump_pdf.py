import fitz
import sys

def dump_text(pdf_path):
    print(f"--- DUMPING TEXT FROM {pdf_path} ---")
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        text = page.get_text("text")
        print(f"--- PAGE {i} ---")
        print(text)
        print("-------------")
    doc.close()

if __name__ == "__main__":
    dump_text(sys.argv[1])
