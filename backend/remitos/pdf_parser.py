import re
import fitz
import logging
from typing import Optional
from fastapi import UploadFile

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
    """Parse Argentine number format: '9.750,00' or '9750,00' -> 9750.0"""
    s = s.strip()
    if ',' in s:
        return float(s.replace('.', '').replace(',', '.'))
    return float(s)

def _iso_date(val: str) -> Optional[str]:
    """Convierte DD/MM/YYYY a YYYY-MM-DD para Pydantic"""
    if not val or "/" not in val: return val
    try:
        parts = val.split('/')
        if len(parts) == 3:
            return f"{parts[2]}-{parts[1]}-{parts[0]}"
    except:
        pass
    return val

def parse_invoice_data(text: str, words_data: list = None) -> dict:
    """
    Parses raw text and word data using Sabueso Zonal Heuristics (V5.5).
    """
    data = {"cliente": {"domicilio": ""}, "factura": {}, "items": []}
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
    # [V5.7 Robustness] Handle both: "PV: XXXX Comp: YYYY" AND "PV: Comp: XXXX YYYY"
    match_comp = re.search(r'Punto.*?Comp.*?Nro[.\s:|]*\s*(\d{4,5})[\s\-]+(\d{8})', text, re.IGNORECASE)
    if not match_comp:
        match_comp = re.search(r'Punto\s*de\s*Ventas?[^\d]*(\d{4,5}).*?Comp.*?(?:Nro)?[^\d]*(\d{8})', text, re.IGNORECASE)
    
    if match_comp:
         pv = match_comp.group(1).zfill(5)
         nc = match_comp.group(2).zfill(8)
         data["factura"]["numero"] = f"{pv}-{nc}"
    else:
        # Last ditch: Look for two long sequences of numbers near "Comp"
        match_lazy = re.search(r'Comp[^\d]*(\d{4,5})[^\d]+(\d{8})', text, re.IGNORECASE)
        if match_lazy:
             data["factura"]["numero"] = f"{match_lazy.group(1).zfill(5)}-{match_lazy.group(2).zfill(8)}"
    
    match_cae = re.search(r'C\.?A\.?E\.?.*?(?:\:)?.*?(\d{14})', text, re.IGNORECASE)
    if match_cae: data["factura"]["cae"] = match_cae.group(1)

    match_vto = re.search(r'(?:Vto|Vencimiento).*?(\d{2}/\d{2}/\d{4})', text, re.IGNORECASE)
    if match_vto: 
        data["factura"]["vto_cae"] = _iso_date(match_vto.group(1))

    match_neto = re.search(r'Importe Neto Gravado:\s*\$?\s*([\d\.,]+)', text, re.IGNORECASE)
    if match_neto: data["factura"]["total_neto"] = _parse_ar_float(match_neto.group(1))
    
    match_total = re.search(r'Importe Total:\s*\$?\s*([\d\.,]+)', text, re.IGNORECASE)
    if match_total: data["factura"]["total_final"] = _parse_ar_float(match_total.group(1))

    # 2. CLIENTE (CUIT & Razón Social)
    cuit_final = None
    labels_cuit = re.finditer(r"(?:CUIT|CUIL)[:\s|]*((?:20|23|24|27|30|33|34)\-?\d{8}\-?\d{1})", text, re.IGNORECASE)
    for match in labels_cuit:
        c = match.group(1).replace("-", "").strip()
        if c != ISSUER_CUIT:
            cuit_final = c
            break
    if cuit_final: data["cliente"]["cuit"] = cuit_final

    blocks = [b.strip() for b in text.split('|')]
    razon_social = None
    if cuit_final:
        for block in blocks:
            if cuit_final in block.replace("-", ""):
                clean_candidate = block.replace("-", "").replace(cuit_final, "").strip()
                if len(clean_candidate) > 3:
                    razon_social = clean_candidate
                    break
    if not razon_social:
        name_match = re.search(r"(?:Apellido y Nombre|Razón Social)\s*[:\|]?\s*([^|]{3,})(?=\s*\||$)", text, re.IGNORECASE)
        if name_match: razon_social = name_match.group(1).strip()

    if razon_social:
        razon_social = re.sub(r'(?:Apellido y Nombre|Razón Social)[:\s]*', '', razon_social, flags=re.I).strip()
        razon_social = razon_social.replace('|', '').strip()
        data["cliente"]["razon_social"] = razon_social.upper()

    iva_match = re.search(r"(?:Condición frente al IVA|IVA)[:\|]?\s*([^|]{5,30})(?=\s*\||$)", text, re.IGNORECASE)
    if iva_match:
        iva_val = iva_match.group(1).strip().upper()
        if "INSCRIPTO" in iva_val: data["cliente"]["condicion_iva"] = "Responsable Inscripto"
        elif "MONOTRIBUTO" in iva_val: data["cliente"]["condicion_iva"] = "Monotributista"
        elif "EXENTO" in iva_val: data["cliente"]["condicion_iva"] = "Exento"
        elif "CONSUMIDOR FINAL" in iva_val: data["cliente"]["condicion_iva"] = "Consumidor Final"
        else: data["cliente"]["condicion_iva"] = iva_val
    
    dom_match = re.search(r"(?:Domicilio Comercial|Domicilio)[:\|]?\s*([^|]{5,100})(?=\s*\||$)", text, re.IGNORECASE)
    if dom_match: data["cliente"]["domicilio"] = dom_match.group(1).strip()

    # --- [SABUESO V5.5 ZONAL ITEMS] ---
    if words_data:
        # 1. Agrupamos palabras por línea (Y0) con tolerancia de 4 pts
        lines = {}
        for w in words_data:
            x0, y0, x1, y1, val, *_ = w
            y_key = round(y0 / 6) * 6
            if y_key not in lines: lines[y_key] = []
            lines[y_key].append({"x0": x0, "text": val})
        
        sorted_y = sorted(lines.keys())
        items_v55 = []
        current_item = None
        table_started = False
        VALID_UNITS = ["UNIDADES", "UN.", "U.", "LITROS", "KG", "MTS", "BULTOS", "OZ", "UN"]

        for y in sorted_y:
            row_words = sorted(lines[y], key=lambda w: w["x0"])
            row_text = " ".join(w["text"] for w in row_words).upper()
            
            # [V5.5] Gate de Salida: Si detectamos el pie de página, cortamos.
            if table_started and any(term in row_text for term in ["NETO GRAVADO", "TOTAL VTA", "SUBTOTAL", "SON PESOS"]):
                table_started = False
                current_item = None
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

            if has_data_anchor and row_data["cantidad"] is not None:
                current_item = {
                    "descripcion": row_data["descripcion"],
                    "cantidad": row_data["cantidad"],
                    "precio_unitario": row_data["precio"] or 0.0,
                    "alicuota_iva": row_data["iva"],
                    "subtotal": round(row_data["cantidad"] * (row_data["precio"] or 0.0), 2)
                }
                items_v55.append(current_item)
            elif current_item and row_data["descripcion"] and not any(n in row_data["descripcion"].upper() for n in ["SUBTOTAL", "TOTAL", "CAE", "NETO", "FACTURA", "PAG.", "IMPORTE"]):
                current_item["descripcion"] += " " + row_data["descripcion"]

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

    # OC & Canal
    oc_match = re.search(r'OC:\s*(OC\s+[\w\d]+)', text, re.IGNORECASE)
    if oc_match: data["factura"]["oc"] = oc_match.group(1).strip()
    if "MERCADO LIBRE" in text.upper() or "MELI" in text.upper(): data["cliente"]["canal"] = "MLIBRE"
    elif "TIENDA NUBE" in text.upper() or "TIENDANUBE" in text.upper(): data["cliente"]["canal"] = "TIENDANUBE"
        
    return data

async def process_pdf_ingestion(file: UploadFile):
    try:
        content = await file.read()
        logger.info(f"--- [SABUESO INGESTA] Recibido: {file.filename} ---")
        
        text, words_data = extract_text_from_pdf(content)
        if not text or len(text.strip()) < 10:
             return {"success": False, "error": "No se pudo extraer texto del PDF."}
             
        parsed_data = parse_invoice_data(text, words_data)
        
        # [V5 EVO] Validation
        if not parsed_data['cliente'].get('cuit') or not parsed_data['items']:
            logger.warning("[SABUESO] Ingesta incompleta.")
            
        return {"success": True, "data": parsed_data}
    except Exception as e:
        logger.error(f"Error en ingesta: {str(e)}")
        return {"success": False, "error": str(e)}
