from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
print("--- [LOAD] Remitos Router (Soberanía Total V5.1) cargado con éxito ---")
from fastapi.responses import FileResponse
from datetime import datetime
from sqlalchemy.orm import Session
from typing import List
from backend.core.database import get_db
from .pdf_parser import process_pdf_ingestion
from backend.remitos import schemas, models

router = APIRouter(
    prefix="/remitos",
    tags=["Remitos (Logística)"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.RemitoResponse])
def list_remitos(db: Session = Depends(get_db)):
    """
    Lista todos los remitos del sistema con carga ansiosa y mapeo manual de visualización.
    """
    from sqlalchemy.orm import joinedload
    from backend.pedidos.models import Pedido, PedidoItem
    
    remitos = db.query(models.Remito).order_by(models.Remito.fecha_creacion.desc()).all()

    return remitos

@router.get("/{remito_id}", response_model=schemas.RemitoResponse)
def get_remito(remito_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el detalle de un remito específico.
    """
    from sqlalchemy.orm import joinedload
    from backend.pedidos.models import Pedido, PedidoItem
    
    remito = db.query(models.Remito).options(
        joinedload(models.Remito.pedido).joinedload(Pedido.cliente),
        joinedload(models.Remito.items).joinedload(models.RemitoItem.pedido_item).joinedload(PedidoItem.producto)
    ).filter(models.Remito.id == remito_id).first()
    
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
    return remito

@router.get("/por_pedido/{pedido_id}", response_model=List[schemas.RemitoResponse])
def get_remitos_por_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todos los remitos asociados a un pedido específico.
    """
    return db.query(models.Remito).filter(models.Remito.pedido_id == pedido_id).all()

@router.post("/{remito_id}/despachar", response_model=schemas.RemitoResponse)
def despachar_remito(remito_id: str, db: Session = Depends(get_db)):
    """
    Cambia el estado del remito a EN_CAMINO y marca la fecha de salida.
    """
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
    
    remito.estado = "EN_CAMINO"
    remito.fecha_salida = datetime.now()
    db.commit()
    db.refresh(remito)
    return remito

@router.get("/{remito_id}/pdf")
def get_remito_pdf(remito_id: str, db: Session = Depends(get_db)):
    """
    Genera y sirve el PDF de un remito.
    """
    try:
        remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
        if not remito:
            raise HTTPException(status_code=404, detail="Remito no encontrado")
        
        # Preparar datos para el motor
        cliente = remito.pedido.cliente
        items = []
        for r_item in remito.items:
            p_item = r_item.pedido_item
            items.append({
                "codigo": p_item.producto.codigo_visual if p_item.producto else "",
                "descripcion": p_item.producto.nombre if p_item.producto else p_item.nota,
                "cantidad": r_item.cantidad,
                "unidad": "UN" # Default
            })

        # Determine if it's a manual remito (0015- prefix)
        # 0015: Manual (Rosa/Blanco sin intervención fiscal directa en este paso)
        # 0016: Ingesta (Mirror de factura con CAE)
        is_manual = str(remito.numero_legal or "").startswith("0015")
        
        cae_val = getattr(remito, 'cae', None) if not is_manual else None
        vto_cae_val = getattr(remito, 'vto_cae', None) if not is_manual else None

        cliente_data = {
            "razon_social": cliente.razon_social,
            "cuit": cliente.cuit,
            "domicilio_fiscal": remito.domicilio_entrega.resumen if remito.domicilio_entrega else cliente.domicilio_fiscal_resumen or "SIN DOMICILIO FISCAL",
            "condicion_iva": "RESPONSABLE INSCRIPTO", # Default for now
            "factura_vinculada": remito.pedido.nota.replace("Ingesta Automática Factura: ", "") if remito.pedido.nota else "",
            "cae": cae_val,
            "vto_cae": vto_cae_val.strftime("%d/%m/%Y") if vto_cae_val else None,
            "bultos": getattr(remito, 'bultos', 1),
            "valor_declarado": getattr(remito, 'valor_declarado', 0.0),
            "observaciones": remito.pedido.nota or ""
        }
        
        from .remito_engine import generar_remito_pdf
        import os
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        target_dir = os.path.join(base_dir, "DOCUMENTOS_GENERADOS_RAR", "Remitos de salida")
        os.makedirs(target_dir, exist_ok=True)
        
        safe_num = str(remito.numero_legal or remito_id).replace("-", "_")
        final_filename = f"remito_{safe_num}.pdf"
        final_path = os.path.join(target_dir, final_filename)
        
        generar_remito_pdf(
            cliente_data, 
            items, 
            is_preview=False, 
            output_path=final_path, 
            numero_remito=remito.numero_legal,
            cae=cae_val,
            vto_cae=vto_cae_val.strftime("%d/%m/%Y") if vto_cae_val else None
        )
        return FileResponse(
            final_path, 
            media_type='application/pdf', 
            filename=final_filename
        )
    except Exception as e:
        import traceback
        import os
        log_path = os.path.join(os.getcwd(), "pdf_error.log")
        with open(log_path, "w") as f_err:
            f_err.write(f"FATAL ERROR: {str(e)}\n")
            traceback.print_exc(file=f_err)
        print(f"PDF FATAL (logged to {log_path}): {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {str(e)}")

@router.post("/ingesta-pdf")
async def ingest_invoice_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    result = await process_pdf_ingestion(file)
    
    # [V5] ABM Workflow: Verify Client Status in DB
    if result.get("success") and result.get("data"):
        cuit = result["data"].get("cliente", {}).get("cuit")
        if cuit:
            from backend.clientes.models import Cliente
            cliente_db = db.query(Cliente).filter(Cliente.cuit == cuit).first()
            if cliente_db:
                result["data"]["cliente"]["id"] = str(cliente_db.id)
                result["data"]["cliente"]["db_status"] = "EXISTE"
                result["data"]["cliente"]["flags_estado"] = cliente_db.flags_estado
                result["data"]["cliente"]["razon_social"] = cliente_db.razon_social # Overrule PDF with DB truth
                result["data"]["cliente"]["domicilio"] = cliente_db.domicilio_fiscal_resumen or result["data"]["cliente"]["domicilio"]
                # [V5.8 GOLD] Heurística de Matching
                extracted_dom = result["data"]["cliente"]["domicilio"].replace("[EXTRACTED] ", "").upper()
                
                def calculate_score(d_obj, extracted_text):
                    score = 0
                    # Si la calle está contenida (Fuzzy Match simple)
                    if d_obj.calle and d_obj.calle.upper() in extracted_text: score += 50
                    # Si el número coincide perfectamente
                    if d_obj.numero and d_obj.numero in extracted_text: score += 30
                    # Prioridad por tipo
                    if d_obj.es_entrega: score += 10
                    if d_obj.es_fiscal: score += 5
                    return score

                domicilios_raw = []
                for d in cliente_db.domicilios:
                    if not d.activo: continue
                    d_dict = {
                        "id": str(d.id), 
                        "calle": d.calle, 
                        "numero": d.numero, 
                        "localidad": d.localidad, 
                        "es_fiscal": d.es_fiscal, 
                        "es_entrega": d.es_entrega, 
                        "alias": d.alias,
                        "score": calculate_score(d, extracted_dom)
                    }
                    domicilios_raw.append(d_dict)
                
                # Ordenar por score descendente
                domicilios_raw.sort(key=lambda x: x['score'], reverse=True)
                
                # Marcar el mejor como sugerido si supera el umbral
                if domicilios_raw and domicilios_raw[0]['score'] >= 50:
                    domicilios_raw[0]['is_suggested'] = True

                result["data"]["cliente"]["domicilios_disponibles"] = domicilios_raw
                result["data"]["suggested_action"] = "EDIT_CLIENT"
            else:
                result["data"]["cliente"]["db_status"] = "NO_EXISTE"
                result["data"]["cliente"]["flags_estado"] = 0
                result["data"]["suggested_action"] = "CREATE_CLIENT"
                
    return result

@router.post("/ingesta-process", response_model=schemas.RemitoResponse)
def create_remito_from_ingestion(payload: schemas.IngestionPayload, db: Session = Depends(get_db)):
    """
    Toma la salida de la Ingesta PDF y genera un Remito (y Pedido) en la Base de Datos.
    """
    try:
        from backend.remitos.service import RemitosService
        remito = RemitosService.create_from_ingestion(db, payload)
        
        if remito is None:
             # Case: solo_actualizar_cliente=True
             from fastapi.responses import JSONResponse
             return JSONResponse(
                 status_code=200, 
                 content={"status": "success", "message": "Cliente actualizado correctamente. No se generó remito."}
             )

        return remito
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error creating Remito from Ingestion: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.post("/manual", response_model=schemas.RemitoResponse)
def create_manual_remito(payload: schemas.ManualRemitoPayload, db: Session = Depends(get_db)):
    """
    Crea un Remito de forma manual (sin PDF).
    Serie 0015-
    """
    try:
        from backend.remitos.service import RemitosService
        remito = RemitosService.create_manual(db, payload)
        return remito
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error creating Manual Remito: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
@router.patch("/{remito_id}", response_model=schemas.RemitoResponse)
def update_remito(remito_id: str, payload: schemas.RemitoUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un remito existente (Cabecera).
    """
    try:
        from backend.remitos.service import RemitosService
        updated = RemitosService.update_remito(db, remito_id, payload)
        return updated
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error updating Remito {remito_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al actualizar remito")

@router.delete("/{remito_id}")
def delete_remito(remito_id: str, db: Session = Depends(get_db)):
    """
    Elimina un remito en estado BORRADOR y su pedido asociado (si es huérfano de ingesta).
    """
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
    if not remito:
        raise HTTPException(status_code=404, detail="Remito no encontrado")
        
    if remito.estado != "BORRADOR":
        raise HTTPException(status_code=400, detail="Solo se pueden eliminar remitos en estado BORRADOR")
        
    pedido_id = remito.pedido_id
    
    # Delete remito (cascades to remito_items)
    db.delete(remito)
    db.flush()
    
    # Check if we should delete the Pedido too
    from backend.pedidos.models import Pedido
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido and pedido.origen == "INGESTA_PDF":
        db.delete(pedido) # This cascades to pedido_items
        
    db.commit()
    return {"message": "Remito eliminado correctamente"}
