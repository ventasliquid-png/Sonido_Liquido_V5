
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.remitos.pdf_parser import parse_afip_pdf_offline
from backend.remitos import schemas
import traceback

router = APIRouter(
    prefix="/remitos",
    tags=["Remitos (Logística)"],
    responses={404: {"description": "Not found"}},
)

@router.post("/ingesta-pdf")
async def ingest_invoice_pdf(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF válido.")
    
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="El archivo PDF está vacío.")
            
        # 1. Sabueso Soberano (Fase 0 y Fase 1)
        result = parse_afip_pdf_offline(content)
        
        # 2. Manejo Estricto de Errores
        if not result.get("cuit"):
            raise HTTPException(
                status_code=422, 
                detail="No se detectó CUIT de cliente en el PDF. Asegúrese de que sea una factura de Receptor válida."
            )
        if not result.get("cae"):
            raise HTTPException(
                status_code=422, 
                detail="No se detectó CAE en el PDF. El documento carece de validez fiscal."
            )
            
        # 3. Doctrina de Miembro Pleno (Pre-Vuelo FrontEnd)
        from backend.clientes.models import Cliente
        cuit_raw = result.get("cuit")
        cuit_limpio = cuit_raw.replace("-", "") if cuit_raw else None
        
        estado_cliente = "NUEVO"
        razon_social = result.get("razon_social") or "Consumidor Final"

        if cuit_limpio:
            cliente = db.query(Cliente).filter(Cliente.cuit == cuit_limpio).first()
            if not cliente and cuit_raw:
                cliente = db.query(Cliente).filter(Cliente.cuit == cuit_raw).first()

            if cliente:
                razon_social = cliente.razon_social
                es_pleno = bool(cliente.lista_precios_id and cliente.segmento_id)
                estado_cliente = "PLENO" if es_pleno else "INCOMPLETO"

        # 4. Preparación de la "Tríada de Control"
        parsed_data = {
            "cliente": {
                "id": str(cliente.id) if cliente else None,
                "cuit": cuit_raw,
                "razon_social": razon_social,
                "direccion": result.get("direccion", ""),
                "condicion_iva": result.get("condicion_iva", ""),
                "estado_db": estado_cliente
            },
            "factura": {
                "numero": result.get("numero", "S/N"),
                "cae": result.get("cae"),
                "vto_cae": result.get("vto_cae")
            },
            "items": result.get("items", [])
        }
        
        return {
            "success": True,
            "data": parsed_data
        }
        
    except ValueError as ve:
        # Errores del parser pikepdf o regex malformado
        raise HTTPException(status_code=422, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error procesando PDF (Sabueso): {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno del servidor PDF: {str(e)}")

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
        error_msg = str(ve)
        # Parse custom business markers
        if error_msg.startswith("CLIENT_NOT_FOUND") or error_msg.startswith("CLIENT_NOT_PLENO"):
            raise HTTPException(status_code=422, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        print(f"Error creating Remito from Ingestion: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
