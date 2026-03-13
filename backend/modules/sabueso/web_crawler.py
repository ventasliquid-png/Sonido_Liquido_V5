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
        with httpx.Client(follow_redirects=True, headers=headers, timeout=10.0) as client:
            response = client.get(url)
            if response.status_code != 200:
                return {"error": f"CuitOnline respondió con error {response.status_code}"}
            
            content = response.text
            
            # Patrón 1: Renglón de Ganancias/IVA (ej: "Ganancias: Ganancias Personas Fisicas - IVA: Iva Inscripto")
            # El regex busca después de "IVA:" hasta el próximo tag o fin de línea
            iva_match = re.search(r'IVA:\s*([^<>\n]+)', content, re.IGNORECASE)
            
            if iva_match:
                iva_raw = iva_match.group(1).replace("&nbsp;", " ").strip()
                normalized = normalizar_iva(iva_raw)
                logger.info(f"IVA detectado en Web: {normalized}")
                return {
                    "cuit": cuit_clean,
                    "condicion_iva": normalized,
                    "fuente": "CuitOnline (Validación Web)",
                    "confianza": "ALTA"
                }
            
            # Patrón 2: Condición IVA explícita en otro formato
            condicion_match = re.search(r'Condición IVA:\s*([^<>\n]+)', content, re.IGNORECASE)
            if condicion_match:
                iva_raw = condicion_match.group(1).replace("&nbsp;", " ").strip()
                normalized = normalizar_iva(iva_raw)
                return {
                    "cuit": cuit_clean,
                    "condicion_iva": normalized,
                    "fuente": "CuitOnline (Validación Web)",
                    "confianza": "ALTA"
                }

            return {"error": "IVA no encontrado en la ficha web pública", "fuente": "CuitOnline"}

    except httpx.ConnectError:
        return {"error": "No se pudo conectar con el servidor de validación web."}
    except Exception as e:
        logger.error(f"Error en SabuesoWeb: {str(e)}")
        return {"error": f"Fallo crítico en validación web: {str(e)}"}

if __name__ == "__main__":
    # Test
    print(scrape_cuit_online("20362621950"))
