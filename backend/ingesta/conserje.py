# [IDENTIDAD] - backend/ingesta/conserje.py
# Versión: V5.6 GOLD | Sincronización: 20260508191300
# ------------------------------------------
import re
import fitz
import logging
import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.clientes.models import Cliente, Domicilio
from backend.maestros.models import CondicionIva

logger = logging.getLogger(__name__)

class ConserjeV2:
    """
    Motor de Inteligencia de Ingesta (Stateless).
    Especializado en auditoría de PDFs AFIP y resolución de identidades.
    """
    
    @staticmethod
    def extract_text(file_bytes: bytes) -> tuple:
        """
        Extrae texto y palabras con coordenadas de un PDF.
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text_blocks = []
            words_data = []
            
            if doc.page_count > 0:
                page = doc[0]
                blocks = page.get_text("blocks")
                blocks.sort(key=lambda b: (b[1], b[0]))
                for b in blocks:
                    text_blocks.append(b[4].replace("\n", " ").strip())
                words_data = page.get_text("words")
            
            doc.close()
            full_text = " | ".join(text_blocks)
            return full_text, words_data
        except Exception as e:
            logger.error(f"Conserje: Error extrayendo texto: {e}")
            raise e

    @staticmethod
    def parse_afip_pdf(text: str, words_data: list = None) -> dict:
        """
        Heurística Sabueso V5.5 para extraer datos de factura AFIP.
        """
        from backend.remitos.pdf_parser import parse_invoice_data
        # Delegamos a la lógica existente de Sabueso V5.5
        return parse_invoice_data(text, words_data)

    @staticmethod
    def resolve_client(db: Session, cuit: Optional[str], nombre: Optional[str], payload_id: Any = None) -> Dict[str, Any]:
        """
        Resuelve la identidad del cliente en la DB.
        Retorna {cliente: Cliente, status: str, warnings: list}
        """
        warnings = []
        status = "DESCONOCIDO"
        cliente = None
        
        cuit_clean = (cuit or "").replace("-", "").strip()
        nombre_clean = (nombre or "").strip()
        
        # 1. Por ID directo (si el frontend lo mandó)
        if payload_id:
            cliente = db.query(Cliente).filter(Cliente.id == payload_id).first()
            if cliente: status = "EXISTE_ID"
            
        # 2. Por CUIT
        if not cliente and cuit_clean and cuit_clean != "00000000000":
            cliente = db.query(Cliente).filter(
                or_(
                    Cliente.cuit == cuit_clean,
                    Cliente.cuit == f"{cuit_clean[:2]}-{cuit_clean[2:10]}-{cuit_clean[10:]}"
                )
            ).first()
            if cliente: status = "EXISTE_CUIT"
            
        # 3. Por Nombre (Fuzzy)
        if not cliente and nombre_clean:
            cliente = db.query(Cliente).filter(Cliente.razon_social.ilike(f"%{nombre_clean}%")).first()
            if cliente:
                status = "EXISTE_NOMBRE"
                warnings.append(f"Cliente encontrado por nombre, CUIT no coincide o no existe en DB.")

        return {
            "cliente": cliente,
            "db_status": status if cliente else "NO_EXISTE",
            "razon_social": cliente.razon_social if cliente else None,
            "flags_estado": cliente.flags_estado if cliente else 0,
            "warnings": warnings
        }



    @staticmethod
    def audit_ingestion(parsed_data: dict, db: Session) -> dict:
        """
        Realiza una auditoría completa de los datos parseados contra la realidad de la DB.
        Retorna el audit_log para FacturasProcesadas.
        """
        log = {
            "decisions": [],
            "warnings": [],
            "confidence": 100,
            "client_resolution": {},
            "totals_check": "OK",
            "domicilios_scoring": []
        }
        
        # 1. Cliente
        res = ConserjeV2.resolve_client(
            db, 
            parsed_data["cliente"].get("cuit"), 
            parsed_data["cliente"].get("razon_social")
        )
        log["client_resolution"] = {
            "db_status": res["db_status"],
            "id": str(res["cliente"].id) if res["cliente"] else None,
            "razon_social": res["razon_social"],
            "flags_estado": res["flags_estado"]
        }
        log["warnings"].extend(res["warnings"])
        
        if res["db_status"] == "NO_EXISTE":
            log["confidence"] -= 30
            log["decisions"].append("Requiere creación de cliente nuevo.")
            
        # 2. Totales
        if parsed_data["factura"].get("audit_status") == "CONSULTA_FLAG":
            log["totals_check"] = "WARNING"
            log["warnings"].append(parsed_data["factura"].get("audit_warning"))
            log["confidence"] -= 20
            
        # 3. Domicilios
        # La Ingesta ya no adivina ni realiza scoring heurístico sobre los domicilios 
        # para preservar la Soberanía del Pedido.
        # Si el cliente existe, la sede se hereda de su Pedido o se selecciona manualmente.
        log["domicilios_scoring"] = []
            
        return log
