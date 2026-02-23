import io
import re
import pikepdf
import pdfplumber

def parse_afip_pdf_offline(raw_pdf_bytes: bytes) -> dict:
    """
    Operativo Sabueso Soberano (Fase 0 y Fase 1).
    Extrae la Tríada de Control (CUIT, CAE, Vto CAE) en memoria.
    No toca el File System ni invoca APIs externas.
    """
    
    # --- FASE 0: ROMPIMIENTO DE ESCLUSA (IN-MEMORY) ---
    unlocked_pdf_stream = io.BytesIO()
    
    try:
        with pikepdf.Pdf.open(io.BytesIO(raw_pdf_bytes)) as pdf:
            pdf.save(unlocked_pdf_stream)
        unlocked_pdf_stream.seek(0)
    except Exception as e:
        raise ValueError(f"Fallo en Fase 0 (Rompimiento de Esclusa): {str(e)}")

    # --- FASE 1: DOCTRINA DE EXTRACCIÓN (TRIANGULACIÓN ASIMÉTRICA) ---
    texto_total = ""
    items = []
    
    try:
        with pdfplumber.open(unlocked_pdf_stream) as pl_pdf:
            if pl_pdf.pages:
                page = pl_pdf.pages[0] # TRIPLICADO FIX: Solo procesar la primera hoja
                texto_pagina = page.extract_text()
                if texto_pagina:
                    texto_total += texto_pagina + "\n"
                    
                # 0. Extracción de Ítems vía AFIP Tables
                tables = page.extract_tables(table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"})
                # Si fallan las líneas, intentamos text mode
                if not tables:
                    tables = page.extract_tables(table_settings={"vertical_strategy": "text", "horizontal_strategy": "text"})
                    
                for table in tables:
                    if len(table) > 1:
                        header = [str(c).upper() for c in table[0] if c]
                        # Buscamos columnas clave de AFIP
                        if any("CANTIDAD" in c for c in header) or any("PRODUCTO" in c for c in header) or any("DESCRIP" in c for c in header):
                            idx_desc = next((i for i, c in enumerate(header) if "PRODUCTO" in c or "DESCRIP" in c), 0)
                            idx_cant = next((i for i, c in enumerate(header) if "CANTIDAD" in c or "CANT" in c), 1)
                            
                            for row in table[1:]:
                                if idx_desc >= len(row) or not row[idx_desc] or not str(row[idx_desc]).strip():
                                    continue
                                
                                desc = str(row[idx_desc]).replace("\n", " ").strip()
                                # Limpiar cantidad
                                cant = 1.0
                                try:
                                    if idx_cant < len(row) and row[idx_cant]:
                                        cant_str = str(row[idx_cant]).strip().replace(",", ".")
                                        cant_str = re.sub(r'[^\d.]', '', cant_str)
                                        if cant_str:
                                            cant = float(cant_str)
                                except:
                                    pass
                                
                                # Prevent duplicates from overlapping tables
                                if not any(it["descripcion"] == desc and it["cantidad"] == cant for it in items):
                                    items.append({
                                        "descripcion": desc,
                                        "cantidad": cant,
                                        "precio_unitario": 0.0,
                                        "codigo": None
                                    })
                                
    except Exception as e:
        raise ValueError(f"Fallo en lectura de texto de PDF (pdfplumber): {str(e)}")

    # --- Fallback de Ítems (Regex Líneas AFIP) ---
    if not items:
        lines = texto_total.split('\n')
        for line in lines:
            line = line.strip()
            match_item = re.search(r'^(.+?)\s+(\d+[,.]\d{2,3})\s+(unidades|u\.|u|litros|l|kg|kilos|cajas|cj|pares|mts|m)\b', line, re.IGNORECASE)
            if match_item:
                desc = match_item.group(1).strip()
                cant = float(match_item.group(2).replace(',', '.'))
                if not any(it["descripcion"] == desc and it["cantidad"] == cant for it in items):
                    items.append({
                        "descripcion": desc[:100],
                        "cantidad": cant,
                        "precio_unitario": 0.0,
                        "codigo": None
                    })

    FIREWALL_CUITS = {"30-71560397-3", "30715603973"}
    
    regex_cuit = re.compile(r'\b\d{2}[\s\-]?\d{8}[\s\-]?\d{1}\b')
    regex_cae = re.compile(r'(?i)C[\s]*A[\s]*E[\s]*(?:N°|Nro|[:.]*)?[\s]*(\d{14})')
    regex_vto = re.compile(r'(?:Vto|Vencimiento)[.\s]*(?:de\s+)?(?:CAE)?[.\s]*?[:]*[\s]*(\d{2}/\d{2}/\d{4})')
    # Regex Nro Comprobante (Detached from Punto de Venta)
    regex_nro = re.compile(r'(?:Comp\.|Comprobante|Factura)[\s]*N(?:°|ro|[.]*)?[\s]*:?[\s]*(\d{8})', re.IGNORECASE)
    
    resultado = {
        "cuit": None,
        "cae": None,
        "vto_cae": None,
        "numero": "S/N", # Nro de factura
        "items": items,
        "raw_text_length": len(texto_total)
    }

    # 1. Caza del CUIT (Receptor)
    posibles_cuits = regex_cuit.findall(texto_total)
    cuit_receptor = None
    for candidato in posibles_cuits:
        candidato_limpio = candidato.replace("-", "")
        if candidato not in FIREWALL_CUITS and candidato_limpio not in FIREWALL_CUITS:
            resultado["cuit"] = candidato
            cuit_receptor = candidato_limpio
            break

    # 1.5 Caza de Razón Social y Domicilio
    if cuit_receptor:
        lines = texto_total.split('\n')
        for i, line in enumerate(lines):
            line_clean = line.replace("-", "")
            # Buscamos la línea del receptor (contiene el CUIT y algo de Razón Social / Apellido)
            if cuit_receptor in line_clean and ("Razón" in line or "Apellido" in line or "Nombre" in line):
                # Extraer la Razón Social (lo que viene después del ":")
                partes = re.split(r':', line, 2)
                if len(partes) >= 2:
                    resultado["razon_social"] = partes[-1].strip()
                
                # El domicilio o IVA suele estar en la misma línea o en la siguiente "Condición frente al IVA: ... Domicilio Comercial: ..."
                if i + 1 < len(lines):
                    next_line = lines[i+1]
                    match_dom = re.search(r'Domicilio\s+Comercial:\s*(.+)', next_line, re.IGNORECASE)
                    if match_dom:
                        resultado["direccion"] = match_dom.group(1).strip()
                    
                    match_iva = re.search(r'Condici[oó]n\s+frente\s+al\s+IVA:\s*(.+?)(?:\s+Domicilio|$)', next_line, re.IGNORECASE)
                    if match_iva:
                        resultado["condicion_iva"] = match_iva.group(1).strip()
                break

    # 2. Caza del CAE
    match_cae = regex_cae.search(texto_total)
    if match_cae:
        resultado["cae"] = match_cae.group(1)
    else:
        fallback_cae = re.search(r'\b\d{14}\b', texto_total)
        if fallback_cae:
            resultado["cae"] = fallback_cae.group(0)

    # 3. Caza del Vto CAE
    match_vto = regex_vto.search(texto_total)
    if match_vto:
        resultado["vto_cae"] = match_vto.group(1)
        
    # 4. Caza del Nro de Comprobante (Extrayendo Punto de Venta real)
    # Busca 'Punto de Venta: 00001 Comp. Nro: 00002489' de AFIP
    regex_nro_ptovta = re.compile(r'Punto\s+de\s+Venta:\s*(\d{4,5})\s*Comp\.\s*Nro:\s*(\d{8})', re.IGNORECASE)
    match_nro_completo = regex_nro_ptovta.search(texto_total)
    
    if match_nro_completo:
        ptovta = match_nro_completo.group(1)
        nro = match_nro_completo.group(2)
        resultado["numero"] = f"{ptovta}-{nro}"
    else:
        # Fallback original
        match_nro = regex_nro.search(texto_total)
        if match_nro:
            nro_factura = match_nro.group(1)
            resultado["numero"] = f"0016-{nro_factura}"

    return resultado
