import httpx
import re
import html
import logging
from typing import Dict, Any

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SabuesoWeb")

def normalizar_iva(texto: str) -> str:
    """Normaliza el texto extraído del HTML a etiquetas estándar de RAR."""
    t = html.unescape(texto).strip().upper()
    if "IVA INSCRIPTO" in t or "INSCRIPTO" in t:
        return "RESPONSABLE INSCRIPTO"
    if "MONOTRIBUTO" in t or "MONOTRIBUTISTA" in t:
        return "MONOTRIBUTO"
    if "EXENTO" in t:
        return "EXENTO"
    if "CONSUMIDOR FINAL" in t:
        return "CONSUMIDOR FINAL"
    return t

def scrape_cuit_online(cuit: str) -> Dict[str, Any]:
    """
    Realiza una búsqueda proactiva en CuitOnline para resolver la condición IVA 
    cuando AFIP/ARCA no es concluyente.
    """
    cuit_clean = re.sub(r'[^0-9]', '', str(cuit))
    if len(cuit_clean) != 11:
        return {"error": "CUIT inválido para búsqueda web"}

    url = f"https://www.cuitonline.com/search.php?q={cuit_clean}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://www.google.com/"
    }

    try:
        logger.info(f"Iniciando validación web proactiva para CUIT: {cuit_clean}")
        with httpx.Client(follow_redirects=True, headers=headers, timeout=12.0) as client:
            response = client.get(url)
            if response.status_code != 200:
                return {"error": f"CuitOnline respondió con error {response.status_code}"}
            
            content = response.text
            
            # --- [ETAPA 1: Búsqueda en Lista] ---
            # Razón Social
            name_match = re.search(r'<h2 class="denominacion"[^>]*>([^<]+)</h2>', content, re.IGNORECASE)
            razon_social = html.unescape(name_match.group(1)).strip() if name_match else None
            
            # IVA
            iva_match = re.search(r'IVA:\s*([^<>\n]+)', content, re.IGNORECASE)
            iva_normalized = normalizar_iva(iva_match.group(1)) if iva_match else "REVISAR/NOT_FOUND"

            # Enlace de detalle para el domicilio
            detail_match = re.search(r'href="(detalle/[^"]+)"', content)
            domicilio = "SIN DIRECCIÓN (WEB)"
            
            if detail_match:
                detail_url = f"https://www.cuitonline.com/{detail_match.group(1)}"
                logger.info(f"Siguiendo enlace de detalle: {detail_url}")
                detail_res = client.get(detail_url)
                if detail_res.status_code == 200:
                    detail_content = detail_res.text
                    # Buscar calle, localidad y provincia por itemprop (microdatos )
                    calle_match = re.search(r'itemprop="streetAddress">([^<]+)', detail_content)
                    localidad_match = re.search(r'itemprop="addressLocality"[^>]*>([^<]+)', detail_content)
                    provincia_match = re.search(r'itemprop="addressRegion"[^>]*>([^<]+)', detail_content)
                    
                    calle = html.unescape(calle_match.group(1)).strip() if calle_match else ""
                    loc = html.unescape(localidad_match.group(1)).strip() if localidad_match else ""
                    prov = html.unescape(provincia_match.group(1)).strip() if provincia_match else ""
                    
                    if calle:
                        domicilio = f"{calle}"
                        if loc: domicilio += f", {loc}"
                        if prov: domicilio += f", {prov}"
                    else:
                        # Fallback por regex más amplio (ej: meta description)
                        desc_match = re.search(r'content="[^"]+  ([^]+)  Localidad: ([^]+) ', detail_content)
                        if desc_match:
                            domicilio = f"{desc_match.group(1).strip()}, {desc_match.group(2).strip()}"

            if razon_social or iva_match:
                return {
                    "cuit": cuit_clean,
                    "razon_social": razon_social or "DESCONOCIDO",
                    "domicilio_fiscal": domicilio,
                    "condicion_iva": iva_normalized,
                    "fuente": "CuitOnline (Ficha Detallada)",
                    "confianza": "ALTA"
                }

            return {"error": "No se encontraron datos en la web pública para este CUIT.", "fuente": "CuitOnline"}

    except httpx.ConnectError:
        return {"error": "No se pudo conectar con el servidor de validación web."}
    except Exception as e:
        logger.error(f"Error en SabuesoWeb: {str(e)}")
        return {"error": f"Fallo crítico en validación web: {str(e)}"}

if __name__ == "__main__":
    # Test
    print(scrape_cuit_online("20362621950"))
