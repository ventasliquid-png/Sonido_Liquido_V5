# [IDENTIDAD] - backend/ingesta/router.py
# Versión: V5.6 GOLD | Sincronización: 20260508191500
# ------------------------------------------
import uuid
import io
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.ingesta.service import IngestaService

router = APIRouter(prefix="/ingesta", tags=["ingesta"])

@router.post("/raw")
async def upload_raw(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        content = await file.read()
        raw = IngestaService.store_raw(db, content, file.filename)
        
        parsed_data = raw.parsed_data_raw
        duplicado = {"encontrado": False}
        
        if parsed_data and isinstance(parsed_data, dict):
            factura_data = parsed_data.get("factura", {})
            numero = factura_data.get("numero")
            cae = factura_data.get("cae")
            
            pv = 0
            nc = 0
            if numero:
                try:
                    parts = numero.split("-")
                    if len(parts) == 2:
                        pv = int(parts[0])
                        nc = int(parts[1])
                except:
                    pass
            
            if pv > 0 and nc > 0:
                cond_iva = (parsed_data.get("cliente", {}).get("condicion_iva") or "").upper()
                tipo_comprobante = "FACTURA_B"
                if "INSCRIPTO" in cond_iva:
                    tipo_comprobante = "FACTURA_A"
                elif "MONOTRIBUTO" in cond_iva:
                    tipo_comprobante = "FACTURA_C"
                
                from backend.facturacion.models import Factura
                from backend.ingesta.models import FacturasProcesadas
                
                existing_factura = db.query(Factura).filter(
                    Factura.tipo_comprobante == tipo_comprobante,
                    Factura.punto_venta == pv,
                    Factura.numero_comprobante == nc
                ).first()
                
                if existing_factura:
                    remito_id = None
                    remito_estado = None
                    if existing_factura.vinculos_remitos:
                        linked_remito = existing_factura.vinculos_remitos[0].remito
                        if linked_remito:
                            remito_id = str(linked_remito.id)
                            remito_estado = linked_remito.estado
                            
                    raw_id_anterior = None
                    fecha_procesamiento = None
                    
                    procesada = None
                    if existing_factura.pedido_id:
                        procesada = db.query(FacturasProcesadas).filter(
                            FacturasProcesadas.pedido_id == existing_factura.pedido_id
                        ).first()
                        
                    if not procesada:
                        invoice_num_str = f"{pv:05d}-{nc:08d}"
                        procesada = db.query(FacturasProcesadas).filter(
                            (FacturasProcesadas.numero_factura == invoice_num_str) |
                            (FacturasProcesadas.numero_factura == f"{pv}-{nc}")
                        ).first()
                        
                    if not procesada and cae:
                        procesada = db.query(FacturasProcesadas).filter(
                            FacturasProcesadas.cae == cae
                        ).first()
                        
                    if procesada:
                        raw_id_anterior = str(procesada.raw_id)
                        dt = procesada.processed_at or procesada.created_at
                        fecha_procesamiento = dt.isoformat() if dt else None
                        
                    duplicado = {
                        "encontrado": True,
                        "tipo_comprobante": existing_factura.tipo_comprobante,
                        "punto_venta": existing_factura.punto_venta,
                        "numero_comprobante": existing_factura.numero_comprobante,
                        "factura_id": str(existing_factura.id),
                        "pedido_id": existing_factura.pedido_id,
                        "remito_id": remito_id,
                        "remito_estado": remito_estado,
                        "raw_id_anterior": raw_id_anterior,
                        "fecha_procesamiento": fecha_procesamiento
                    }
        
        return {
            "id": raw.id, 
            "filename": raw.filename, 
            "status": raw.audit_status, 
            "duplicado": duplicado
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/raw/{raw_id}/preview")
def get_preview(raw_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        return IngestaService.preview(db, raw_id)
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/raw/{raw_id}/approve")
def approve_ingesta(raw_id: uuid.UUID, edited_data: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        procesada = IngestaService.approve(db, raw_id, edited_data)
        return {
            "id": procesada["id"],
            "estado": procesada["estado"],
            "remito_id": procesada.get("remito_id")
        }
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/raw/{raw_id}/quarantine")
def quarantine_ingesta(raw_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        raw = IngestaService.quarantine(db, raw_id)
        return {"id": raw.id, "status": raw.audit_status, "flags": raw.flags_estado}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/procesadas/{proc_id}")
def get_procesada(proc_id: uuid.UUID, db: Session = Depends(get_db)):
    procesada = IngestaService.get_procesada(db, proc_id)
    if not procesada:
        raise HTTPException(status_code=404, detail="Factura procesada no encontrada")
    return procesada

@router.get("/raw/{raw_id}/pdf")
def get_raw_pdf(raw_id: uuid.UUID, db: Session = Depends(get_db)):
    from backend.ingesta.models import FacturasRaw
    raw = db.query(FacturasRaw).filter(FacturasRaw.id == raw_id).first()
    if not raw:
        raise HTTPException(status_code=404, detail="Factura Raw no encontrada")
    return StreamingResponse(
        io.BytesIO(raw.pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "inline"}
    )

class AnularPayload(BaseModel):
    factura_id: uuid.UUID
    pin: str

@router.post("/raw/{raw_id}/anular-y-reingestar")
def anular_y_reingestar(raw_id: uuid.UUID, payload: AnularPayload, db: Session = Depends(get_db)):
    if payload.pin != "1974":
        raise HTTPException(status_code=403, detail="PIN incorrecto. Operación no autorizada.")
        
    from backend.ingesta.models import FacturasRaw, FacturasProcesadas
    raw_nuevo = db.query(FacturasRaw).filter(FacturasRaw.id == raw_id).first()
    if not raw_nuevo:
        raise HTTPException(status_code=404, detail="Nueva Factura Raw no encontrada")
        
    from backend.facturacion.models import Factura
    factura_vieja = db.query(Factura).filter(Factura.id == payload.factura_id).first()
    if not factura_vieja:
        raise HTTPException(status_code=404, detail="Factura a anular no encontrada")
        
    # 1. Verificar que remito asociado esté en BORRADOR
    linked_remito = None
    if factura_vieja.vinculos_remitos:
        linked_remito = factura_vieja.vinculos_remitos[0].remito
        
    if linked_remito and linked_remito.estado != "BORRADOR":
        raise HTTPException(status_code=409, detail="Remito ya despachado, no se puede anular")
        
    # 2. Marcar RAW viejo con Bit 11 (DUPLICATE=2048)
    procesada_vieja = None
    if factura_vieja.pedido_id:
        procesada_vieja = db.query(FacturasProcesadas).filter(
            FacturasProcesadas.pedido_id == factura_vieja.pedido_id
        ).first()
        
    if not procesada_vieja:
        pv, nc = factura_vieja.punto_venta, factura_vieja.numero_comprobante
        invoice_num_str = f"{pv:05d}-{nc:08d}"
        procesada_vieja = db.query(FacturasProcesadas).filter(
            (FacturasProcesadas.numero_factura == invoice_num_str) |
            (FacturasProcesadas.numero_factura == f"{pv}-{nc}")
        ).first()
        
    if procesada_vieja:
        raw_viejo = db.query(FacturasRaw).filter(FacturasRaw.id == procesada_vieja.raw_id).first()
        if raw_viejo:
            raw_viejo.flags_estado = (raw_viejo.flags_estado or 0) | 2048
            db.add(raw_viejo)
        procesada_vieja.estado = "ANULADA"
        db.add(procesada_vieja)
        
    # 3. Verificar pedido asociado
    if factura_vieja.pedido_id:
        from backend.pedidos.models import Pedido
        from backend.pedidos.constants import PedidoFlags
        pedido_asoc = db.query(Pedido).filter(Pedido.id == factura_vieja.pedido_id).first()
        if pedido_asoc:
            if pedido_asoc.flags_estado & PedidoFlags.ORIGEN_FACTURA:
                pedido_asoc.estado = "ANULADO"
                pedido_asoc.flags_estado = (pedido_asoc.flags_estado & ~PedidoFlags.STATE_MASK) | PedidoFlags.ES_ANULADO
                db.add(pedido_asoc)
                
    # 4. Eliminar remito en BORRADOR
    if linked_remito:
        db.delete(linked_remito)
        
    # 5. Eliminar/anular factura mirror
    db.delete(factura_vieja)
    
    # 6. Dejar el nuevo RAW listo para procesar normalmente
    raw_nuevo.audit_status = "RECIBIDO"
    raw_nuevo.flags_estado &= ~2048
    db.add(raw_nuevo)
    
    db.commit()
    return { "status": "ok", "raw_id_nuevo": str(raw_nuevo.id) }
