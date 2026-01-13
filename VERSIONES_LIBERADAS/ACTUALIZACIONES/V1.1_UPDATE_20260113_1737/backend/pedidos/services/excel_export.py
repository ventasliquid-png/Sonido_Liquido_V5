import pandas as pd
from io import BytesIO
from sqlalchemy.orm import Session
from backend.pedidos.models import Pedido, PedidoItem
from backend.clientes.models import Cliente, Domicilio
from backend.maestros.models import Vendedor
from datetime import datetime

class ExcelExportService:
    def generate_orders_excel(self, db: Session) -> BytesIO:
        """
        Genera un archivo Excel con dos hojas:
        1. Pedidos (Cabeceras)
        2. Items (Detalle)
        """
        
        # 1. Fetch Data
        pedidos = db.query(Pedido).filter(Pedido.activo == True).all()
        
        # 2. Prepare Data for Headers
        headers_data = []
        items_data = []
        
        for p in pedidos:
            # Flatten Header Info
            cliente_rs = p.cliente.razon_social if p.cliente else "N/A"
            cliente_cuit = p.cliente.cuit if p.cliente else "N/A"
            vendedor_nombre = p.vendedor.nombre if p.vendedor else "N/A"
            
            headers_data.append({
                "ID Pedido": p.id,
                "Fecha": p.fecha_emision,
                "Cliente": cliente_rs,
                "CUIT": cliente_cuit,
                "Vendedor": vendedor_nombre,
                "Estado": p.estado,
                "Total Neto": p.total_neto,
                "Total IVA": p.total_iva,
                "Total General": p.total_general,
                "Condición Pago": p.condicion_pago,
                "Logística": p.tipo_entrega,
                "Observaciones": p.observaciones,
                "Creado Por": p.usuario_creador
            })
            
            # Flatten Items Info
            for item in p.items:
                items_data.append({
                    "ID Pedido": p.id,
                    "SKU": item.producto_id, # Asumimos ID como SKU por ahora
                    "Producto": item.descripcion_producto, # O cargar nombre si no está denormalizado
                    "Cantidad": item.cantidad,
                    "Precio Unit.": item.precio_unitario,
                    "IVA %": item.tasa_iva,
                    "Subtotal": item.subtotal
                })
                
        # 3. Create DataFrame
        df_headers = pd.DataFrame(headers_data)
        df_items = pd.DataFrame(items_data)
        
        # 4. Write to Excel Buffer
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_headers.to_excel(writer, sheet_name='Pedidos', index=False)
            df_items.to_excel(writer, sheet_name='Detalle Items', index=False)
            
            # Auto-adjust columns width (Basic)
            for sheet in writer.sheets.values():
                for column in sheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = (max_length + 2) * 1.2
                    sheet.column_dimensions[column_letter].width = adjusted_width

        output.seek(0)
        return output
