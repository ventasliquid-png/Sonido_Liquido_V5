
import re
import io
import logging
import fitz  # PyMuPDF
from fastapi import UploadFile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes):
    """
    Infiltra un PDF de ARCA/AFIP usando PyMuPDF (fitz) para extraer bloques 
    y palabras con coordenadas exactas.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_blocks = []
        words_data = []
        
        if doc.page_count > 0:
            page = doc[0]
            # 1. Blocks for legacy text search
            blocks = page.get_text("blocks")
            blocks.sort(key=lambda b: (b[1], b[0]))
            for b in blocks:
                text_blocks.append(b[4].replace("\n", " ").strip())
            
            # 2. Words for Zonal parsing
            words_data = page.get_text("words")
        
        doc.close()
        full_text = " | ".join(text_blocks)
        
        # Debug trace
        try:
             with open("pdf_debug.txt", "w", encoding="utf-8") as f:
                  f.write(full_text)
        except:
             pass
             
        return full_text, words_data
    except Exception as e:
        logger.error(f"Error reading PDF with fitz: {e}")
        raise e

def _parse_ar_float(s: str) -> float:
    """Parse Argentine number format: '9.750,00' or '9750,00' → 9750.0"""
    s = s.strip()
    if ',' in s:
        return float(s.replace('.', '').replace(',', '.'))
    return float(s)


def parse_invoice_data(text: str, words_data: list = None) -> dict:
    """
    Parses raw text and word data using Sabueso Zonal Heuristics (V5.5).
    """
    data = {"cliente": {}, "factura": {}, "items": []}
    ISSUER_CUIT = "30715603973"

    # [ZONAS AFIP CALIBRADAS 2026]
    ZONAS = {
        "descripcion": (0, 235),
        "cantidad":    (235, 280),
        "u_medida":    (280, 330),
        "precio_unit": (330, 385), # Narrower to avoid Bonif (390+)
        "subtotal":    (410, 485),
        "alicuota":    (485, 525),
        "total_item":  (525, 600)
    }

    # 1. FACTURA & CAE (Protocolo Sabueso Oro - RAR Port)
    # Pto Vta and Comp Nro
    # Allow pipes | in between because PyMuPDF joins separate blocks with ' | '
    
    # [GY-FIX] Patrón AFIP Reciente: "Punto de Venta: Comp. Nro: 00001 00002493"
    match_comp = re.search(r'Punto.*?Comp.*?Nro[.\s:|]*\s*(\d{4,5})\s+(\d{8})', text, re.IGNORECASE)
    
    if not match_comp:
        match_comp = re.search(r'Punto\s*de\s*Ventas?[^\d]*(\d{4,5}).*?Comp.*?(?:Nro)?[^\d]*(\d{8})', text, re.IGNORECASE)
    if not match_comp:
        match_comp = re.search(r'(?:Punto|Pto)?\s*(?:de\s*)?VTA[.\s]*:?\s*(\d{4,5}).*?Comp.*?Nro[.\s]*:?\s*(\d{8})', text, re.IGNORECASE)
    if not match_comp:
        match_comp = re.search(r'(\d{4,5})\s*(?:\|\s*)?-\s*(?:\|\s*)?(\d{8})', text)
    if not match_comp:
        # Sometimes it appears as just "Comp. Nro: | 0001 | 12345678" without dash
        match_comp = re.search(r'Comp.*?(?:Nro)?[.\s:|]*(\d{4,5})\s*\|\s*(?:-\s*\|\s*)?(\d{8})', text, re.IGNORECASE)
    
    if match_comp:
         data["factura"]["numero"] = f"{match_comp.group(1).zfill(5)}-{match_comp.group(2).zfill(8)}"
    
    # [SABUESO ORO] CAE Detection
    match_cae = re.search(r'C\.?A\.?E\.?.*?(?:\:)?.*?(\d{14})', text, re.IGNORECASE)
    if match_cae:
        data["factura"]["cae"] = match_cae.group(1)

    # Vencimiento
    match_vto = re.search(r'(?:Vto|Vencimiento).*?(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if match_vto:
        data["factura"]["vto_cae"] = match_vto.group(1)

    # 2. CLIENTE (CUIT Detection - Prioritized Strategy)
    cuit_final = None
    
    # Priority 1: Find CUIT following a "CUIT:" label that is NOT the issuer's
    labels_cuit = re.finditer(r"(?:CUIT|CUIL)[:\s|]*((?:20|23|24|27|30|33|34)\-?\d{8}\-?\d{1})", text, re.IGNORECASE)
    for match in labels_cuit:
        c = match.group(1).replace("-", "").strip()
        if c != ISSUER_CUIT:
            cuit_final = c
            break
    
    # Priority 2: Fallback to any CUIT-like pattern found in text
    if not cuit_final:
        patrones_cuit = re.findall(r'\b((?:20|23|24|27|30|33|34)\-?\d{8}\-?\d{1})\b', text)
        cuits_limpios = [c.replace("-", "") for c in patrones_cuit]
        cuits_filtrados = [c for c in cuits_limpios if c != ISSUER_CUIT]
        if cuits_filtrados:
            cuit_final = cuits_filtrados[0]

    if cuit_final:
        data["cliente"]["cuit"] = cuit_final

    # Name and Address Detection (Context-aware)
    blocks = [b.strip() for b in text.split('|')]
    cuit_pattern = cuit_final if cuit_final else "NO_CUIT_FOUND"
    
    # [V5 BRAIN] Strategy: Inverted AFIP detection.
    razon_social = None
    
    # Strategy B: Block-based (Near CUIT) - HIGH PRIORITY FOR INVERTED
    if cuit_final:
        for idx, block in enumerate(blocks):
            if cuit_pattern in block.replace("-", ""):
                clean_candidate = block.replace("-", "").replace(cuit_pattern, "").strip()
                if len(clean_candidate) > 3:
                    razon_social = clean_candidate
                    break
    
    # Strategy A: Label-based (Fallback)
    if not razon_social:
        name_match = re.search(r"(?:Apellido y Nombre|Razón Social)\s*[:\|]?\s*([^|]{3,})(?=\s*\||$)", text, re.IGNORECASE)
        if name_match:
            candidate = name_match.group(1).strip()
            if not any(x in candidate.upper() for x in ["CUIT", ISSUER_CUIT, "IVA"]):
                razon_social = candidate

    if razon_social:
        razon_social = re.sub(r'(?:Apellido y Nombre|Razón Social)[:\s]*', '', razon_social, flags=re.I).strip()
        razon_social = razon_social.replace('|', '').strip()
        data["cliente"]["razon_social"] = razon_social.upper()

    # [LOG TRACE] Guardar lo que se leyó para diagnóstico
    try:
        with open("sabueso_trace.log", "a", encoding="utf-8") as log_f:
            import datetime
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_f.write(f"[{now}] CUIT: {cuit_final} | Cliente: {razon_social} | Factura: {data['factura'].get('numero')}\n")
    except:
        pass

    # [NUEVO] Condición IVA
    iva_match = re.search(r"(?:Condición frente al IVA|IVA)[:\|]?\s*([^|]{5,30})(?=\s*\||$)", text, re.IGNORECASE)
    if iva_match:
        iva_val = iva_match.group(1).strip().upper()
        # Normalización básica para el mapping posterior
        if "INSCRIPTO" in iva_val: data["cliente"]["condicion_iva"] = "Responsable Inscripto"
        elif "MONOTRIBUTO" in iva_val or "MONOTRIBUTISTA" in iva_val: data["cliente"]["condicion_iva"] = "Monotributista"
        elif "EXENTO" in iva_val: data["cliente"]["condicion_iva"] = "Exento"
        elif "CONSUMIDOR FINAL" in iva_val: data["cliente"]["condicion_iva"] = "Consumidor Final"
        else: data["cliente"]["condicion_iva"] = iva_val

    # Domicilio (Busqueda en bloques ruidosos)
    # Strategy: Find "Domicilio" block, and take the next significant blocks that look like an address
    domicilio_parts = []
    found_label = False
    for idx, block in enumerate(blocks):
        upper_block = block.upper()
        if "DOMICILIO" in upper_block or "DIRECCIÓN" in upper_block:
            found_label = True
            # Check if value is in same block
            val = re.sub(r'(?:Domicilio|Dirección)[^:]*[:\s|]*', '', block, flags=re.I).strip()
            if len(val) > 5 and not any(x in val.upper() for x in ["COMERCIAL", "FISCAL"]):
                domicilio_parts.append(val)
            continue
        
        if found_label:
            # If we already found the label, the next 1-2 blocks are usually the address
            if len(domicilio_parts) < 3: # Max 3 blocks for address
                if len(block) > 2 and not any(x in block.upper() for x in ["CONDICIÓN", "CUIT", "SONIDO LIQUIDO", "IVA", "EMISIÓN"]):
                    domicilio_parts.append(block)
                else:
                    if domicilio_parts: break # End of address
            else:
                break

    # Filter out issuer address if it leaked
    final_domicilio = " ".join(domicilio_parts).strip()
    if "ROSETI" in final_domicilio.upper():
        final_domicilio = "S/D"

    data["cliente"]["domicilio"] = f"[EXTRACTED] {final_domicilio}" if final_domicilio else "S/D"

    # [V5] Detección de Totales (Pie de Factura)
    match_neto = re.search(r'Importe Neto Gravado:\s*\$?\s*([\d\.,]+)', text, re.IGNORECASE)
    if match_neto:
        data["factura"]["total_neto"] = _parse_ar_float(match_neto.group(1))
    
    match_total = re.search(r'Importe Total:\s*\$?\s*([\d\.,]+)', text, re.IGNORECASE)
    if match_total:
        data["factura"]["total_final"] = _parse_ar_float(match_total.group(1))

    # --- [SABUESO V5.5 ZONAL ITEMS] ---
    if words_data:
        # 1. Agrupamos palabras por línea (Y0) con tolerancia de 4 pts
        lines = {}
        for w in words_data:
            x0, y0, x1, y1, val, *_ = w
            y_key = round(y0 / 4) * 4
            if y_key not in lines: lines[y_key] = []
            lines[y_key].append({"x0": x0, "text": val})
        
        sorted_y = sorted(lines.keys())
        items_v55 = []
        current_item = None
        desc_buffer = "" # [V5.5] Buffer para descripciones pre-data
        table_started = False
        VALID_UNITS = ["UNIDADES", "UN.", "U.", "LITROS", "KG", "MTS", "BULTOS", "OZ", "UN"]

        for y in sorted_y:
            row_words = sorted(lines[y], key=lambda w: w["x0"])
            row_text = " ".join(w["text"] for w in row_words).upper()
            
            # [V5.5] Gate de Salida: Si detectamos el pie de página, cortamos.
            if table_started and any(term in row_text for term in ["NETO GRAVADO", "TOTAL VTA", "SUBTOTAL", "SON PESOS"]):
                table_started = False
                current_item = None
                desc_buffer = ""
                continue

            if not table_started:
                if "PRODUCTO / SERVICIO" in row_text or "CÓDIGO" in row_text:
                    table_started = True
                continue

            # Clasificar por zonas
            row_data = {"descripcion": "", "cantidad": None, "u_medida": None, "precio": None, "iva": 21.0}
            has_data_anchor = False

            for w in row_words:
                x = w["x0"]
                txt = w["text"]
                
                if x < ZONAS["descripcion"][1]:
                    row_data["descripcion"] += " " + txt
                elif ZONAS["cantidad"][0] <= x < ZONAS["cantidad"][1]:
                    if re.match(r'^\d+[\d\.,]*$', txt) and row_data["cantidad"] is None:
                         row_data["cantidad"] = _parse_ar_float(txt)
                elif ZONAS["u_medida"][0] <= x < ZONAS["u_medida"][1]:
                    if txt.upper() in VALID_UNITS: 
                        row_data["u_medida"] = txt
                        has_data_anchor = True
                elif ZONAS["precio_unit"][0] <= x < ZONAS["precio_unit"][1]:
                    if re.match(r'^\d+[\d\.,]*$', txt) and row_data["precio"] is None:
                         row_data["precio"] = _parse_ar_float(txt)
                elif ZONAS["alicuota"][0] <= x < ZONAS["alicuota"][1]:
                    if "%" in txt:
                        try: row_data["iva"] = float(txt.replace("%", "").replace(",", "."))
                        except: pass

            row_data["descripcion"] = row_data["descripcion"].strip()

            # Lógica de ensamblaje de ítem (Buffer-Aware)
            if has_data_anchor and row_data["cantidad"] is not None:
                # Línea primaria: consumimos buffer acumulado
                full_desc = (desc_buffer + " " + row_data["descripcion"]).strip()
                current_item = {
                    "descripcion": full_desc,
                    "cantidad": row_data["cantidad"],
                    "precio_unitario_neto": row_data["precio"] or 0.0,
                    "alicuota_iva": row_data["iva"],
                    "subtotal": round(row_data["cantidad"] * (row_data["precio"] or 0.0), 2)
                }
                items_v55.append(current_item)
                desc_buffer = "" # Limpiamos buffer
            elif row_data["descripcion"] and not any(n in row_data["descripcion"].upper() for n in ["SUBTOTAL", "TOTAL", "CAE", "NETO", "FACTURA", "PAG.", "IMPORTE"]):
                # Línea de extensión
                if current_item:
                    # Pertenece al ítem actual (Post-Data Extension)
                    current_item["descripcion"] += " " + row_data["descripcion"]
                else:
                    # No hay ítem activo, se acumula para el próximo (Pre-Data Buffer)
                    desc_buffer += " " + row_data["descripcion"]

        # Limpieza final de ruidos
        HEADER_NOISE = ["SUBTOTAL", "IMPORTES", "ALICUOTA", "IVA", "IMPORTE", "CAE", "FECHA", "CUIT", "CONDICIÓN", "U. MEDIDA", "PRODUCTO / SERVICIO"]
        for it in items_v55:
            for noise in HEADER_NOISE:
                it["descripcion"] = re.sub(rf'\b{noise}\b', '', it["descripcion"], flags=re.I).strip()
            it["descripcion"] = re.sub(r'\s+', ' ', it["descripcion"]).strip()

        data["items"] = items_v55

    # [V5.5] Macro-Validación: Consulta Flag
    if data["factura"].get("total_neto") and data["items"]:
        suma_items = sum(it["subtotal"] for it in data["items"])
        if abs(suma_items - data["factura"]["total_neto"]) < 0.5:
            data["factura"]["audit_status"] = "VERIFICADO_OK"
        else:
            data["factura"]["audit_status"] = "CONSULTA_FLAG"
            data["factura"]["audit_warning"] = f"La suma de ítems (${suma_items}) no coincide con el Neto de la factura (${data['factura']['total_neto']})"

    # [NUEVO] OC Detection
    oc_match = re.search(r'OC:\s*(OC\s+[\w\d]+)', text, re.IGNORECASE)
    if oc_match:
        data["factura"]["oc"] = oc_match.group(1).strip()

    # [NUEVO] Detección de Canal (Marketing DNA)
    if "MERCADO LIBRE" in text.upper() or "MELI" in text.upper():
        data["cliente"]["canal"] = "MLIBRE"
    elif "TIENDA NUBE" in text.upper() or "TIENDANUBE" in text.upper():
        data["cliente"]["canal"] = "TIENDANUBE"
        
    return data


async def process_pdf_ingestion(file: UploadFile):
    try:
        content = await file.read()
        logger.info(f"--- [SABUESO INGESTA] Recibido: {file.filename} ({len(content)} bytes) ---")
        
        # Guardar copia física en DOCUMENTOS_GENERADOS_RAR/Facturas procesadas
        import os
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            target_dir = os.path.join(base_dir, "DOCUMENTOS_GENERADOS_RAR", "Facturas procesadas")
            os.makedirs(target_dir, exist_ok=True)
            safe_filename = "".join([c for c in file.filename if c.isalpha() or c.isdigit() or c in " .-_"]).rstrip()
            if not safe_filename.lower().endswith('.pdf'):
                safe_filename += '.pdf'
            file_path = os.path.join(target_dir, safe_filename)
            with open(file_path, "wb") as f_out:
                f_out.write(content)
            logger.info(f"[SABUESO INGESTA] Copia guardada en: {file_path}")
        except Exception as file_e:
            logger.error(f"Error guardando copia de factura: {str(file_e)}")
        
        if not content:
             return {"success": False, "error": "El archivo está vacío."}
             
        text, words_data = extract_text_from_pdf(content)
        
        if not text or len(text.strip()) < 10:
             return {"success": False, "error": "No se pudo extraer texto del PDF (¿Es una imagen?)."}
             
        parsed_data = parse_invoice_data(text, words_data)
        
        # [V5 EVO] Validation of results
        if not parsed_data['cliente'].get('cuit') or not parsed_data['items']:
            logger.warning("[SABUESO] Advertencia: Ingesta incompleta (sin CUIT o items).")
            
        return {"success": True, "data": parsed_data}
    except Exception as e:
        logger.error(f"--- [SABUESO CRASH] {str(e)} ---")
        return {"success": False, "error": f"Error Sabueso: {str(e)}"}
