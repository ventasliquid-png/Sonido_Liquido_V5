from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.cantera.service import CanteraService
from backend.clientes.service import ClienteService
from backend.clientes.schemas import ClienteCreate, ClienteResponse, DomicilioCreate
from backend.productos import models, schemas




router = APIRouter(
    prefix="/bridge",
    tags=["Cantera (Maestros)"],
)

@router.get("/clientes/search")
def search_clientes_cantera(q: str = Query(..., min_length=2)):
    return CanteraService.search_clientes(q)

@router.get("/clientes")
def list_clientes_cantera(limit: int = 100, offset: int = 0):
    return CanteraService.get_clientes(limit, offset)

@router.get("/productos/search")
def search_productos_cantera(q: str = Query(..., min_length=2)):
    return CanteraService.search_productos(q)

@router.get("/productos")
def list_productos_cantera(limit: int = 100, offset: int = 0):
    return CanteraService.get_productos(limit, offset)

@router.get("/productos/{producto_id}/details")
def get_producto_details_cantera(producto_id: str):
    """Retorna los datos completos del JSON sin importar nada a la DB operativa."""
    data = CanteraService.get_full_product_data(producto_id)
    if not data:
        raise HTTPException(status_code=404, detail="Producto no encontrado en Cantera")
    return data

@router.post("/clientes/{cliente_id}/import")
def import_cliente_from_cantera(cliente_id: str, db: Session = Depends(get_db)):
    full_data = CanteraService.get_full_client_data(cliente_id)
    if not full_data:
        raise HTTPException(status_code=404, detail="Cliente no encontrado en Cantera")
    
    try:
        # [GY-FIX V5.6.12] Importar también el domicilio principal
        domicilios_in = []
        
        # Mapeo de campos legacy (ajustar según JSON real de Cantera)
        calle = full_data.get("domicilio") or full_data.get("calle")
        localidad = full_data.get("ciudad") or full_data.get("localidad")
        if calle:
            new_dom = DomicilioCreate(
                calle=calle,
                numero=str(full_data.get("numero") or "S/N"),
                localidad=localidad,
                cp=str(full_data.get("cp") or ""),
                es_fiscal=True,  # Default to Fiscal for immediate use
                es_entrega=True,
                activo=True,
                alias="Domicilio Importado"
            )
            domicilios_in.append(new_dom)

        razon_social = full_data.get("razon_social") or "CLIENTE IMPORTADO"
        cuit = full_data.get("cuit") or "00000000000"
        
        cliente_in = ClienteCreate(
            razon_social=razon_social,
            cuit=cuit,
            activo=full_data.get("activo", 1),
            domicilios=domicilios_in
        )
        new_client = ClienteService.create_cliente(db, cliente_in)
        db.flush()
        
        # [GY-FIX] Re-obtener el cliente completo para validación y retorno
        full_client = ClienteService.get_cliente(db, new_client.id)
        if not full_client:
             raise Exception("Error al recuperar el cliente recién creado")
             
        print(f"[CANTERA-IMPORT] Éxito importando {new_client.id}")
        
        return {
            "status": "success", 
            "imported_id": str(new_client.id),
            "cliente": ClienteResponse.model_validate(full_client)
        }
    except Exception as e:
        db.rollback()
        print(f"[CANTERA-IMPORT] Error crítico: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/productos/{producto_id}/import")
def import_producto_from_cantera(producto_id: str, db: Session = Depends(get_db)):
    full_data = CanteraService.get_full_product_data(producto_id)
    if not full_data:
        raise HTTPException(status_code=404, detail="Producto no encontrado en Cantera")
    
    try:
        # 1. Verificar Rubro
        rubro_id = full_data.get("rubro_id")
        if rubro_id:
            db_rubro = db.query(models.Rubro).get(rubro_id)
            if not db_rubro:
                # Importar Rubro desde Cantera
                rubro_data = CanteraService.get_full_rubro_data(rubro_id)
                if rubro_data:
                    new_rubro = models.Rubro(
                        id=rubro_id,
                        nombre=rubro_data.get("nombre"),
                        codigo=str(rubro_id), # Placeholder
                        activo=1
                    )
                    db.add(new_rubro)
                    db.commit()
        
        # 2. Crear Producto
        # Mapeamos SKU a un tipo compatible (el mirror lo tiene como float/int)
        sku_val = full_data.get("sku")
        
        new_prod = models.Producto(
            id=int(producto_id),
            sku=str(sku_val) if sku_val else None,
            nombre=full_data.get("nombre"),
            rubro_id=rubro_id,
            activo=1
        )
        db.add(new_prod)
        
        # 3. Crear Costos base (evita 500 en el front)
        db.flush() # Para tener el id si fuera autoincremental
        from decimal import Decimal
        new_costo = models.ProductoCosto(
            producto_id=new_prod.id,
            costo_reposicion=Decimal("0.00"),
            margen_mayorista=Decimal("0.00"),
            iva_alicuota=Decimal("21.00")
        )
        db.add(new_costo)
        
        # [FIX V5.6.1] Logistics Defaults
        new_prod.unidades_bulto = 1.0
        new_prod.presentacion_compra = "Unidad"
        
        db.commit()
        
        # [FIX V5.6.1] Return full structure for GridLoader
        return {
            "status": "success", 
            "imported_id": str(new_prod.id),
            "id": new_prod.id,
            "descripcion": new_prod.nombre,
            "precio_unitario": 0.00,
            "alicuota_iva": 21.00, # Defaulting to 21%
            "unidad_venta": "UN" # Defaulting to UN
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error importing product: {str(e)}")

@router.post("/clientes/{cliente_id}/inactivate")
def inactivate_cliente_cantera(cliente_id: str):
    try:
        CanteraService.inactivate_client(cliente_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/productos/{producto_id}/inactivate")
def inactivate_producto_cantera(producto_id: str):
    try:
        CanteraService.inactivate_product(producto_id)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
