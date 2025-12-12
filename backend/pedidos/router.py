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
            subtotal=subtotal
        )
        db.add(nuevo_item)
        
        # Preparar datos para Excel
        items_excel_data.append({
            "Fecha": pedido_data.fecha.strftime("%d/%m/%Y") if pedido_data.fecha else "",
            "Cliente": cliente.razon_social,
            "CUIT": cliente.cuit,
            "Producto": producto.nombre,
            "SKU": producto.sku or "",
            "Cantidad": item.cantidad,
            "Precio Unitario": item.precio_unitario,
            "Subtotal": subtotal,
            "Nota": pedido_data.nota or ""
        })

    # 4. Actualizar Total Header
    nuevo_pedido.total = total_pedido
    db.commit()
    db.refresh(nuevo_pedido)

    # 5. Generar Excel (Pandas)
    if not items_excel_data:
        # Si no hay items, igual devolvemos un excel vacío o con headers
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
    
    # 6. Retornar Archivo
    headers = {
        'Content-Disposition': f'attachment; filename="Pedido_{cliente.razon_social}_{nuevo_pedido.id}.xlsx"'
    }
    return Response(content=output.getvalue(), media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers=headers)
