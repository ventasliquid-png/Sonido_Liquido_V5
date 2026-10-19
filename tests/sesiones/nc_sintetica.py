"""Helper de test 7d: fabrica una NC/ND SINTETICA a partir del PDF real de la factura 2526 (cambia leyenda,
codigo AFIP y numero; deja igual la geometria de los renglones). NO hay NC real en el corpus."""
import sqlite3, fitz

def _reemplazar(page, buscado, nuevo, fontsize=None, indice=0):
    rects = page.search_for(buscado)
    r = rects[indice]
    page.add_redact_annot(r, fill=(1, 1, 1))
    page.apply_redactions()
    fs = fontsize or max(6.0, (r.y1 - r.y0) * 0.72)
    page.insert_text((r.x0, r.y1 - (r.y1 - r.y0) * 0.22), nuevo, fontsize=fs, fontname="helv")

def fabricar(pdf_bytes, leyenda="NOTA DE CREDITO", cod="03", numero="00000101", letra="A", cae=None):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf"); page = doc[0]
    _reemplazar(page, "FACTURA A", f"{leyenda} {letra}", fontsize=13)
    _reemplazar(page, "COD. 01", f"COD. {cod}")
    _reemplazar(page, "00002526", numero)
    if cae:
        rects = page.search_for("CAE")
    out = doc.tobytes(); doc.close()
    return out

if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5")
    from backend.remitos.pdf_parser import extract_text_from_pdf, parse_invoice_data
    con = sqlite3.connect(r"C:\dev\Sonido_Liquido_V5\pilot_v5x.db")
    pdf = con.execute("SELECT pdf_bytes FROM ingesta_facturas_raw WHERE filename LIKE '%00002526%' LIMIT 1").fetchone()[0]
    for leyenda, cod in (("NOTA DE CREDITO", "03"), ("NOTA DE DEBITO", "02")):
        t, w = extract_text_from_pdf(fabricar(pdf, leyenda, cod))
        p = parse_invoice_data(t, w)
        print(leyenda, "->", p["factura"].get("tipo_comprobante"), p["factura"].get("clase_comprobante"), p["factura"].get("numero"),
              "| items:", len(p.get("items", [])), "| cae:", p["factura"].get("cae"), "| cuit:", p["factura"].get("cuit"))
    t, w = extract_text_from_pdf(pdf); p0 = parse_invoice_data(t, w)
    print("original ->", p0["factura"].get("tipo_comprobante"), p0["factura"].get("numero"), "| items:", len(p0.get("items", [])))
