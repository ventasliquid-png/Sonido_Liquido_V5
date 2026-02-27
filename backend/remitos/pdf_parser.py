
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
        
        # [V5 FIX] Solo analizamos la primera página para evitar triplicación 
        # de items (Original, Duplicado, Triplicado)
        if doc.page_count > 0:
            page = doc[0]
            blocks = page.get_text("blocks")
            # Ordenamos por Y (arriba a abajo) y luego X (izq a der)
            blocks.sort(key=lambda b: (b[1], b[0]))
            for b in blocks:
                # b[4] es el texto del bloque
                text_blocks.append(b[4].replace("\n", " ").strip())
        
        doc.close()
        return " | ".join(text_blocks)
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

    # 1. FACTURA & CAE (Robust Pattern from RAR + V5 fix)
    # Pto Vta and Comp Nro
    match_comp = re.search(r'(?:Punto|Pto)?\s*(?:de\s*)?VTA[.\s]*:?\s*(\d{4,5}).*?Comp.*?Nro[.\s]*:?\s*(\d{8})', text, re.IGNORECASE)
    if not match_comp:
        match_comp = re.search(r'Punto\s*de\s*Ventas?[^\d]*(\d{4,5}).*?Comp.*?(?:Nro)?[^\d]*(\d{8})', text, re.IGNORECASE)
    if not match_comp:
        match_comp = re.search(r'(\d{4,5})\s*-\s*(\d{8})', text)
    
    if match_comp:
         data["factura"]["numero"] = f"{match_comp.group(1).zfill(5)}-{match_comp.group(2).zfill(8)}"
    
    # CAE
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
        data["cliente"]["cuit"] = f"{cuit_final[:2]}-{cuit_final[2:10]}-{cuit_final[10:]}"

    # Name and Address Detection (Context-aware)
    # Usually Client name appears after "Apellido y Nombre / Razón Social"
    # [V5 FIX] Replaced empty OR pipe `(?:|...)` with standard lookahead to prevent empty matching
    name_match = re.search(r"(?:Apellido y Nombre|Razón Social)\s*[:\|]\s*(.*?)(?=\s*\||$)", text, re.IGNORECASE)
    if name_match:
         data["cliente"]["razon_social"] = name_match.group(1).strip().replace('|', '').strip()

    # Domicilio (Busqueda en bloques ruidosos)
    dom_match = re.search(r"(?:Domicilio|Dirección)[:\s|]+(.*?)(?:| Localidad| CP| Condición| IVA|$)", text, re.IGNORECASE)
    if dom_match:
         data["cliente"]["domicilio"] = dom_match.group(1).strip().replace('|', '').strip()

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
    return data

async def process_pdf_ingestion(file: UploadFile):
    try:
        content = await file.read()
        logger.info(f"--- [SABUESO INGESTA] Recibido: {file.filename} ({len(content)} bytes) ---")
        
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
