# backend/facturacion/service.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime
import uuid

from backend.facturacion import models, schemas
from backend.pedidos.models import Pedido
from backend.remitos.models import Remito

class FacturacionService:

    @staticmethod
    def create_draft_from_pedido(db: Session, pedido_id: int) -> models.Factura:
        """
        Genera un borrador de Factura a partir de un Pedido.
        Aplica los descuentos globales de forma proporcional a los ítems para compatibilidad AFIP.
        """
        pedido = db.query(Pedido).options(
            joinedload(Pedido.items),
            joinedload(Pedido.cliente)
        ).filter(Pedido.id == pedido_id).first()
        
        if not pedido:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
            
        # Determinar Tipo de Comprobante
        tipo_comp = "PRESUPUESTO_X"
        if pedido.tipo_facturacion in ["A", "M"]:
            tipo_comp = f"FACTURA_{pedido.tipo_facturacion}"
        elif pedido.tipo_facturacion in ["B", "C", "FISCAL"]:
            tipo_comp = "FACTURA_B" if pedido.cliente.condicion_iva_id else "FACTURA_C"

        factura = models.Factura(
            cliente_id=pedido.cliente_id,
            pedido_id=pedido.id,
            tipo_comprobante=tipo_comp,
            estado="BORRADOR"
        )
        db.add(factura)
        db.flush()
        
        # Lógica de distribución de descuentos:
        # AFIP requiere que cada línea tenga su neto unitario, % de bonificación, y neto total.
        # Si hay un descuento global, en esta versión semiautomática "netemaos" el renglón
        # multiplicándolo por el ratio (neto final / suma de todos los items bruto).
        suma_subtotales = sum(item.subtotal for item in pedido.items)
        neto_base = suma_subtotales - (pedido.descuento_global_importe or 0)
        
        ratio = 1.0
        if suma_subtotales > 0 and (pedido.descuento_global_importe or 0) > 0:
            ratio = neto_base / suma_subtotales
            
        total_neto = 0.0
        total_exento = 0.0
        total_iva_21 = 0.0
        total_iva_105 = 0.0
        
        for p_item in pedido.items:
            # 1. Renglón neto con descuento global aplicado
            subtotal_renglon_neto = p_item.subtotal * ratio
            
            # 2. Determinar IVA
            # Regla de Negocio: Si es "X" no tributa. Si es "A/B" tributa.
            # Idealmente se saca del Producto.alicuota_iva. Asumimos 21% por defecto si tributa.
            alicuota = 21.0
            if tipo_comp.endswith("_X") or tipo_comp.endswith("_C"):
                alicuota = 0.0
                
            # 3. Sumarizadores
            if alicuota > 0:
                total_neto += subtotal_renglon_neto
                if alicuota == 21.0:
                    total_iva_21 += subtotal_renglon_neto * 0.21
                elif alicuota == 10.5:
                    total_iva_105 += subtotal_renglon_neto * 0.105
            else:
                total_exento += subtotal_renglon_neto
                
            # 4. Crear Item de Factura
            f_item = models.FacturaItem(
                factura_id=factura.id,
                pedido_item_id=p_item.id,
                descripcion=p_item.producto.nombre if p_item.producto else (p_item.nota or "Item"),
                cantidad=p_item.cantidad,
                precio_unitario_neto=(subtotal_renglon_neto / p_item.cantidad) if p_item.cantidad > 0 else 0,
                alicuota_iva=alicuota,
                subtotal_neto=subtotal_renglon_neto
            )
            db.add(f_item)
            
        # 5. Cierre de Totales
        factura.neto_gravado = round(total_neto, 2)
        factura.exento = round(total_exento, 2)
        factura.iva_21 = round(total_iva_21, 2)
        factura.iva_105 = round(total_iva_105, 2)
        factura.total = round(total_neto + total_exento + total_iva_21 + total_iva_105, 2)
        
        db.commit()
        db.refresh(factura)
        return factura

    @staticmethod
    def get_factura(db: Session, factura_id: str) -> models.Factura:
        factura = db.query(models.Factura).options(
            joinedload(models.Factura.items),
            joinedload(models.Factura.cliente)
        ).filter(models.Factura.id == uuid.UUID(factura_id)).first()
        if not factura:
            raise HTTPException(status_code=404, detail="Factura no encontrada")
        return factura

    @staticmethod
    def sellar_factura(db: Session, factura_id: str, update_data: schemas.FacturaUpdate) -> models.Factura:
        """
        Asistente de Carga Manual (Fase 1 ARCA).
        Se reciben los datos (CAE, Nro, Vto) tipeados de la página de AFIP y se sella la factura.
        """
        factura = FacturacionService.get_factura(db, factura_id)
        
        if update_data.cae:
            factura.cae = update_data.cae
            factura.estado = "AUTORIZADA_AFIP" # Pasa a estado firme
        
        if update_data.vto_cae:
            factura.vto_cae = update_data.vto_cae
            
        if update_data.punto_venta:
            factura.punto_venta = update_data.punto_venta
            
        if update_data.numero_comprobante:
            factura.numero_comprobante = update_data.numero_comprobante
            
        if update_data.estado and not update_data.cae:
            # Simple state toggle to "LIQUIDADA_MANUAL" prior to CAE insertion or other manual statuses
            factura.estado = update_data.estado

        db.commit()
        db.refresh(factura)
        return factura
