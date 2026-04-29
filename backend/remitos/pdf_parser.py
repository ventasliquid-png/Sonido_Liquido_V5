
import re
import io
import logging
import fitz  # PyMuPDF
from fastapi import UploadFile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Infiltra un PDF de ARCA/AFIP usando PyMuPDF (fitz) para extraer bloques 
    ordenados espacialmente, sorteando el desorden de AFIP.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_blocks = []
        
        # [ALFA-CA] REGLA DE PAGINA 1: Solo analizamos la primera página 
        # para evitar triplicación de items y asegurar paridad Sabueso Oro.
        if doc.page_count > 0:
            page = doc[0]
            blocks = page.get_text("blocks")
            # Ordenamos por Y (arriba a abajo) y luego X (izq a der)
            blocks.sort(key=lambda b: (b[1], b[0]))
            for b in blocks:
                # b[4] es el texto del bloque
                text_blocks.append(b[4].replace("\n", " ").strip())
        
        doc.close()
        # [SABUESO ORO] Joining with pipes for robust regex targeting
        full_text = " | ".join(text_blocks)
        try:
             with open("pdf_debug.txt", "w", encoding="utf-8") as f:
                  f.write(full_text)
        except:
             pass
        return full_text
    except Exception as e:
        logger.error(f"Error reading PDF with fitz: {e}")
        raise e

def _parse_ar_float(s: str) -> float:
    """Parse Argentine number format: '9.750,00' or '9750,00' → 9750.0"""
    s = s.strip()
    if ',' in s:
        return float(s.replace('.', '').replace(',', '.'))
    return float(s)


def parse_invoice_data(text: str) -> dict:
    """
    Parses raw text from AFIP Invoice using Sabueso Heuristics (Doctrina 2026).
    Robust patterns ported from RAR repository.
    """
    data = {"cliente": {}, "factura": {}, "items": []}
    ISSUER_CUIT = "30715603973"

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

    # 3. ITEMS (Triangulación: Cantidad + Unidad + Precio/Número posterior)
    lines = text.split('|')
    # Exigimos 'unidades' o 'un.' (con punto) para evitar falsos positivos como 'X 100 UN'
    item_pattern = re.compile(r"(\d+[\d\.,]*)\s+(unidades|un\.|u\.|litros|kg|mts|bultos|oz)\s+(\d+[\d\.,]*)", re.IGNORECASE)

    HEADER_NOISE = ["SUBTOTAL", "IMPORTES", "ALICUOTA", "IVA", "IMPORTE", "CAE", "FECHA",
                    "CUIT", "CONDICIÓN", "CÓDIGO", "PRODUCTO / SERVICIO", "U. MEDIDA",
                    "PRECIO UNIT", "TRIBUTOS", "NETO GRAVADO", "SONIDO LIQUIDO",
                    "DOMICILIO", "RAZÓN SOCIAL", "PUNTO DE VENTA", "COMP"]

    items_found = []
    prev_desc = ""

    for line in lines:
        line = line.strip()
        if not line: continue
        
        # logger.info(f"[SABUESO-ITEM-SCAN] Line: {line[:50]}...")


        # [SABUESO ORO V4] ESTRATEGIA DE ANCLAJE (Derecha a Izquierda)
        # Limpiamos la línea de caños y ruidos
        clean_line = line.replace('|', ' ').strip()
        words = clean_line.split()
        
        # Unidades de medida válidas (Anclas)
        VALID_UNITS = ["UNIDADES", "UN.", "U.", "LITROS", "KG", "MTS", "BULTOS", "OZ", "UN"]
        
        found_item = None
        for i, word in enumerate(words):
            if word.upper() in VALID_UNITS:
                # Encontramos un ancla. Los datos reales están a sus flancos.
                if i > 0 and i < len(words) - 1:
                    qty_str = words[i-1]
                    price_str = words[i+1]
                    
                    # Validamos que sean números
                    if re.match(r'^\d+[\d\.,]*$', qty_str) and re.match(r'^\d+[\d\.,]*$', price_str):
                        qty = _parse_ar_float(qty_str)
                        p_unit = _parse_ar_float(price_str)
                        
                        # Capturamos la descripción (todo lo que está a la izquierda de la cantidad)
                        desc_part = " ".join(words[:i-1]).strip()
                        
                        # [SABUESO PRIORIDAD] Seguimos buscando por si hay otro ancla más a la derecha
                        found_item = {
                            "descripcion": (prev_desc + " " + desc_part).strip() if prev_desc else desc_part,
                            "cantidad": qty,
                            "precio_unitario_neto": p_unit,
                            "alicuota_iva": 21.0, # Default, se refina abajo
                            "words_index": i
                        }
        
        if found_item:
            # Refinamos la alícuota con el resto de la línea
            remaining = " ".join(words[found_item["words_index"]+2:])
            iva_match = re.search(r'(\d+)\s*%', remaining)
            if iva_match:
                found_item["alicuota_iva"] = float(iva_match.group(1))
            
            items_found.append({
                "descripcion": found_item["descripcion"].upper(),
                "cantidad": found_item["cantidad"],
                "precio_unitario_neto": found_item["precio_unitario_neto"],
                "alicuota_iva": found_item["alicuota_iva"]
            })
            prev_desc = ""
            continue


        # 2. Si no tiene ancla, acumulamos como descripción probable
        upper = clean_line.upper()
        if len(clean_line) > 2 and not any(noise in upper for noise in HEADER_NOISE):
            if prev_desc:
                prev_desc += " " + clean_line
            else:
                prev_desc = clean_line


    data["items"] = items_found

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
             
        text = extract_text_from_pdf(content)
        
        if not text or len(text.strip()) < 10:
             return {"success": False, "error": "No se pudo extraer texto del PDF (¿Es una imagen?)."}
             
        parsed_data = parse_invoice_data(text)
        
        # [V5 EVO] Validation of results
        if not parsed_data['cliente'].get('cuit') or not parsed_data['items']:
            logger.warning("[SABUESO] Advertencia: Ingesta incompleta (sin CUIT o items).")
            
        return {"success": True, "data": parsed_data}
    except Exception as e:
        logger.error(f"--- [SABUESO CRASH] {str(e)} ---")
        return {"success": False, "error": f"Error Sabueso: {str(e)}"}
