from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.remitos import schemas, models
from backend.clientes.models import Cliente, Domicilio
from backend.productos.models import Producto
from backend.pedidos.models import Pedido, PedidoItem
from backend.logistica.models import EmpresaTransporte
# [GY-FIX] Import Vinculo to avoid Registry Error during potential implicit loads
import os

# [V5] Base Dirs for relative referencing
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # .../backend/remitos/
BACKEND_DIR = os.path.dirname(BASE_DIR)              # .../backend/
ROOT_DIR = os.path.dirname(BACKEND_DIR)              # .../ (Raiz)

class RemitosService:
    
    @staticmethod
    def create_from_ingestion(db: Session, payload: schemas.IngestionPayload):
        """
        Creates a Pedido and Remito from PDF Ingestion Data.
        """
        # 1. FIND CLIENT
        cliente = db.query(Cliente).filter(Cliente.cuit == payload.cliente.cuit).first()
        
        if not cliente and payload.cliente.cuit:
             # Try stripping dashes if any
             clean_cuit = payload.cliente.cuit.replace("-", "")
             cliente = db.query(Cliente).filter(Cliente.cuit == clean_cuit).first()
             
        if not cliente:
            # DOCTRINA DE MIEMBRO PLENO: NO crear el cliente mágicamente.
            # Devolver señal al frontend para abrir ABM con los datos de ARCA/Sabueso.
            calle_extra = getattr(payload.cliente, 'direccion', None) or getattr(payload.cliente, 'calle', None) or ""
            raise ValueError(f"CLIENT_NOT_FOUND||{payload.cliente.cuit}||{payload.cliente.razon_social}||{calle_extra}")
        
        # DOCTRINA DE MIEMBRO PLENO: Check Estado 15 (Faltan datos críticos) vs Estado 13 (Pleno)
        # Un cliente no es pleno si le falta Lista de Precios o Segmento
        if not getattr(cliente, 'lista_precios_id', None) or not getattr(cliente, 'segmento_id', None):
             raise ValueError(f"CLIENT_NOT_PLENO||{cliente.id}||El cliente {cliente.razon_social} existe pero está incompleto (falta Lista de Precios o Segmento). Abra el ABM para completarlo.")
             
        # 2. RESOLVE LOGISTICS
        domicilio = next((d for d in getattr(cliente, 'domicilios', []) if getattr(d, 'activo', True)), None)
        if not domicilio:
            # Fallback to first address in DB or error
            domicilio = db.query(Domicilio).first() # Dangerous but keeps flow moving
            
        # Default Transport
        transporte = db.query(EmpresaTransporte).first()
        transporte_id = transporte.id if transporte else None

        # 3. CREATE PEDIDO
        # We assume "PENDIENTE" state validation will happen in V5 logic
        nuevo_pedido = Pedido(
            cliente_id=cliente.id,
            fecha=datetime.now(),
            nota=f"Ingesta Automática Factura: {payload.factura.numero or 'S/N'}",
            estado="PENDIENTE",
            origen="INGESTA_PDF",
            domicilio_entrega_id=domicilio.id if domicilio else None,
            transporte_id=transporte_id
        )
        db.add(nuevo_pedido)
        db.flush()

        # 4. RESOLVE ITEMS
        # Find Generic Product for fallback
        prod_generico = db.query(Producto).filter(Producto.nombre.ilike("%VARIOS%")).first()
        if not prod_generico:
             prod_generico = db.query(Producto).filter(Producto.activo == True).first()

        pedido_items = []
        for item in payload.items:
            # Fuzzy Logic could go here. For now, try exact match on description or clean description
            # Since PDF Descriptions might be dirty, we rely on "VARIOS" mostly unless we have code mapping
            
            producto = None
            # If we had a code, we'd search by code.
            
            # Simple Description Match
            producto = db.query(Producto).filter(Producto.nombre.ilike(f"%{item.descripcion}%")).first()
            
            nota_item = ""
            prod_id = prod_generico.id
            
            if producto:
                prod_id = producto.id
            else:
                nota_item = item.descripcion # Store original description
                
            new_p_item = PedidoItem(
                pedido_id=nuevo_pedido.id,
                producto_id=prod_id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario or 0.0,
                nota=nota_item
            )
            db.add(new_p_item)
            db.flush() 
            pedido_items.append(new_p_item)

        # 5. CREATE REMITO
        vto_cae_date = None
        if payload.factura.vto_cae:
            try:
                # Try common formats
                vto_cae_date = datetime.strptime(payload.factura.vto_cae, "%d/%m/%Y")
            except:
                pass
        
        # Internal Number Logic
        numero_legal = f"R-{str(nuevo_pedido.id).zfill(8)}"

        remito = models.Remito(
            pedido_id=nuevo_pedido.id,
            domicilio_entrega_id=domicilio.id if domicilio else None,
            transporte_id=transporte_id,
            estado="BORRADOR",
            aprobado_para_despacho=True,
            cae=payload.factura.cae,
            vto_cae=vto_cae_date,
            numero_legal=numero_legal
        )
        db.add(remito)
        db.flush()

        # 6. CREATE REMITO ITEMS
        for p_item in pedido_items:
            r_item = models.RemitoItem(
                remito_id=remito.id,
                pedido_item_id=p_item.id,
                cantidad=p_item.cantidad
            )
            db.add(r_item)
            
        # 7. [V14 GENOMA] EVO: Desactivar Virginidad (Bit 1) del Cliente
        # Si el cliente ya tenía movimientos, el bit ya es 0. 
        # Si era Virgen (Bit 1 = 1), ahora deja de serlo.
        from backend.clientes.constants import ClientFlags
        
        # Sincronizar Flags
        # 1. Asegurar Existencia (Bit 0)
        # 2. Desactivar Virginidad (Evolución Natural)
        # Bitwise: flag &= ~2 (Apaga Bit 1)
        # Aseguramos V14 Struct (Bit 3) si es nuevo
        
        current_flags = cliente.flags_estado or 0
        new_flags = (current_flags | ClientFlags.EXISTENCE | ClientFlags.V14_STRUCT) & ~ClientFlags.VIRGINITY
        
        if current_flags != new_flags:
            cliente.flags_estado = new_flags
            db.add(cliente)
            print(f"Genoma EVO: Cliente {cliente.razon_social} evolucionó a Flag {new_flags} (Activo)")

        db.commit()
        db.refresh(remito)
        
        # 8. [V5-AUTO] Generar PDF Físico
        try:
            from .remito_engine import generar_remito_pdf
            
            # Preparar datos para el motor
            cliente_data = {
                "razon_social": cliente.razon_social,
                "cuit": cliente.cuit,
                "domicilio_fiscal": domicilio.calle if domicilio else "",
                "condicion_iva": cliente.condicion_iva or "Consumidor Final",
                "factura_vinculada": payload.factura.numero,
                "cae": payload.factura.cae,
                "vto_cae": payload.factura.vto_cae
            }
            
            items_data = []
            for item in payload.items:
                items_data.append({
                    "descripcion": item.descripcion,
                    "cantidad": item.cantidad,
                    "unidad": "UN",
                    "codigo": item.codigo or "S/N"
                })
            
            # Guardar en static/remitos
            static_dir = os.path.join(ROOT_DIR, "static", "remitos")
            os.makedirs(static_dir, exist_ok=True)
            
            filename = f"REMITO_{remito.numero_legal.replace('-', '_')}.pdf"
            pdf_path = os.path.join(static_dir, filename)
            
            
            generar_remito_pdf(cliente_data, items_data, is_preview=False, output_path=pdf_path, numero_remito=remito.numero_legal)
            print(f"Genoma PDF: Remito físico generado en {pdf_path}")
            
            # 9. Set URL para retorno (Relative to SPA)
            remito.pdf_url = f"/static-remitos/{filename}"
            
        except Exception as pdf_err:
            print(f"[X] Error generando PDF automático: {pdf_err}")
            # No bloqueamos el commit principal por un error de PDF
            
        return remito
