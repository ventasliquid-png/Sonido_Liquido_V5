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

    # ------------------------------------------------------------------ [Etapa 7d] NC / ND
    # Dictamen Nike 29/09 (BIBLIOTECA_NIKE.md, Módulo 2, "¿Cómo se modela NC/ND...?"): misma tabla
    # `facturas` por tipo_comprobante + tabla puente `facturas_ajustes` + bits 17-20 mantenidos acá.

    @staticmethod
    def sincronizar_bits_ajuste(db: Session, factura: models.Factura) -> None:
        """Recalcula ES_NC/ES_ND/TIENE_NC/TIENE_ND de UNA factura desde los datos reales.

        No es un "prender/apagar" a ciegas: cada llamada mira facturas_ajustes y el tipo, así que no
        puede desincronizarse (la lección de los Bits 20/21 de Pedido, cachés de una resta que se
        rompieron). Una NC/ND ANULADA no cuenta como ajuste vigente. No hace commit."""
        from backend.facturacion.constants import FacturaFlags, es_nota_credito, es_nota_debito

        db.flush()

        def hay_ajuste(prefijo: str) -> bool:
            return db.query(models.FacturaAjuste.id).join(
                models.Factura, models.FacturaAjuste.factura_nc_nd_id == models.Factura.id
            ).filter(
                models.FacturaAjuste.factura_ajustada_id == factura.id,
                models.Factura.estado != "ANULADA",
                models.Factura.tipo_comprobante.like(f"{prefijo}%"),
            ).first() is not None

        quiere = {
            FacturaFlags.ES_NC: es_nota_credito(factura.tipo_comprobante),
            FacturaFlags.ES_ND: es_nota_debito(factura.tipo_comprobante),
            FacturaFlags.TIENE_NC: hay_ajuste("NOTA_CREDITO"),
            FacturaFlags.TIENE_ND: hay_ajuste("NOTA_DEBITO"),
        }
        flags = factura.flags_estado or 0
        for bit, encendido in quiere.items():
            flags = (flags | bit) if encendido else (flags & ~bit)
        if flags != factura.flags_estado:
            # Sin db.add(): la factura ya es persistente en esta sesión, y un add() cascadea por las
            # colecciones de ajustes, que pueden tener filas ya borradas (revertir_ajuste).
            factura.flags_estado = flags

    @staticmethod
    def registrar_ajuste(
        db: Session,
        nc_nd: models.Factura,
        ajustadas: Optional[List[dict]] = None,
    ) -> List[models.FacturaAjuste]:
        """Vincula una NC/ND con las facturas que ajusta y enciende los bits. No hace commit.

        `ajustadas`: [{"factura_id": <uuid|str>, "monto_aplicado": float|None}, ...].
        - NC: al menos una factura (una NC sin comprobante asociado no tiene qué ajustar).
        - ND: puede ir SUELTA (lista vacía): intereses por mora, gastos bancarios -- queda una fila con
          factura_ajustada_id NULL, atribuida solo al cliente de la propia ND (Nike, punto 5).
        Una factura ajustada no puede ser otra NC, ni estar anulada, ni ser de otro cliente."""
        from backend.facturacion.constants import es_nota_credito, es_nota_debito

        ajustadas = ajustadas or []
        if not (es_nota_credito(nc_nd.tipo_comprobante) or es_nota_debito(nc_nd.tipo_comprobante)):
            raise HTTPException(
                status_code=409,
                detail=f"AJUSTE_TIPO_INVALIDO: {nc_nd.tipo_comprobante} no es una nota de crédito ni de débito.")
        if es_nota_credito(nc_nd.tipo_comprobante) and not ajustadas:
            raise HTTPException(
                status_code=409,
                detail="NC_SIN_FACTURA: una nota de crédito tiene que ajustar al menos una factura "
                       "(solo la nota de débito puede ir suelta).")

        creadas: List[models.FacturaAjuste] = []
        vistas = set()
        objetivos = []
        for a in ajustadas:
            try:
                fid = a["factura_id"] if isinstance(a["factura_id"], uuid.UUID) else uuid.UUID(str(a["factura_id"]))
            except (ValueError, KeyError):
                raise HTTPException(status_code=409, detail=f"AJUSTADA_INEXISTENTE: id inválido {a.get('factura_id')!r}.")
            if fid in vistas:
                raise HTTPException(status_code=409, detail=f"AJUSTE_DUPLICADO: la factura {fid} está repetida.")
            vistas.add(fid)
            destino = db.query(models.Factura).filter(models.Factura.id == fid).first()
            if destino is None:
                raise HTTPException(status_code=409, detail=f"AJUSTADA_INEXISTENTE: no existe la factura {fid}.")
            if destino.id == nc_nd.id:
                raise HTTPException(status_code=409, detail="AJUSTADA_ES_LA_MISMA: un comprobante no se ajusta a sí mismo.")
            if es_nota_credito(destino.tipo_comprobante):
                raise HTTPException(
                    status_code=409,
                    detail=f"AJUSTADA_ES_NC: {destino.tipo_comprobante} {destino.numero_completo} es una nota de crédito.")
            if destino.estado == "ANULADA":
                raise HTTPException(status_code=409, detail=f"AJUSTADA_ANULADA: {destino.numero_completo} está anulada.")
            if destino.cliente_id != nc_nd.cliente_id:
                raise HTTPException(
                    status_code=409,
                    detail=f"CLIENTE_DISTINTO: {destino.numero_completo} es de otro cliente que la nota.")
            if db.query(models.FacturaAjuste.id).filter(
                models.FacturaAjuste.factura_nc_nd_id == nc_nd.id,
                models.FacturaAjuste.factura_ajustada_id == destino.id,
            ).first():
                raise HTTPException(status_code=409, detail=f"AJUSTE_DUPLICADO: ya existe el vínculo con {destino.numero_completo}.")
            objetivos.append((destino, a.get("monto_aplicado")))

        if not objetivos:  # ND suelta
            objetivos = [(None, None)]

        for destino, monto in objetivos:
            fila = models.FacturaAjuste(
                factura_nc_nd_id=nc_nd.id,
                factura_ajustada_id=destino.id if destino is not None else None,
                monto_aplicado=monto,
            )
            db.add(fila)
            creadas.append(fila)
        db.flush()
        # Las filas se crearon por FK, no por la relación: las colecciones ya cargadas quedaron viejas.
        db.expire(nc_nd, ["ajustes_emitidos"])
        for destino, _ in objetivos:
            if destino is not None:
                db.expire(destino, ["ajustes_recibidos"])

        FacturacionService.sincronizar_bits_ajuste(db, nc_nd)
        for destino, _ in objetivos:
            if destino is not None:
                FacturacionService.sincronizar_bits_ajuste(db, destino)
        return creadas

    @staticmethod
    def revertir_ajuste(db: Session, ajuste_id: int) -> None:
        """Deshace un vínculo NC/ND -> factura y recalcula los bits de las dos puntas. No hace commit.
        ES_NC/ES_ND de la nota NO se apagan: sigue siendo una nota aunque ya no ajuste nada."""
        fila = db.query(models.FacturaAjuste).filter(models.FacturaAjuste.id == ajuste_id).first()
        if fila is None:
            raise HTTPException(status_code=404, detail="Ajuste no encontrado")
        nc_nd = fila.nc_nd
        ajustada = fila.ajustada
        db.delete(fila)
        db.flush()
        db.expire(nc_nd, ["ajustes_emitidos"])
        if ajustada is not None:
            db.expire(ajustada, ["ajustes_recibidos"])
        FacturacionService.sincronizar_bits_ajuste(db, nc_nd)
        if ajustada is not None:
            FacturacionService.sincronizar_bits_ajuste(db, ajustada)

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
