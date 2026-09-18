# backend/facturacion/service.py
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime, timezone
import uuid

from backend.facturacion import models, schemas
from backend.pedidos.models import Pedido
from backend.remitos.models import Remito
from backend.remitos.constants import RemitoFlags

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

        # Sello histórico: CUIT del comprador al momento de facturar (inmutable ante cambios futuros del cliente)
        if pedido.cliente and pedido.cliente.cuit:
            factura.cuit_comprador = pedido.cliente.cuit

        # ARQUITECTURA N:M: El vínculo en facturas_remitos NO se crea aquí.
        # La factura en BORRADOR no tiene remito aún.
        # El vínculo se materializa en RemitosService.create_puente_factura().
        
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

            # Doctrina de Virginidad: CAE real registrado en AFIP → apagar Bit 1 del cliente (irreversible)
            from backend.clientes.constants import ClientFlags
            if factura.cliente and (factura.cliente.flags_estado & ClientFlags.IS_VIRGIN):
                factura.cliente.flags_estado &= ~ClientFlags.IS_VIRGIN
                db.add(factura.cliente)
        
        if update_data.cae_vencimiento:
            factura.cae_vencimiento = update_data.cae_vencimiento
            
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

    @staticmethod
    def anular_factura(db: Session, factura_id: str, payload: schemas.FacturaAnularPayload) -> models.Factura:
        """
        [T4, S868 -- dictamen de Nike] "Facturado -> no facturable" (NC financiera, error de carga,
        "hacéme NC y te lo pago en negro"): la factura se marca ANULADA. El vínculo en
        facturas_remitos NUNCA se borra (trazabilidad) -- con la factura anulada,
        Remito.factura_vinculada ya deja de mostrarla sola (filtra por estado), así que el remito
        "vuelve a pendiente" sin tocar una sola fila de facturas_remitos.

        Además enciende, una sola vez y para siempre, RemitoFlags.REMITO_DESFACTURADO (Bit 41,
        asignado por Nike) en cada remito que estuvo vinculado a esta factura -- la cicatriz que
        distingue "nació no facturable" de "estuvo facturado y se desfacturó".
        """
        factura = FacturacionService.get_factura(db, factura_id)

        if factura.estado == "ANULADA":
            raise HTTPException(status_code=409, detail="La factura ya está anulada.")
        if not payload.motivo.strip():
            raise HTTPException(status_code=400, detail="Falta el motivo de la anulación (nota forense).")

        estado_previo = factura.estado
        factura.estado = "ANULADA"
        nota = f"[ANULADA {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}, era {estado_previo}] {payload.motivo.strip()}"
        factura.notas_auditoria = f"{factura.notas_auditoria}\n{nota}" if factura.notas_auditoria else nota
        db.add(factura)

        remitos_marcados = 0
        for vinculo in factura.vinculos_remitos:
            remito = vinculo.remito
            if remito is None:
                continue
            flags = remito.flags_estado or 0
            if not (flags & int(RemitoFlags.REMITO_DESFACTURADO)):
                remito.flags_estado = flags | int(RemitoFlags.REMITO_DESFACTURADO)
                db.add(remito)
                remitos_marcados += 1

        db.commit()
        db.refresh(factura)
        print(f"[FACTURACION] Factura {factura.id} anulada. Remitos marcados REMITO_DESFACTURADO: {remitos_marcados}")
        return factura
