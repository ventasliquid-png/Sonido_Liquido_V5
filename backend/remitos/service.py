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
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        """
        Retorna la lista de remitos con información cruzada del cliente para la grilla.
        """
        remitos = db.query(models.Remito).order_by(models.Remito.fecha_creacion.desc()).offset(skip).limit(limit).all()
        
        resultado = []
        for r in remitos:
            # We need client info, Remito -> Pedido -> Cliente
            cliente_nombre = "Desconocido"
            cliente_cuit = "-"
            
            if r.pedido and r.pedido.cliente:
                cliente_nombre = r.pedido.cliente.razon_social
                cliente_cuit = r.pedido.cliente.cuit or "S/N"
                
            resultado.append({
                "id": str(r.id),
                "numero_legal": r.numero_legal,
                "fecha_creacion": r.fecha_creacion,
                "estado": r.estado,
                "pdf_url": r.pdf_url,
                "cliente_razon_social": cliente_nombre,
                "cliente_cuit": cliente_cuit
            })
        return resultado

    @staticmethod
    def delete_remito(db: Session, remito_id: str):
        """
        Elimina un remito y opcionalmente limpia el PDF físico si existe.
        """
        remito = db.query(models.Remito).filter(models.Remito.id == remito_id).first()
        if not remito:
            raise ValueError("Remito no encontrado")
            
        # Intentar borrar PDF físico
        if remito.pdf_url:
            filename = remito.pdf_url.split('/')[-1]
            pdf_path = os.path.join(ROOT_DIR, "static", "remitos", filename)
            if os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except Exception as e:
                    print(f"Sabueso Trace: No se pudo borrar el PDF físico {pdf_path}: {e}")
                    
        db.delete(remito)
        db.commit()
        return True

    @staticmethod
    def create_from_ingestion(db: Session, payload: schemas.IngestionPayload):
        """
        Creates a Pedido and Remito from PDF Ingestion Data.
        """
        # 1. FIND CLIENT
        # [GY-FIX-V14] Robust Numeric-only CUIT cleaning
        import re
        c_raw = payload.cliente.cuit or ""
        c_clean = re.sub(r'[^0-9]', '', c_raw)
        
        print(f"Sabueso Trace: Searching for CUIT {c_clean} (Original: {c_raw})")
        
        cliente = db.query(Cliente).filter(Cliente.cuit == c_clean).first()
        
        if not cliente and c_raw:
             # Fallback to search by raw text if cleaning was too aggressive or DB is legacy
             cliente = db.query(Cliente).filter(Cliente.cuit == c_raw).first()
             
        if not cliente:
            print(f"Sabueso Trace: Client NOT FOUND for {c_clean}")
            calle_extra = getattr(payload.cliente, 'direccion', None) or getattr(payload.cliente, 'calle', None) or ""
            raise ValueError(f"CLIENT_NOT_FOUND||{payload.cliente.cuit}||{payload.cliente.razon_social}||{calle_extra}")
        
        # [NEW] Check for inactive client
        if not cliente.activo:
             # Carlos requested a warning. We raise a specific error so frontend can ask.
             raise ValueError(f"CLIENT_INACTIVE||{cliente.id}||{cliente.razon_social}")

        # DOCTRINA DE MIEMBRO PLENO: Check Estado 15 (Faltan datos críticos) vs Estado 13 (Pleno)
        # Un cliente no es pleno si le falta Lista de Precios o Segmento
        if not getattr(cliente, 'lista_precios_id', None) or not getattr(cliente, 'segmento_id', None):
             raise ValueError(f"CLIENT_NOT_PLENO||{cliente.id}||El cliente {cliente.razon_social} existe pero está incompleto (falta Lista de Precios o Segmento). Abra el ABM para completarlo.")

        # [NEW] Duplicate remito check based on Mirrored Numbering
        fact_num = payload.factura.numero or "0"
        fact_num_pure = fact_num.split("-")[-1].strip() if "-" in fact_num else fact_num.strip()
        fact_num_pure = re.sub(r'\D', '', fact_num_pure) or "0"
        potential_num = f"0016-{fact_num_pure.zfill(8)}"
        
        existing_remito = db.query(models.Remito).filter(models.Remito.numero_legal == potential_num).first()
        if existing_remito:
            # Report existing remito to frontend
            raise ValueError(f"REMITO_EXISTS||{existing_remito.id}||{potential_num}")
             
        # 2. RESOLVE LOGISTICS (Depurated Address & Transport)
        domicilio = None
        if payload.domicilio_id:
            domicilio = db.query(Domicilio).filter(Domicilio.id == payload.domicilio_id).first()
        
        if not domicilio:
            # Priority to Fiscal Address
            domicilios_lista = getattr(cliente, 'domicilios', [])
            domicilio = next((d for d in domicilios_lista if getattr(d, 'es_fiscal', False) and getattr(d, 'activo', True)), None)
            if not domicilio:
                domicilio = next((d for d in domicilios_lista if getattr(d, 'activo', True)), None)
            
        if not domicilio:
            # Fallback to absolute first address in DB if client has NONE (rare)
            domicilio = db.query(Domicilio).first()
            
        # Default Transport
        transporte_id = payload.transporte_id
        if not transporte_id:
            transporte = db.query(EmpresaTransporte).first()
            transporte_id = transporte.id if transporte else None

        # Depurated Reference Logic
        ref_base = payload.referencia or "A FACTURAR"
        factura_tag = f"Fact: {payload.factura.numero}" if payload.factura.numero else ""
        if factura_tag and "A FACTURAR" in ref_base:
            full_referencia = f"{ref_base} | {factura_tag}"
        else:
            full_referencia = ref_base

        # 3. CREATE PEDIDO
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

        # 4. RESOLVE ITEMS (Simplified for Remito Bridge)
        prod_generico = db.query(Producto).filter(Producto.nombre.ilike("%VARIOS%")).first()
        if not prod_generico:
             prod_generico = db.query(Producto).filter(Producto.activo == True).first()

        pedido_items = []
        for item in payload.items:
            producto = db.query(Producto).filter(Producto.nombre.ilike(f"%{item.descripcion}%")).first()
            
            nota_item = ""
            prod_id = prod_generico.id if prod_generico else None
            
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

        # 5. CREATE REMITO (With Logistics Persistence)
        vto_cae_date = None
        if payload.factura.vto_cae:
            try:
                vto_cae_date = datetime.strptime(payload.factura.vto_cae, "%d/%m/%Y")
            except:
                pass
        
        # Mirrored Numbering (RAR Standard) - Force 0016-000XXXXX
        fact_num = payload.factura.numero or "0"
        # Extract last part if hyphenated
        fact_num_pure = fact_num.split("-")[-1].strip() if "-" in fact_num else fact_num.strip()
        # Ensure it's digits only for padding
        import re
        fact_num_pure = re.sub(r'\D', '', fact_num_pure) or "0"
            
        numero_legal = f"0016-{fact_num_pure.zfill(8)}"

        remito = models.Remito(
            pedido_id=nuevo_pedido.id,
            domicilio_entrega_id=domicilio.id if domicilio else None,
            transporte_id=transporte_id,
            estado="BORRADOR",
            aprobado_para_despacho=True,
            cae=payload.factura.cae,
            vto_cae=vto_cae_date,
            numero_legal=numero_legal,
            # Logistics Fields
            bultos=payload.bultos or 1,
            valor_declarado=payload.valor_declarado or 0.0,
            referencia=full_referencia,
            observaciones=payload.observaciones
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
            
        # 7. EVO: Genoma EVO Logic
        from backend.clientes.constants import ClientFlags
        current_flags = cliente.flags_estado or 0
        new_flags = (current_flags | ClientFlags.EXISTENCE | ClientFlags.V14_STRUCT) & ~ClientFlags.VIRGINITY
        
        if current_flags != new_flags:
            cliente.flags_estado = new_flags
            db.add(cliente)

        db.commit()
        db.refresh(remito)
        
        # 8. [V5-AUTO] Generar PDF Físico (Depurated Data)
        try:
            from .remito_engine import generar_remito_pdf
            
            # Resolve Transport Name for PDF
            trans_obj = db.query(EmpresaTransporte).filter(EmpresaTransporte.id == transporte_id).first()
            trans_nombre = trans_obj.nombre if trans_obj else "PROPIO"

            # Resolve Condition IVA string
            cond_iva_str = "Consumidor Final"
            if cliente.condicion_iva:
                cond_iva_str = getattr(cliente.condicion_iva, 'nombre', str(cliente.condicion_iva))

            # Build Full Address String for PDF
            dom_str = "S/D"
            if domicilio:
                parts = []
                # Handle potential pipe format in legacy or sync data
                calle_pure = (domicilio.calle or "").split('|')[0].strip()
                if calle_pure: parts.append(calle_pure)
                if domicilio.numero: parts.append(domicilio.numero)
                if domicilio.piso: parts.append(f"Piso {domicilio.piso}")
                if domicilio.depto: parts.append(f"Depto {domicilio.depto}")
                if domicilio.localidad: parts.append(domicilio.localidad)
                dom_str = ", ".join(parts)

            # Preparar datos para el motor
            cliente_data = {
                "razon_social": cliente.razon_social,
                "cuit": cliente.cuit,
                "domicilio_fiscal": dom_str,
                "condicion_iva": cond_iva_str,
                "factura_vinculada": payload.factura.numero,
                "cae": payload.factura.cae,
                "vto_cae": payload.factura.vto_cae,
                # New Fields
                "referencia": full_referencia,
                "observaciones": payload.observaciones or "",
                "bultos": str(remito.bultos),
                "valor_declarado": str(remito.valor_declarado),
                "transporte": trans_nombre
            }
            
            items_data = []
            for item in payload.items:
                items_data.append({
                    "descripcion": item.descripcion,
                    "cantidad": item.cantidad,
                    "unidad": "UN",
                    "codigo": item.codigo or "S/N"
                })
            
            static_dir = os.path.join(ROOT_DIR, "static", "remitos")
            os.makedirs(static_dir, exist_ok=True)
            
            filename = f"REMITO_{remito.numero_legal.replace('-', '_')}.pdf"
            pdf_path = os.path.join(static_dir, filename)
            
            generar_remito_pdf(cliente_data, items_data, is_preview=False, output_path=pdf_path, numero_remito=remito.numero_legal)
            
            # 9. Set URL para retorno
            remito.pdf_url = f"/static-remitos/{filename}"
            db.add(remito)
            db.commit() 
            
        except Exception as pdf_err:
            print(f"[X] Error generando PDF automático depurado: {pdf_err}")
            
            # 9. Set URL para retorno (Relative to SPA)
            remito.pdf_url = f"/static-remitos/{filename}"
            db.add(remito)
            db.commit() # Save the URL 
            print(f"Genoma PDF: URL {remito.pdf_url} saved to DB.")
            
        except Exception as pdf_err:
            print(f"[X] Error generando PDF automático: {pdf_err}")
            import traceback
            traceback.print_exc()
            # No bloqueamos el commit principal por un error de PDF
            
        return remito
