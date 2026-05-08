# [IDENTIDAD] - backend/ingesta/service.py
# Versión: V5.6 GOLD | Sincronización: 20260508191400
# ------------------------------------------
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.ingesta.models import FacturasRaw, FacturasProcesadas
from backend.ingesta.conserje import ConserjeV2

class IngestaService:
    @staticmethod
    def store_raw(db: Session, file_bytes: bytes, filename: str) -> FacturasRaw:
        """
        Almacena el PDF crudo e inicia el parsing inicial.
        """
        text, words_data = ConserjeV2.extract_text(file_bytes)
        parsed_data = ConserjeV2.parse_afip_pdf(text, words_data)
        
        raw = FacturasRaw(
            filename=filename,
            pdf_bytes=file_bytes,
            parsed_data_raw=parsed_data,
            audit_status="RECIBIDO"
        )
        db.add(raw)
        db.commit()
        db.refresh(raw)
        return raw

    @staticmethod
    def preview(db: Session, raw_id: uuid.UUID) -> dict:
        """
        Genera un preview del procesamiento (READ-ONLY).
        """
        raw = db.query(FacturasRaw).filter(FacturasRaw.id == raw_id).first()
        if not raw:
            raise ValueError("Factura Raw no encontrada")
            
        import json
        p_data = raw.parsed_data_raw
        if isinstance(p_data, str):
            try:
                p_data = json.loads(p_data)
            except: pass

        audit_log = ConserjeV2.audit_ingestion(p_data, db)
        
        return {
            "raw_id": str(raw.id),
            "filename": raw.filename,
            "audit_log": audit_log,
            "parsed_data": p_data
        }

    @staticmethod
    def approve(db: Session, raw_id: uuid.UUID, edited_data: dict) -> dict:
        """
        Aprueba la ingesta y crea el registro de FacturaProcesada + Remito + Factura Mirror.
        """
        raw = db.query(FacturasRaw).filter(FacturasRaw.id == raw_id).first()
        if not raw:
            raise ValueError("Factura Raw no encontrada")
            
        # 1. Impactar Sistema V5 (Remito + Factura Mirror)
        from backend.remitos.service import RemitosService
        from backend.remitos.schemas import IngestionPayload
        
        remito_id = None
        try:
            # El payload del frontend ya está estructurado como IngestionPayload
            payload = IngestionPayload(**edited_data)
            remito = RemitosService.create_from_ingestion(db, payload)
            if remito:
                remito_id = str(remito.id)
        except Exception as e:
            import logging
            logging.error(f"Error impactando sistema desde IngestaService.approve: {e}")
            raise e
            
        # 2. Crear FacturaProcesada (Persistencia de Auditoría)
        # Extraemos IDs si existen en el payload editado
        p_cliente_id = edited_data.get("cliente", {}).get("id")
        p_pedido_id = edited_data.get("pedido_id_vinculado")
        
        procesada = FacturasProcesadas(
            raw_id=raw.id,
            cliente_id=p_cliente_id,
            pedido_id=p_pedido_id,
            numero_factura=edited_data.get("factura", {}).get("numero"),
            cae=edited_data.get("factura", {}).get("cae"),
            vto_cae=edited_data.get("factura", {}).get("vto_cae"),
            parsed_data_final=edited_data,
            audit_log=edited_data.get("audit_log", {}),
            estado="APROBADA",
            processed_at=datetime.now(timezone.utc)
        )
        db.add(procesada)
        
        raw.audit_status = "PROCESADO"
        raw.processed_at = datetime.now(timezone.utc)
        
        db.add(raw)
        db.commit()
        
        return {
            "id": str(procesada.id),
            "remito_id": remito_id,
            "estado": "APROBADA"
        }


    @staticmethod
    def get_procesada(db: Session, proc_id: uuid.UUID) -> FacturasProcesadas:
        return db.query(FacturasProcesadas).filter(FacturasProcesadas.id == proc_id).first()
