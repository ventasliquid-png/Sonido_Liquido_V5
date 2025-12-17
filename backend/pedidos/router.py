from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
import pandas as pd
from io import BytesIO
from fastapi.responses import Response
from datetime import datetime

from backend.core.database import get_db
from backend.pedidos import models, schemas
from backend.clientes.models import Cliente
from backend.productos.models import Producto

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos (Táctico)"],
    responses={404: {"description": "Not found"}},
)

@router.get("/sugerir_id", response_model=int)
def suggest_next_pedido_id(db: Session = Depends(get_db)):
    """
    Devuelve el próximo ID de pedido sugerido (Max ID + 1)
    """
    from sqlalchemy import func
    max_id = db.query(func.max(models.Pedido.id)).scalar()
    return (max_id or 0) + 1

@router.post("/tactico", status_code=status.HTTP_201_CREATED)
def create_pedido_tactico(
    pedido_data: schemas.PedidoCreate, 
    db: Session = Depends(get_db)
):
    """
    Cargador Táctico:
    1. Guarda el pedido en la BD (V5 Clean Data).
    2. Genera un Excel al vuelo y lo devuelve para descargar (Legacy Bridge).
    """
    
    try:
        # 1. Validar Cliente
        cliente = db.query(Cliente).get(pedido_data.cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # 2. Crear Pedido Header
        # Si el usuario mandó un ID manual (simulado en nota o algo), aqui usamos el autoincrement de la BD
        # El "Nro Pedido" manual del frontend por ahora se guarda en la NOTA del header si el usuario lo pone ahi, 
        # o podríamos forzar el ID si la BD lo permitiera (pero es serial).
        # Asumimos que la "sugerencia" del frontend es visual para que coincida con el ID que se va a generar.
        
        nuevo_pedido = models.Pedido(
            cliente_id=pedido_data.cliente_id,
            fecha=pedido_data.fecha,
            nota=pedido_data.nota,
            oc=pedido_data.oc,
            estado=pedido_data.estado or "PENDIENTE",
            tipo_comprobante=pedido_data.tipo_comprobante or "FISCAL",
            total=0.0 # Se calcula abajo
        )
        db.add(nuevo_pedido)
        db.flush() # Para tener ID

        total_pedido = 0.0
        items_excel_data = []

        # 3. Procesar Items
        for item in pedido_data.items:
            producto = db.query(Producto).get(item.producto_id)
            if not producto:
                continue # O raise error?
            
            # Calcular subtotal (Backend confía en precio del front? Por ahora si es táctico, SÍ.
            # Pero idealmente validaríamos. Asumimos que front manda precio correcto o override.)
            # Si precio es 0, usamos el del sistema?
            precio_final = item.precio_unitario
            if precio_final == 0:
                # Fallback simple
               precio_final = getattr(producto, 'precio_mayorista', 0)

            subtotal = precio_final * item.cantidad
            total_pedido += subtotal
            
            nuevo_item = models.PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=precio_final,
                subtotal=subtotal,
                nota="" # Nota por item no está en schema frontend aun
            )
            db.add(nuevo_item)
            
            # Data para Excel
            items_excel_data.append({
                "CANT": item.cantidad,
                "DESCRIPCION": producto.nombre,
                "P.UNIT": precio_final,
                "SUBTOTAL": subtotal
            })

        # 4. Actualizar Total
        nuevo_pedido.total = total_pedido
        db.commit()
        db.refresh(nuevo_pedido)
        
        # 5. Respuesta JSON (Sin Excel)
        return {
            "id": nuevo_pedido.id,
            "cliente": cliente.razon_social,
            "total": total_pedido,
            "items_count": len(items_excel_data),
            "message": "Pedido creado exitosamente (Modo Táctico)"
        }
        """
        # LEGACY EXCEL GENERATION (Disabled by User Request)
        # Crear DataFrame
        # Header data
        buffer = BytesIO()
        
        # Usamos pandas y XlsxWriter
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            workbook = writer.book
            worksheet = workbook.add_worksheet("Pedido")
            
            # Estilos
            bold = workbook.add_format({'bold': True})
            money = workbook.add_format({'num_format': '$ #,##0.00'})
            
            # Encabezado
            worksheet.write('A1', f"Pedido # {nuevo_pedido.id}", bold)
            worksheet.write('A2', f"Fecha: {nuevo_pedido.fecha}")
            worksheet.write('A3', f"Cliente: {cliente.razon_social}")
            worksheet.write('A4', f"CUIT: {cliente.cuit or 'N/A'}")
            
            # Tabla Items
            # Convertir a DF
            if items_excel_data:
                df = pd.DataFrame(items_excel_data)
                # Escribir tabla desde A6
                # Header manual o automatico? Automatico
                worksheet.write_row('A6', df.columns, bold)
                
                for i, row in enumerate(items_excel_data):
                    worksheet.write(6+i, 0, row['CANT'])
                    worksheet.write(6+i, 1, row['DESCRIPCION'])
                    worksheet.write(6+i, 2, row['P.UNIT'], money)
                    worksheet.write(6+i, 3, row['SUBTOTAL'], money)

                # Total
                last_row = 6 + len(items_excel_data)
                worksheet.write(last_row+1, 2, "TOTAL", bold)
                worksheet.write(last_row+1, 3, total_pedido, money)
            else:
                worksheet.write('A6', "Sin items")

        buffer.seek(0)
        
        filename = f"Pedido_{nuevo_pedido.id}_{cliente.razon_social[:10]}.xlsx".replace(" ", "_")
        
        return Response(
            content=buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
        """
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando pedido: {str(e)}")

