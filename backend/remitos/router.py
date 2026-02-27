
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
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
        import tempfile
        import os
        
        temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_path = temp_pdf.name
        temp_pdf.close()
        
        generar_remito_pdf(
            cliente_data, 
            items, 
            is_preview=False, 
            output_path=temp_path, 
            numero_remito=remito.numero_legal,
            cae=remito.cae,
            vto_cae=remito.vto_cae.strftime("%d/%m/%Y") if remito.vto_cae else None
        )
        return FileResponse(
            temp_path, 
            media_type='application/pdf', 
            filename=f"remito_{remito.numero_legal or remito_id}.pdf"
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
                result["data"]["cliente"]["db_status"] = "EXISTE"
                result["data"]["cliente"]["flags_estado"] = cliente_db.flags_estado
                result["data"]["cliente"]["razon_social"] = cliente_db.razon_social # Overrule PDF with DB truth
            else:
                result["data"]["cliente"]["db_status"] = "NO_EXISTE"
                result["data"]["cliente"]["flags_estado"] = 0
                
    return result

@router.post("/ingesta-process", response_model=schemas.RemitoResponse)
def create_remito_from_ingestion(payload: schemas.IngestionPayload, db: Session = Depends(get_db)):
    """
    Toma la salida de la Ingesta PDF y genera un Remito (y Pedido) en la Base de Datos.
    """
    try:
        from backend.remitos.service import RemitosService
        remito = RemitosService.create_from_ingestion(db, payload)
        return remito
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Error creating Remito from Ingestion: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
