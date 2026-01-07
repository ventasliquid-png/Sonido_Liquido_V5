from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
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

@router.post("/tactico", status_code=status.HTTP_201_CREATED, response_model=schemas.PedidoResponse)
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
            # [Hardening v6.7] Si es PENDIENTE/PRESUPUESTO y no especifica tipo, asumir 'B' (Final). Si es otro, 'X'.
            tipo_facturacion=pedido_data.tipo_facturacion or ("B" if (pedido_data.estado in ["PENDIENTE", "PRESUPUESTO"]) else "X"),
            origen=pedido_data.origen or "DIRECTO",
            fecha_compromiso=pedido_data.fecha_compromiso,
            descuento_global_porcentaje=pedido_data.descuento_global_porcentaje or 0.0,
            descuento_global_importe=pedido_data.descuento_global_importe or 0.0,
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
            
            # Lógica de Precios V5:
            # Si el usuario mandó un precio, lo respetamos (incluso si es 0).
            # Solo usamos fallback si el precio_unitario es None (aunque el schema lo obliga a float).
            precio_final = item.precio_unitario
            
            # El subtotal ya debe venir calculado del front o se calcula aquí 
            # (mejor recalcular en backend para seguridad).
            # Subtotal = (Precio * Cantidad) - Descuento Importe
            # El descuento importe ya debería ser el absoluto por renglón.
            subtotal = (precio_final * item.cantidad) - (item.descuento_importe or 0.0)
            total_pedido += subtotal
            
            nuevo_item = models.PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad,
                precio_unitario=precio_final,
                descuento_porcentaje=item.descuento_porcentaje or 0.0,
                descuento_importe=item.descuento_importe or 0.0,
                subtotal=subtotal,
                nota="" # Nota por item no está en schema frontend aun
            )
            db.add(nuevo_item)
            
            # Data para Excel
            items_excel_data.append({
                "CANT": item.cantidad,
                "DESCRIPCION": producto.nombre,
                "P.UNIT": precio_final,
                "DTO (%)": item.descuento_porcentaje or 0.0,
                "DTO ($)": item.descuento_importe or 0.0,
                "SUBTOTAL": subtotal
            })

        # 4. Actualizar Total (Restando descuento global y aplicando IVA si corresponde)
        raw_neto = total_pedido - (nuevo_pedido.descuento_global_importe or 0.0)
        
        # Sincronización con Doctrina Táctica v5.6:
        # PENDIENTE/PRESUPUESTO FISCAL (A o B) -> +21% IVA
        # Si es INTERNO o modo 'X', no aplica IVA.
        apply_iva = nuevo_pedido.estado in ["PENDIENTE", "PRESUPUESTO"] and nuevo_pedido.tipo_facturacion in ["A", "B", "FISCAL"]
        
        if apply_iva:
            nuevo_pedido.total = round(raw_neto * 1.21, 2)
        else:
            nuevo_pedido.total = round(raw_neto, 2)

        db.commit()
        db.refresh(nuevo_pedido)
        
        return nuevo_pedido

    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creando pedido: {str(e)}")