@router.get("/", response_model=List[schemas.PedidoResponse])
def get_pedidos(
    estado: str = None,
    limit: int = 50, 
    offset: int = 0, 
    db: Session = Depends(get_db)
):
    """
    Lista de Pedidos (Dashboard).
    Permite filtrar por estado.
    """
    q = db.query(models.Pedido)
    if estado:
        q = q.filter(models.Pedido.estado == estado)
    
    # Ordenar por fecha descendente (más nuevos primero)
    q = q.order_by(models.Pedido.fecha.desc(), models.Pedido.id.desc())

    # Eager load cliente and items with products
    q = q.options(
        joinedload(models.Pedido.cliente),
        joinedload(models.Pedido.items).joinedload(models.PedidoItem.producto)
    )
    
    return q.limit(limit).offset(offset).all()

@router.get("/historial/{cliente_id}", response_model=List[schemas.PedidoResponse])
def get_historial_cliente(
    cliente_id: str,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    Últimos 5 pedidos de un cliente (Intelligence Widget).
    """
    """
    Últimos 5 pedidos de un cliente (Intelligence Widget).
    """
    # VECTOR UPDATE: Read directly from Client Cache
    from sqlalchemy import cast, String
    from backend.clientes.models import Cliente
    
    # Robust search for client
    cliente = db.query(Cliente).filter(cast(Cliente.id, String) == str(cliente_id)).first()
    
    if cliente and cliente.historial_cache:
        return cliente.historial_cache
        
    return []



@router.get("/last_price/{cliente_id}/{producto_id}")
def get_ultima_venta(
    cliente_id: str,
    producto_id: int,
    db: Session = Depends(get_db)
):
    """
    Recupera la última vez que un cliente compró un producto.
    Retorna: { precio, fecha, pedido_id, cantidad } o null.
    """
    last_item = (
        db.query(models.PedidoItem)
        .join(models.Pedido)
        .filter(models.Pedido.cliente_id == cliente_id)
        .filter(models.PedidoItem.producto_id == producto_id)
        .order_by(models.Pedido.fecha.desc())
        .first()
    )
    
    if not last_item:
        return None
        
@router.patch("/{pedido_id}", response_model=schemas.PedidoResponse)
def update_pedido(
    pedido_id: int, 
    pedido_update: schemas.PedidoUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza parcialmente un pedido (ej: cambiar estado).
    """
    # Use eager load to return full structure
    pedido = (
        db.query(models.Pedido)
        .options(
            joinedload(models.Pedido.cliente),
            joinedload(models.Pedido.items).joinedload(models.PedidoItem.producto)
        )
        .filter(models.Pedido.id == pedido_id)
        .first()
    )
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    update_data = pedido_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(pedido, key, value)
        
    db.commit()
    db.refresh(pedido)
    return pedido

@router.post("/{pedido_id}/items", response_model=schemas.PedidoResponse)
def add_pedido_item(
    pedido_id: int, 
    item_create: schemas.PedidoItemCreate,
    db: Session = Depends(get_db)
):
    """
    Agrega un item a un pedido existente.
    """
    pedido = db.query(models.Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    producto = db.query(Producto).get(item_create.producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    # Calculate values
    # Use provided price or default to product price
    precio_final = item_create.precio_unitario
    if precio_final == 0:
         precio_final = getattr(producto, 'precio_mayorista', 0)
         
    subtotal = precio_final * item_create.cantidad
    
    new_item = models.PedidoItem(
        pedido_id=pedido.id,
        producto_id=item_create.producto_id,
        cantidad=item_create.cantidad,
        precio_unitario=precio_final,
        subtotal=subtotal,
        nota=item_create.nota or ""
    )
    db.add(new_item)
    
    # Update Total
    pedido.total += subtotal
    
    db.commit()
    
    # Refresh logic to return full PedidoResponse
    return (
        db.query(models.Pedido)
        .options(
            joinedload(models.Pedido.cliente),
            joinedload(models.Pedido.items).joinedload(models.PedidoItem.producto)
        )
        .filter(models.Pedido.id == pedido.id)
        .first()
    )

@router.patch("/items/{item_id}", response_model=schemas.PedidoResponse)
def update_pedido_item(
    item_id: int, 
    item_update: schemas.PedidoItemUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza un item de pedido (cantidad, precio) y recalcula el total del pedido.
    """
    item = db.query(models.PedidoItem).filter(models.PedidoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    # Update fields
    update_data = item_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)
    
    # Recalculate Subtotal
    item.subtotal = item.cantidad * item.precio_unitario
    
    # Recalculate Order Total
    pedido = item.pedido
    db.flush() # Save item change first
    
    new_total = sum(i.cantidad * i.precio_unitario for i in pedido.items)
    pedido.total = new_total
    
    db.commit()
    
    # Refresh to return full PedidoResponse
    return (
        db.query(models.Pedido)
        .options(
            joinedload(models.Pedido.cliente),
            joinedload(models.Pedido.items).joinedload(models.PedidoItem.producto)
        )
        .filter(models.Pedido.id == pedido.id)
        .first()
    )

@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pedido_item(item_id: int, db: Session = Depends(get_db)):
    """
    Elimina un item específico de un pedido.
    """
    item = db.query(models.PedidoItem).filter(models.PedidoItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    # Optional logic: recalculate order total? Or assumes frontend/trigger handles it?
    # For now, let's recalculate total explicitly or assume client will reload.
    # Recalculating is safer.
    pedido = item.pedido
    db.delete(item)
    db.commit()
    
    # Recalculate total
    new_total = sum(i.cantidad * i.precio_unitario for i in pedido.items)
    pedido.total = new_total
    db.commit()
    
    return None

@router.post("/{pedido_id}/clone", response_model=schemas.PedidoResponse)
def clone_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """
    Clona un pedido existente, creando uno nuevo con estado PENDIENTE y fecha actual.
    """
    original = (
        db.query(models.Pedido)
        .options(joinedload(models.Pedido.items))
        .filter(models.Pedido.id == pedido_id)
        .first()
    )
    
    if not original:
        raise HTTPException(status_code=404, detail="Pedido original no encontrado")
        
    new_pedido = models.Pedido(
        cliente_id=original.cliente_id,
        fecha=datetime.now(),
        nota=f"Clonado de Pedido #{original.id}. {original.nota or ''}",
        oc=original.oc,
        estado="BORRADOR",
        tipo_comprobante=original.tipo_comprobante or "FISCAL",
        total=original.total, # Initial total, assuming prices same. Ideally should fetch current prices but clone usually implies exact copy first.
    )
    db.add(new_pedido)
    db.flush() # get ID
    
    for item in original.items:
        new_item = models.PedidoItem(
            pedido_id=new_pedido.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario
        )
        db.add(new_item)
        
    db.commit()
    
    # Refresh to load relations for response
    return (
        db.query(models.Pedido)
        .options(
            joinedload(models.Pedido.cliente),
            joinedload(models.Pedido.items).joinedload(models.PedidoItem.producto)
        )
        .filter(models.Pedido.id == new_pedido.id)
        .first()
    )

@router.delete("/{pedido_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """
    Eliminación física de un pedido (Sólo Admin/Corrección).
    Elimina también los items en cascada.
    """
    pedido = db.query(models.Pedido).get(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    db.delete(pedido)
    db.commit()
    return None

# --- MOTOR DE PRECIOS V5 ENDPOINTS ---
from backend.pedidos.pricing import PricingEngine
from pydantic import BaseModel

class CotizacionRequest(BaseModel):
    cliente_id: str
    producto_id: int
    cantidad: float = 1.0

@router.post("/cotizar")
def cotizar_precio(req: CotizacionRequest, db: Session = Depends(get_db)):
    """
    Endpoint Táctico: Cotiza un producto para un cliente específico
    usando la lógica 'La Roca y La Máscara'.
    """
    engine = PricingEngine(db)
    resultado = engine.cotizar_producto(req.cliente_id, req.producto_id, req.cantidad)
    return resultado
