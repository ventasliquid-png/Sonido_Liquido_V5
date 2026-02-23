
import re
import io
import logging
from pypdf import PdfReader
from fastapi import UploadFile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        # [V5 Optimization] Only read first page to avoid duplicates (Triplicado, etc.)
        if len(reader.pages) > 0:
            text = reader.pages[0].extract_text() or ""
        else:
            text = ""
        return text
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        # Re-raise to let caller handle it or return meaningful error
        raise e

def parse_invoice_data(text: str) -> dict:
    """
    Parses raw text from AFIP Invoice V1.
    """
    data = {"cliente": {}, "factura": {}, "items": []}

    # 1. CLEANUP
    # Remove excessive newlines for regex stability
    clean_text = text.replace("\n", " ")

    # 2. FACTURA & CAE
    # "Punto de Venta: 00001 Comp. Nro: 00002489"
    # 2. FACTURA & CAE
    # "Punto de Venta: 00001 Comp. Nro: 00002489" OR "Punto de Venta: Comp. Nro:00001 00002489"
    # Unified pattern to catch both:
    invoice_match = re.search(r"(?:Punto de Venta|PV):?.*?(?:Comp\. Nro|Nro):?\s*(\d+)\s*[-]?\s*(\d+)", clean_text, re.IGNORECASE)
    if invoice_match:
         data["factura"]["numero"] = f"{invoice_match.group(1).zfill(4)}-{invoice_match.group(2).zfill(8)}"
    else:
         # Fallback for "Comp. Nro:00001 00002489" directly
         invoice_match_v2 = re.search(r"Comp\. Nro:?\s*(\d{4,5})\s*(\d{8})", clean_text)
         if invoice_match_v2:
             data["factura"]["numero"] = f"{invoice_match_v2.group(1).zfill(4)}-{invoice_match_v2.group(2).zfill(8)}"

    # CAE N°: 86084487042986
    cae_match = re.search(r"CAE\s*(?:N°|Nro)?:?\s*(\d+)", clean_text, re.IGNORECASE)
    if cae_match:
        data["factura"]["cae"] = cae_match.group(1)

    # Fecha de Vto. de CAE: 01/03/2026
    vto_match = re.search(r"Vto\.?\s*(?:de)?\s*CAE:?\s*(\d{2}/\d{2}/\d{4})", clean_text, re.IGNORECASE)
    if vto_match:
        data["factura"]["vto_cae"] = vto_match.group(1)

    # 3. CLIENTE
    # CUIT Matching
    cuits = re.findall(r"\b(20|23|27|30|33|24)[-]?(\d{8})[-]?(\d{1})\b", text)
    formatted_cuits = [f"{c[0]}-{c[1]}-{c[2]}" for c in cuits]
    
    ISSUER_CUIT = "30-71560397-3"
    client_cuit = None
    
    # Heuristic: The client CUIT is usually the second one found (after Issuer) OR one that appears near "CUIT:" label
    for c in formatted_cuits:
        if c != ISSUER_CUIT:
            client_cuit = c
            break
            
    data["cliente"]["cuit"] = client_cuit

    # Try to find Name (razon_social)
    # Strategy A: Label "Apellido y Nombre / Razón Social:"
    # This often catches empty space if the value is on the next line.
    name_match = re.search(r"(?:Apellido y Nombre|Razón Social)[:\s]+(.*?)(?:Domicilio|Condición|IVA)", clean_text, re.IGNORECASE)
    if name_match:
         candidate = name_match.group(1).strip()
         # If candidate is just separators or empty, ignore
         if len(candidate) > 2 and "/" not in candidate:
            data["cliente"]["razon_social"] = candidate
    
    # Strategy B: "CUIT NAME" line (Common in compressed PDFs like Lavimar)
    # E.g. "30536602913 LAVIMAR S A"
    # [FIX] CUIT in text might not have dashes, but client_cuit does.
    if client_cuit:
        clean_cuit_digits = client_cuit.replace("-", "")
        # Search for CUIT digits followed by text
        # Regex must match the specific "30536602913 LAVIMAR S A" pattern
        line_match = re.search(rf"{clean_cuit_digits}\s+([A-Z0-9\s\.]+)(?:\n|$)", text)
        if line_match:
             potential_name = line_match.group(1).strip()
             # Filter out noise
             if len(potential_name) > 3 and "Av." not in potential_name:
                 data["cliente"]["razon_social"] = potential_name

    # 4. ITEMS (Anchor Strategy)
    # The text splits lines, but "unidades" usually stays with the quantity.
    # Pattern:  [Description] [Quantity] [Unit]
    # Regex:    (.*?)\s+(\d+[\.,]\d{2})\s*(unidades|un|u\.|litros|kg|mts)
    
    items_found = []
    
    # We join lines first to handle some splits? No, pypdf join might be messy.
    # Let's scan line by line.
    
    # Regex to find: Text ending with Number AND Unit
    item_pattern = re.compile(r"(.*?)\s+(\d+[\.,]\d{2})\s*(unidades|un|u\.|litros|kg|mts|bultos)", re.IGNORECASE)
    
    # Filter out header lines that might match this (unlikely but possible)
    lines = text.split('\n')
    
    start_parsing = False
    header_seen = False
    
    for line in lines:
        if "Código Producto" in line or "Descripción" in line:
            start_parsing = True
            header_seen = True
            continue
        if "Subtotal" in line or "CAE N" in line:
            start_parsing = False
            continue
            
        # Safety: Don't parse before we see at least one header-like thing to avoid grabbing address lines
        # Lavimar has "CCódigo Producto / Servicio"
        if "Producto" in line and "Servicio" in line:
             start_parsing = True
             header_seen = True
             continue

        if not header_seen and not start_parsing:
            continue
            
        match = item_pattern.search(line)
        if match:
            desc = match.group(1).strip()
            qty_str = match.group(2).replace('.', '').replace(',', '.') # 6,00 -> 6.00
            
            # Filter noise
            if "Alicuota" in desc or "Precio" in desc:
                continue
            
            # Clean description of common artifacts
            # If desc ends with digits that are part of the product code, keep them.
            
            items_found.append({
                "descripcion": desc,
                "cantidad": float(qty_str)
            })
            
    data["items"] = items_found
    
    return data

async def process_pdf_ingestion(file: UploadFile):
    try:
        content = await file.read()
        if not content:
             return {"success": False, "error": "El archivo está vacío."}
             
        text = extract_text_from_pdf(content)
        if not text or len(text.strip()) < 10:
             return {"success": False, "error": "No se pudo extraer texto del PDF (¿Es una imagen?)."}
             
        parsed_data = parse_invoice_data(text)
        return {"success": True, "data": parsed_data, "raw_text_preview": text[:500]}
    except Exception as e:
        logger.error(f"PDF Processing Failed: {e}")
        import traceback
        trace_str = traceback.format_exc()
        print(f"--- PDF ERROR TRACE ---\n{trace_str}\n-----------------------")
        return {"success": False, "error": f"{str(e)}"}
