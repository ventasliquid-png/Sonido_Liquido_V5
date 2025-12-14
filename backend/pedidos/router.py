from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
from io import BytesIO
from fastapi.responses import Response

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
            continue # O lanzar error, pero en táctico mejor omitir y seguir
            
        subtotal = item.cantidad * item.precio_unitario
        total_pedido += subtotal
        
        # Guardar Item BD
        nuevo_item = models.PedidoItem(
            pedido_id=nuevo_pedido.id,
            producto_id=item.producto_id,
            cantidad=item.cantidad,
            precio_unitario=item.precio_unitario,
            subtotal=subtotal,
            nota=item.nota
        )
        db.add(nuevo_item)
        
        # Preparar datos para Excel
        items_excel_data.append({
            "Fecha": pedido_data.fecha.strftime("%d/%m/%Y") if pedido_data.fecha else "",
            "Pedido Nro": nuevo_pedido.id, # Usamos el ID real de la BD
            "Cliente": cliente.razon_social,
            "CUIT": cliente.cuit,
            "Producto": producto.nombre,
            "SKU": producto.sku or "",
            "Cantidad": item.cantidad,
            "Precio Unitario": item.precio_unitario,
            "Subtotal": subtotal,
            "Notas Item": item.nota or "",
            "Nota Pedido": pedido_data.nota or ""
        })

    # 4. Actualizar Total Header
    nuevo_pedido.total = total_pedido
    db.commit()
    db.refresh(nuevo_pedido)

    # 5. Generar Excel (Pandas)
    if not items_excel_data:
        items_excel_data = [{"Nota": "Pedido sin items validos"}]

    df = pd.DataFrame(items_excel_data)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Pedido')
        # Auto-adjust column width (Basic)
        worksheet = writer.sheets['Pedido']
        for column_cells in worksheet.columns:
            length = max(len(str(cell.value)) for cell in column_cells)
            worksheet.column_dimensions[column_cells[0].column_letter].width = length + 2
    
    output.seek(0)
    
    # Filename
    filename = f"Pedido_{nuevo_pedido.id}_{cliente.razon_social[:10]}.xlsx".replace(" ", "_")
    
    return Response(
        content=output.getvalue(),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )

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
    return db.query(models.Pedido)\
        .filter(models.Pedido.cliente_id == cliente_id)\
        .order_by(models.Pedido.fecha.desc())\
        .limit(limit)\
        .all()



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
        
    return {
        "precio": last_item.precio_unitario,
        "cantidad": last_item.cantidad,
        "fecha": last_item.pedido.fecha,
        "pedido_id": last_item.pedido_id
    }
