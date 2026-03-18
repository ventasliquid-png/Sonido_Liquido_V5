
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
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
    Lista todos los remitos del sistema.
    """
    return db.query(models.Remito).order_by(models.Remito.fecha_creacion.desc()).all()

@router.get("/{remito_id}", response_model=schemas.RemitoResponse)
def get_remito(remito_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el detalle de un remito específico.
    """
    remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
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
        
        cliente_data = {
            "razon_social": cliente.razon_social,
            "cuit": cliente.cuit,
            "domicilio_fiscal": next((d.calle for d in cliente.domicilios if d.es_fiscal), "SIN DOMICILIO FISCAL"),
            "condicion_iva": "RESPONSABLE INSCRIPTO", # Default for now
            "factura_vinculada": remito.pedido.nota.replace("Ingesta Automática Factura: ", "") if remito.pedido.nota else "",
            "cae": remito.cae,
            "vto_cae": remito.vto_cae.strftime("%d/%m/%Y") if remito.vto_cae else None
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
            cae=remito.cae,
            vto_cae=remito.vto_cae.strftime("%d/%m/%Y") if remito.vto_cae else None
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
