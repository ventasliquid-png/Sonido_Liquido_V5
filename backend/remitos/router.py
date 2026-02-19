
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from .pdf_parser import process_pdf_ingestion
from backend.remitos import schemas

router = APIRouter(
    prefix="/remitos",
    tags=["Remitos (Logística)"],
    responses={404: {"description": "Not found"}},
)

@router.post("/ingesta-pdf")
async def ingest_invoice_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    result = await process_pdf_ingestion(file)
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