def generate_pedido_excel_buffer(pedido, db: Session):
    """
    Helper function to generate Excel buffer for an order.
    """
    cliente = pedido.cliente
    items_excel_data = []
    for item in pedido.items:
        items_excel_data.append({
            "CANT": item.cantidad,
            "DESCRIPCION": item.producto.nombre,
            "P.UNIT": item.precio_unitario,
            "DTO (%)": item.descuento_porcentaje,
            "DTO ($)": item.descuento_importe,
            "SUBTOTAL": item.subtotal
        })

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        workbook = writer.book
        worksheet = workbook.add_worksheet("Pedido")
        
        bold = workbook.add_format({'bold': True})
        money = workbook.add_format({'num_format': '$ #,##0.00'})
        money4 = workbook.add_format({'num_format': '$ #,##0.0000'})
        percent = workbook.add_format({'num_format': '0.00%'})
        
        worksheet.write('A1', f"Pedido # {pedido.id}", bold)
        worksheet.write('A2', f"Fecha: {pedido.fecha}")
        worksheet.write('A3', f"Cliente: {cliente.razon_social}")
        worksheet.write('A4', f"CUIT: {cliente.cuit or 'N/A'}")
        
        if items_excel_data:
            df = pd.DataFrame(items_excel_data)
            worksheet.write_row('A6', df.columns, bold)
            for i, row in enumerate(items_excel_data):
                worksheet.write(6+i, 0, row['CANT'])
                worksheet.write(6+i, 1, row['DESCRIPCION'])
                worksheet.write(6+i, 2, row['P.UNIT'], money4)
                worksheet.write(6+i, 3, row['DTO (%)'] / 100, percent)
                worksheet.write(6+i, 4, row['DTO ($)'], money)
                worksheet.write(6+i, 5, row['SUBTOTAL'], money)

            last_row = 6 + len(items_excel_data)
            
            # Subtotal Bruto (Suma de items con sus descuentos individuales)
            bruto_items = sum(i.subtotal for i in pedido.items)
            
            worksheet.write(last_row+1, 4, "SUBTOTAL BRUTO:", bold)
            worksheet.write(last_row+1, 5, float(bruto_items), money)
            
            curr_row = last_row + 1
            
            # Descuento Global
            if (pedido.descuento_global_importe or 0) > 0:
                curr_row += 1
                worksheet.write(curr_row, 4, f"DTO GLOBAL ({pedido.descuento_global_porcentaje}%):", bold)
                worksheet.write(curr_row, 5, float(pedido.descuento_global_importe), money)
            
            # Neto Gravado (Bruto - Dto Global)
            neto_gravado = bruto_items - (pedido.descuento_global_importe or 0)
            
            # Lógica de IVA v5.6
            if pedido.estado in ["PENDIENTE", "PRESUPUESTO"]:
                iva_val = neto_gravado * 0.21
                
                curr_row += 1
                worksheet.write(curr_row, 4, "NETO GRAVADO:", bold)
                worksheet.write(curr_row, 5, float(neto_gravado), money)
                
                curr_row += 1
                worksheet.write(curr_row, 4, "IVA (21%):", bold)
                worksheet.write(curr_row, 5, float(iva_val), money)
                
                curr_row += 1
                worksheet.write(curr_row, 4, "TOTAL FINAL:", bold)
                worksheet.write(curr_row, 5, float(pedido.total), money) # pedido.total ya tiene el IVA
            else:
                # Caso INTERNO (Sin IVA)
                curr_row += 1
                worksheet.write(curr_row, 4, "TOTAL:", bold)
                worksheet.write(curr_row, 5, float(pedido.total), money)
        else:
            worksheet.write('A6', "Sin ítems")

    buffer.seek(0)
    return buffer

