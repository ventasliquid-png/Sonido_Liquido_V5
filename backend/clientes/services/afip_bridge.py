import sys
import os
import logging
from typing import Dict, Any, Optional

# --- CONFIGURACIÓN DEL PUENTE ---
RAR_PATH = "C:/dev/RAR_V1"
logger = logging.getLogger(__name__)

class AfipBridgeService:
    """
    Puente de Inteligencia Fiscal RAR-V5.
    Permite a V5 utilizar el motor de validación de RAR V1 como librería satélite.
    """
    
    @staticmethod
    def get_datos_afip(cuit: str) -> Dict[str, Any]:
        """
        Consulta el Padrón A13 de AFIP a través de Sabueso Oro (V5 Internal).
        """
        try:
            # Importación desde el nuevo ámbito Sabueso V5
            try:
                from backend.modules.sabueso.Conexion_Blindada import get_datos_afip
            except ImportError as e:
                import traceback
                error_detail = traceback.format_exc()
                logger.error(f"FATAL: No se pudo importar Sabueso desde backend.modules.sabueso.\n{error_detail}")
                return {"error": f"Error de inyección Sabueso: {str(e)}", "detail": error_detail}
            
            # Ejecución blindada
            logger.info(f"[PUENTE RAR] Consultando AFIP para CUIT: {cuit}")
            resultado = get_datos_afip(cuit)
            
            # Post-procesamiento: Normalizar para esquema V5
            if "error" in resultado:
                logger.warning(f"[PUENTE RAR] Error AFIP: {resultado['error']}")
                return resultado
            
            logger.info(f"[PUENTE RAR] Éxito. Normalizando datos para: {resultado.get('razon_social', 'Desconocido')}")
            return AfipBridgeService.normalize_for_v5(resultado)
            
        except Exception as e:
            import traceback
            error_msg = f"Error interno en Puente RAR: {str(e)}"
            logger.error(f"[PUENTE RAR] CRITICAL: {error_msg}")
            logger.error(traceback.format_exc())
            return {"error": error_msg}

    @staticmethod
    def normalize_for_v5(rar_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapta la respuesta de RAR al esquema que espera el Frontend de V5.
        """
        if "error" in rar_data:
            return rar_data
            
        # Mapeo de Campos RAR -> V5
        return {
            "cuit": rar_data.get("cuit", ""),
            "razon_social": rar_data.get("razon_social", ""), # RAR core ya normaliza esto
            "condicion_iva": rar_data.get("condicion_iva", ""),
            "domicilio_fiscal": rar_data.get("domicilio_fiscal", ""),
            "parsed_address": rar_data.get("parsed_address", {}),
            # Datos crudos para debug
            "_raw_rar": rar_data
        }

# [GY-TRICK] Forcing uvicorn reload to clear RAR module cache
