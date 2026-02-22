import fitz
import sys
import json
import re

def extraer_datos_v2(pdf_path, cuit_emisor=None):
    doc = fitz.open(pdf_path)
    text_blocks = []
    for page in doc:
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[1], b[0]))
        for b in blocks:
            text_blocks.append(b[4].replace("\n", " ").strip())
    
    doc.close()
    texto_completo = " | ".join(text_blocks)
    
    datos_extraidos = {
        "cuit_receptor": None,
        "comprobante": None,
        "cae": None,
        "vto_cae": None,
        "error": None
    }

    try:
        # 1. CUIT RECEPTOR
        patrones_cuit = re.findall(r'\b((?:20|23|24|27|30|33|34)\-?\d{8}\-?\d{1})\b', texto_completo)
        cuits_limpios = [c.replace("-", "") for c in patrones_cuit]
        
        if cuit_emisor:
            cuits_filtrados = [c for c in cuits_limpios if c != cuit_emisor]
            if cuits_filtrados:
                datos_extraidos["cuit_receptor"] = cuits_filtrados[0]
        else:
            if len(cuits_limpios) >= 2:
                datos_extraidos["cuit_receptor"] = cuits_limpios[1] # Suponiendo que el 1ro es emisor
            elif len(cuits_limpios) == 1:
                datos_extraidos["cuit_receptor"] = cuits_limpios[0]

        # 2. COMPROBANTE - Busqueda flexible para Ptos de Venta separados del Comprobante
        match_comp = re.search(r'Punto\s*de\s*Ventas?[^\d]*(\d{4,5}).*?Comp.*?(?:Nro)?[^\d]*(\d{8})', texto_completo, re.IGNORECASE)
        if not match_comp:
            # Alternativa: "00003-00000123" crudo
            match_comp = re.search(r'(\d{4,5})\s*-\s*(\d{8})', texto_completo)

        if match_comp:
            datos_extraidos["comprobante"] = f"{match_comp.group(1).zfill(5)}-{match_comp.group(2).zfill(8)}"

        # 3. CAE
        match_cae = re.search(r'C\.?A\.?E\.?.*?(?:\:)?.*?(\d{14})', texto_completo, re.IGNORECASE)
        if match_cae:
            datos_extraidos["cae"] = match_cae.group(1)

        # 4. VENCIMIENTO CAE
        match_vto = re.search(r'(?:Vto|Vencimiento).*?(\d{2}/\d{2}/\d{4})', texto_completo, re.IGNORECASE)
        if match_vto:
            datos_extraidos["vto_cae"] = match_vto.group(1)

    except Exception as e:
        datos_extraidos["error"] = str(e)

    print(json.dumps(datos_extraidos, indent=4))

if __name__ == "__main__":
    cuit_nuestro = "30715603973" 
    extraer_datos_v2(sys.argv[1], cuit_nuestro)
