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
