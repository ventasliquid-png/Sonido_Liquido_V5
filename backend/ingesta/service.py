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

        # Checkpoint visible: el raw entra en vuelo
        raw.audit_status = "PROCESANDO"
        db.add(raw)
        db.commit()

        try:
            # 1. Impactar Sistema V5 (Remito + Factura Mirror)
            from backend.remitos.service import RemitosService
            from backend.remitos.schemas import IngestionPayload

            payload = IngestionPayload(**edited_data)
            remito = RemitosService.create_from_ingestion(db, payload)
            remito_id = str(remito.id) if remito else None

            # 2. Crear FacturaProcesada (Persistencia de Auditoría)
            p_cliente_id = edited_data.get("cliente", {}).get("id")
            p_pedido_id = edited_data.get("pedido_id_vinculado")

            is_cuarentena = edited_data.get("modo_cuarentena", False)
            procesada = FacturasProcesadas(
                raw_id=raw.id,
                cliente_id=p_cliente_id,
                pedido_id=p_pedido_id,
                numero_factura=edited_data.get("factura", {}).get("numero"),
                cae=edited_data.get("factura", {}).get("cae"),
                vto_cae=edited_data.get("factura", {}).get("vto_cae"),
                parsed_data_final=edited_data,
                audit_log=edited_data.get("audit_log", {}),
                estado="CUARENTENA" if is_cuarentena else "APROBADA",
                processed_at=datetime.now(timezone.utc)
            )
            db.add(procesada)

            if is_cuarentena:
                from backend.ingesta.constants import IngestaFlags
                raw.audit_status = "CUARENTENA"
                raw.flags_estado |= IngestaFlags.RAW_EN_CUARENTENA
            else:
                raw.audit_status = "PROCESADO"
            raw.processed_at = datetime.now(timezone.utc)
            db.add(raw)
            db.commit()

            return {
                "id": str(procesada.id),
                "remito_id": remito_id,
                "estado": "CUARENTENA" if is_cuarentena else "APROBADA"
            }

        except Exception as e:
            import logging
            logging.error(f"[IngestaService.approve] Error: {e}")
            try:
                raw.audit_status = "ERROR"
                db.add(raw)
                db.commit()
            except Exception:
                db.rollback()
            raise


    @staticmethod
    def get_procesada(db: Session, proc_id: uuid.UUID) -> FacturasProcesadas:
        return db.query(FacturasProcesadas).filter(FacturasProcesadas.id == proc_id).first()

    @staticmethod
    def quarantine(db: Session, raw_id: uuid.UUID) -> FacturasRaw:
        """
        Pone una factura RAW en cuarentena (STOP Doctrinal).
        Enciende Bit 2 (4) en flags_estado.
        """
        raw = db.query(FacturasRaw).filter(FacturasRaw.id == raw_id).first()
        if not raw:
            raise ValueError("Factura Raw no encontrada")
            
        from backend.ingesta.constants import IngestaFlags
        raw.audit_status = "CUARENTENA"
        raw.flags_estado |= IngestaFlags.RAW_EN_CUARENTENA
        
        db.add(raw)
        db.commit()
        db.refresh(raw)
        return raw
