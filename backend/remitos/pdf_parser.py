
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

    # 2. CLIENTE (CUIT Detection)
    # Extended patterns to catch varied CUIT prefixes
    patrones_cuit = re.findall(r'\b((?:20|23|24|27|30|33|34)\-?\d{8}\-?\d{1})\b', text)
    cuits_limpios = [c.replace("-", "") for c in patrones_cuit]
    
    # Filtramos nuestro propio CUIT el que sobra es el del cliente
    cuits_filtrados = [c for c in cuits_limpios if c != ISSUER_CUIT]
    cuit_final = None
    if cuits_filtrados:
        cuit_final = cuits_filtrados[0]
    else:
        # Fallback por si no pasamos el CUIT emisor
        if len(cuits_limpios) >= 2:
            cuit_final = cuits_limpios[1]
        elif len(cuits_limpios) == 1:
            cuit_final = cuits_limpios[0]

    if cuit_final:
        # Standardize: Always digits-only for internal logic/DB, format for UI is separate
        clean_cuit = cuit_final.replace("-", "").strip()
        data["cliente"]["cuit"] = clean_cuit

    # Name and Address Detection (Context-aware)
    blocks = [b.strip() for b in text.split('|')]
    cuit_pattern = cuit_final if cuit_final else "NO_CUIT_FOUND"
    
    # [V5 BRAIN] Strategy: Inverted AFIP detection.
    # If we find "Razón Social" but the block before it contains the CUIT + Name, use that.
    razon_social = None
    
    # Strategy B: Block-based (Near CUIT) - HIGH PRIORITY FOR INVERTED
    if cuit_final:
        for idx, block in enumerate(blocks):
            if cuit_pattern in block.replace("-", ""):
                # Is the name in this same block? (e.g. "30611306632 BIOTENK S A")
                clean_candidate = block.replace("-", "").replace(cuit_pattern, "").strip()
                if len(clean_candidate) > 3:
                    razon_social = clean_candidate
                    break
                # Or maybe in the block JUST BEFORE the "Razón Social" label?
                # Find where "Razón Social" label is
                for j in range(len(blocks)):
                    if "RAZÓN SOCIAL" in blocks[j].upper() or "APELLIDO Y NOMBRE" in blocks[j].upper():
                        if j > 0:
                            candidate = blocks[j-1].strip()
                            if len(candidate) > 3 and not any(x in candidate.upper() for x in ["CUIT", "EMISIÓN", ISSUER_CUIT]):
                                razon_social = candidate
                                break
                if razon_social: break

    # Strategy A: Label-based (Fallback)
    if not razon_social:
        name_match = re.search(r"(?:Apellido y Nombre|Razón Social)\s*[:\|]?\s*([^|]{3,})(?=\s*\||$)", text, re.IGNORECASE)
        if name_match:
            candidate = name_match.group(1).strip()
            if not any(x in candidate.upper() for x in ["CUIT", ISSUER_CUIT, "IVA"]):
                razon_social = candidate

    if razon_social:
        # Remove common labels if they leaked in
        razon_social = re.sub(r'(?:Apellido y Nombre|Razón Social)[:\s]*', '', razon_social, flags=re.I).strip()
        razon_social = razon_social.replace('|', '').strip()
        data["cliente"]["razon_social"] = razon_social

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
    # Strategy: Find "Domicilio" block, and take the next significant block that looks like an address
    domicilio = None
    for idx, block in enumerate(blocks):
        if "DOMICILIO" in block.upper() or "DIRECCIÓN" in block.upper():
            # Check if value is in same block
            val = re.sub(r'(?:Domicilio|Dirección)[^:]*[:\s|]*', '', block, flags=re.I).strip()
            if len(val) > 8 and not any(x in val.upper() for x in ["COMERCIAL", "FISCAL"]):
                domicilio = val
            
            # If still nothing, or we only got "Comercial", look at next block
            if not domicilio or any(x in domicilio.upper() for x in ["COMERCIAL", "FISCAL"]):
                if idx < len(blocks) - 1:
                    next_val = blocks[idx+1].strip()
                    if len(next_val) > 8 and not any(x in next_val.upper() for x in ["CONDICIÓN", "LOCALIDAD", "CUIT", "SONIDO LIQUIDO"]):
                         domicilio = next_val
            
            # Avoid issuer address
            if domicilio and "ROSETI" in domicilio.upper():
                domicilio = None
                continue # Keep searching for client address
            
            if domicilio: break

    data["cliente"]["domicilio"] = domicilio.strip() if domicilio else "S/D"

    # 3. ITEMS (Anchor Strategy V2)
    # Pattern looks for: Description, Price/Tax (ignored here but used as anchor), Quantity, Unit
    # AFIP structure: [Qty] [Unit] [Description] ... or [Description] [Qty] [Unit]
    # Block-based extraction usually keeps item lines together.
    
    lines = text.split('|')
    item_pattern = re.compile(r"(\d+[\.,]\d{2,3})\s+(unidades|un|u\.|litros|kg|mts|bultos|oz)", re.IGNORECASE)
    
    items_found = []
    for line in lines:
        match = item_pattern.search(line)
        if match:
            # We found a quantity and unit. The description is usually before or after.
            # In AFIP, it's often: [Desc] [Qty] [Unit] [Price] ...
            # We'll take the whole block as description candidate and clean it.
            qty_str = match.group(1).replace('.', '').replace(',', '.')
            unit = match.group(2)
            
            # Clean description: remove the qty/unit and trailing noise
            desc = line.replace(match.group(0), '').strip()
            # Remove financial columns (approximate)
            desc = re.sub(r'\s+\d+[\.,]\d{2}.*', '', desc) 
            
            if len(desc) > 3 and not any(noise in desc.upper() for noise in ["SUBTOTAL", "IMPORTES", "ALICUOTA", "IVA"]):
                items_found.append({
                    "descripcion": desc,
                    "cantidad": float(qty_str)
                })
            
    data["items"] = items_found

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