@router.get("/{pedido_id}/excel")
def get_pedido_excel(pedido_id: int, db: Session = Depends(get_db)):
    """
    Exporta un pedido existente a Excel.
    """
    try:
        pedido = db.query(models.Pedido).options(
            joinedload(models.Pedido.cliente),
            joinedload(models.Pedido.items).joinedload(models.PedidoItem.producto)
        ).get(pedido_id)
        
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
            
        buffer = generate_pedido_excel_buffer(pedido, db)
        filename = f"Pedido_{pedido.id}_{pedido.cliente.razon_social[:10]}.xlsx".replace(" ", "_")
        
        return Response(
            content=buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al generar Excel: {str(e)}")

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
        joinedload(models.Pedido.cliente).joinedload(models.Cliente.condicion_iva),
        joinedload(models.Pedido.cliente).joinedload(models.Cliente.segmento),
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




@router.get("/{pedido_id}", response_model=schemas.PedidoResponse)
def get_pedido_by_id(pedido_id: int, db: Session = Depends(get_db)):
    """
    Recupera un pedido específico para edición.
    """
    pedido = (
        db.query(models.Pedido)
        .options(
            joinedload(models.Pedido.cliente).joinedload(models.Cliente.condicion_iva),
            joinedload(models.Pedido.cliente).joinedload(models.Cliente.segmento),
            joinedload(models.Pedido.items).joinedload(models.PedidoItem.producto)
        )
        .filter(models.Pedido.id == pedido_id)
        .first()
    )
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido

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
    
    # [GY-FIX] Recalculate Total if Status, Type, Discounts or ITEMS change
    status_changed = ("estado" in update_data and update_data["estado"] != pedido.estado)
    type_changed = ("tipo_facturacion" in update_data and update_data["tipo_facturacion"] != pedido.tipo_facturacion)
    discounts_changed = ("descuento_global_importe" in update_data or "descuento_global_porcentaje" in update_data)
    items_changed = "items" in update_data
    
    if items_changed:
        # REPLACE ALL ITEMS (Tactical Mode Pattern)
        # 1. Delete old items
        db.query(models.PedidoItem).filter(models.PedidoItem.pedido_id == pedido_id).delete()
        # 2. Insert new ones
        for it in update_data["items"]:
            # Recalculate subtotal for safety
            subtotal = (it['cantidad'] * it['precio_unitario']) - (it.get('descuento_importe') or 0)
            new_item = models.PedidoItem(
                pedido_id=pedido_id,
                producto_id=it['producto_id'],
                cantidad=it['cantidad'],
                precio_unitario=it['precio_unitario'],
                descuento_porcentaje=it.get('descuento_porcentaje') or 0,
                descuento_importe=it.get('descuento_importe') or 0,
                subtotal=subtotal,
                nota=it.get('nota')
            )
            db.add(new_item)
        
        # We need to commit the deletes/inserts now so subsequent sum() works if we don't use the list directly
        db.flush() 
        # Important: clear items from update_data so it doesn't crash on setattr(pedido, 'items', ...)
        del update_data["items"]

    for key, value in update_data.items():
        if key == "tipo_facturacion" and value == "FISCAL":
            value = "B" 
        setattr(pedido, key, value)
    
    if status_changed or type_changed or discounts_changed or items_changed:
        # Recalcular Total según Doctrina Táctica v5.6
        apply_iva = pedido.tipo_facturacion in ["A", "B", "FISCAL", "M"]
        
        # [GY-FIX] Recalcular Total sumando directamente de la DB para evitar stale reads de la relación
        items_neto = db.query(func.sum(models.PedidoItem.subtotal)).filter(models.PedidoItem.pedido_id == pedido_id).scalar() or 0.0
        raw_neto = items_neto - (pedido.descuento_global_importe or 0)
        
        if apply_iva:
            pedido.total = round(raw_neto * 1.21, 2)
        else:
            pedido.total = round(raw_neto, 2)
        
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
    
    # Update Total (Recalculate with IVA logic)
    raw_neto = sum(i.subtotal for i in pedido.items) - (pedido.descuento_global_importe or 0.0)
    if pedido.tipo_facturacion in ["A", "B", "FISCAL", "M"]:
        pedido.total = round(raw_neto * 1.21, 2)
    else:
        pedido.total = round(raw_neto, 2)
    
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
    item.subtotal = (item.cantidad * item.precio_unitario) - (item.descuento_importe or 0)
    
    # Recalculate Order Total
    pedido = item.pedido
    db.flush() # Save item change first
    
    raw_neto = sum(i.subtotal for i in pedido.items) - (pedido.descuento_global_importe or 0)
    if pedido.tipo_facturacion in ["A", "B", "FISCAL", "M"]:
        pedido.total = round(raw_neto * 1.21, 2)
    else:
        pedido.total = round(raw_neto, 2)
    
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
    
    # Recalculate total with IVA logic
    raw_neto = sum(i.subtotal for i in pedido.items) - (pedido.descuento_global_importe or 0.0)
    if pedido.tipo_facturacion in ["A", "B", "FISCAL", "M"]:
        pedido.total = round(raw_neto * 1.21, 2)
    else:
        pedido.total = round(raw_neto, 2)
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
        tipo_facturacion=original.tipo_facturacion or "X",
        origen=original.origen or "DIRECTO",
        total=original.total, # Initial total
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
