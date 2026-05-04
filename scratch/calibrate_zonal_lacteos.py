
import fitz
import os

pdf_path = r"C:\dev\V5-LS\current\DOCUMENTOS_GENERADOS_RAR\Facturas procesadas\30715603973_001_00001_00002530 Lacteos 3202_etq.pdf"

if os.path.exists(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    words = page.get_text("words")
    
    print(f"--- CALIBRACIÓN SABUESO ZONAL: {os.path.basename(pdf_path)} ---")
    found_items_header = False
    for w in words:
        x0, y0, x1, y1, text, block_no, line_no, word_no = w
        if "CANTIDAD" in text.upper():
            found_items_header = True
            
        if found_items_header:
            print(f"x0={x0:6.1f} | y0={y0:6.1f} | text='{text}'")
            if y0 > 400:
                 break
    doc.close()
else:
    print(f"Error: No se encontró el PDF")
