import sys
import os
import shutil
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# 1. Setup Environment
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from backend.core.database import Base
from backend.core.constants import (
    CLIENTE_IS_ACTIVE, CLIENTE_IS_VIRGIN, CLIENTE_FISCAL_REQUIRED,
    PRODUCTO_IS_ACTIVE, PRODUCTO_STOCK_CONTROL,
    PEDIDO_DISPATCH_RELEASED, 
    CONTACTO_IS_ACTIVE, CONTACTO_IS_PRIMARY,
    TRANSPORTE_IS_ACTIVE
)

# Import Models (Forces registration)
from backend.clientes import models as clientes_models
from backend.productos import models as productos_models
from backend.pedidos import models as pedidos_models
from backend.contactos import models as contactos_models
from backend.logistica import models as logistica_models
from backend.auth import models as auth_models
from backend.maestros import models as maestros_models
from backend.proveedores import models as proveedores_models

# 2. Config
PROJECT_ROOT = BASE_DIR
SOURCE_DB = "pilot(1).db"
DEST_DB = "pilot_v5x.db"

def run_migration():
    print(f"[START] INICIANDO MIGRACION INTEGRAL V5-X (4 Bytes Protocol)")
    print(f"[DIR] Origen: {SOURCE_DB}")
    print(f"[DIR] Destino: {DEST_DB}")

    source_path = os.path.join(PROJECT_ROOT, SOURCE_DB)
    dest_path = os.path.join(PROJECT_ROOT, DEST_DB)

    if not os.path.exists(source_path):
        print("[ERROR] Error: No se encuentra la base de origen pilot(1).db")
        return

    # 3. Connect to Source
    source_engine = create_engine(f"sqlite:///{source_path}")
    
    # 4. Prepare Destination (Rebuild Schema)
    if os.path.exists(dest_path):
        print("[WARN]  Eliminando base de destino existente para reconstruccion limpia...")
        os.remove(dest_path)
    
    dest_engine = create_engine(f"sqlite:///{dest_path}")
    
    print("[BUILD]  Creando estructura de tablas V5-X...")
    Base.metadata.create_all(dest_engine)
    
    # Sessions
    SourceSession = sessionmaker(bind=source_engine)
    DestSession = sessionmaker(bind=dest_engine)
    
    source_sess = SourceSession()
    dest_sess = DestSession()

    try:
        # --- PHASE 1: MAESTROS & SIMPLE TABLES ---
        # Copy tables that don't need transformation
        simple_tables = [
            # table_name, model_class
            ('roles', auth_models.Rol),
            ('usuarios', auth_models.Usuario),
            ('provincias', maestros_models.Provincia),
            ('condiciones_iva', maestros_models.CondicionIva),
            ('condiciones_iva', maestros_models.CondicionIva),
            ('listas_precios', maestros_models.ListaPrecios),
            ('segmentos', maestros_models.Segmento),
            ('rubros', productos_models.Rubro),
            ('unidades', maestros_models.Unidad),
            ('tasas_iva', maestros_models.TasaIVA),
            ('proveedores', proveedores_models.Proveedor),
            ('vendedores', maestros_models.Vendedor),
            # ('depositos', logistica_models.Deposito), # Check if exists in source
        ]

        print("\n--- FASE 1: Migración Directa (Maestros) ---")
        inspector = inspect(source_engine)
        source_tables = inspector.get_table_names()


        def clean_row(model, row_data):
            """Converts string datetimes to objects based on model definition."""
            cleaned = dict(row_data)
            for col in model.__table__.columns:
                val = cleaned.get(col.name)
                if val and isinstance(col.type, (datetime, datetime)) or str(col.type) == 'DATETIME': # Check type loosely or strictly
                     # SQLALchemy types are classes or instances
                     pass
                
                # Simpler approach: Try parsing if key contains 'created_at', 'updated_at', 'fecha'
                if isinstance(val, str) and col.name in ['created_at', 'updated_at', 'fecha', 'fecha_compromiso', 'datos_arca_last_update']:
                    try:
                        # Try common formats
                         cleaned[col.name] = datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
                    except ValueError:
                         try:
                             cleaned[col.name] = datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                         except:
                             pass # Keep as string if fail, might error
            return cleaned

        # Better Approach:  iterate columns and check type
        from sqlalchemy import DateTime, Date
        
        def fix_types(model_class, row_dict):
             new_row = dict(row_dict)
             for col_name, col in model_class.__table__.columns.items():
                 if col_name in new_row and new_row[col_name] is not None:
                     if isinstance(col.type, (DateTime, Date)):
                         val = new_row[col_name]
                         if isinstance(val, str):
                             try:
                                 new_row[col_name] = datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
                             except ValueError:
                                 try:
                                     new_row[col_name] = datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                                 except ValueError:
                                     # Last resort: just date
                                     try:
                                         new_row[col_name] = datetime.strptime(val, '%Y-%m-%d')
                                     except:
                                         pass
             return new_row

        for table_name, model_class in simple_tables:
            if table_name in source_tables:
                print(f"   -> Migrando {table_name}...")
                data = source_sess.execute(text(f"SELECT * FROM {table_name}")).mappings().all()
                for row in data:
                    cleaned_row = fix_types(model_class, dict(row))
                    # Generic copy
                    obj = model_class(**cleaned_row)
                    dest_sess.merge(obj)
                dest_sess.commit()
            else:
                print(f"   [WARN] Tabla {table_name} no encontrada en origen.")

        # --- PHASE 2: MODULES WITH FLAGS ---
        
        # 1. TRANSPORTES
        print("\n--- FASE 2.1: Logística (Empresas) ---")
        if 'empresas_transporte' in source_tables:
            transportes = source_sess.execute(text("SELECT * FROM empresas_transporte")).mappings().all()
            for t in transportes:
                t_dict = dict(t)
                
                # flags_estado calculation
                flags = 0
                if t_dict.get('activo', 1):
                    flags |= TRANSPORTE_IS_ACTIVE
                
                # Remove extra columns if they don't exist in new model or handle mismatch
                # Using specific mapping is safer
                new_transport = logistica_models.EmpresaTransporte(
                    id=t_dict['id'],
                    nombre=t_dict['nombre'],
                    cuit=t_dict.get('cuit'),
                    condicion_iva_id=t_dict.get('condicion_iva_id'),
                    direccion=t_dict.get('direccion'),
                    localidad=t_dict.get('localidad'),
                    provincia_id=t_dict.get('provincia_id'),
                    whatsapp=t_dict.get('whatsapp'),
                    email=t_dict.get('email'),
                    observaciones=t_dict.get('observaciones'),
                    web_tracking=t_dict.get('web_tracking'),
                    telefono_reclamos=t_dict.get('telefono_reclamos'),
                    servicio_retiro_domicilio=bool(t_dict.get('servicio_retiro_domicilio')),
                    requiere_carga_web=bool(t_dict.get('requiere_carga_web')),
                    activo=bool(t_dict.get('activo', True)),
                    flags_estado=flags
                )
                dest_sess.merge(new_transport)
            dest_sess.commit()


        def parse_dt(val):
            if not val: return None
            if not isinstance(val, str): return val
            try:
                return datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                try:
                    return datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    return None

        # 2. PRODUCTOS
        print("\n--- FASE 2.2: Productos ---")
        if 'productos' in source_tables:
            productos = source_sess.execute(text("SELECT * FROM productos")).mappings().all()
            for p in productos:
                p_dict = dict(p)
                
                flags = 0
                if p_dict.get('activo', 1):
                    flags |= PRODUCTO_IS_ACTIVE
                # Default Stock Control on? Maybe
                flags |= PRODUCTO_STOCK_CONTROL 
                
                new_prod = productos_models.Producto(
                    id=p_dict['id'],
                    sku=p_dict['sku'],
                    codigo_visual=p_dict['codigo_visual'],
                    nombre=p_dict['nombre'],
                    descripcion=p_dict['descripcion'],
                    rubro_id=p_dict['rubro_id'],
                    proveedor_habitual_id=p_dict.get('proveedor_habitual_id'),
                    tasa_iva_id=p_dict.get('tasa_iva_id'),
                    tipo_producto=p_dict.get('tipo_producto', 'VENTA'),
                    unidad_stock_id=p_dict.get('unidad_stock_id'),
                    unidad_compra_id=p_dict.get('unidad_compra_id'),
                    factor_compra=p_dict.get('factor_compra', 1.0),
                    stock_fisico=p_dict.get('stock_fisico', 0.0),
                    stock_reservado=p_dict.get('stock_reservado', 0.0),
                    activo=bool(p_dict.get('activo', True)),
                    es_kit=bool(p_dict.get('es_kit', False)),
                    created_at=parse_dt(p_dict['created_at']),
                    flags_estado=flags
                )
                dest_sess.merge(new_prod)
            dest_sess.commit()

        # 3. CLIENTES & DOMICILIOS
        print("\n--- FASE 2.3: Clientes ---")
        if 'clientes' in source_tables:
            clientes = source_sess.execute(text("SELECT * FROM clientes")).mappings().all()
            for c in clientes:
                c_dict = dict(c)
                
                flags = 0
                if c_dict.get('activo', 1):
                    flags |= CLIENTE_IS_ACTIVE
                
                # Logic: If CUIT exists, FISCAL_REQUIRED (Gold). Else Bronze.
                cuit = c_dict.get('cuit')
                if cuit and len(cuit) > 5:
                    flags |= CLIENTE_FISCAL_REQUIRED
                
                # IS_VIRGIN = 0 (Migrated)
                
                new_client = clientes_models.Cliente(
                    id=c_dict['id'],
                    razon_social=c_dict['razon_social'],
                    nombre_fantasia=c_dict.get('nombre_fantasia'),
                    cuit=cuit,
                    codigo_interno=c_dict.get('codigo_interno'),
                    legacy_id_bas=c_dict.get('legacy_id_bas'),
                    whatsapp_empresa=c_dict.get('whatsapp_empresa'),
                    observaciones=c_dict.get('observaciones'),
                    condicion_iva_id=c_dict.get('condicion_iva_id'),
                    lista_precios_id=c_dict.get('lista_precios_id'),
                    segmento_id=c_dict.get('segmento_id'),
                    vendedor_id=c_dict.get('vendedor_id'),
                    saldo_actual=c_dict.get('saldo_actual', 0.0),
                    activo=bool(c_dict.get('activo', True)),
                    created_at=parse_dt(c_dict['created_at']),
                    flags_estado=flags,
                    estado_arca='PENDIENTE'
                )
                dest_sess.merge(new_client)
            
            # Domicilios
            if 'domicilios' in source_tables:
                print("   -> Migrando Domicilios...")
                domicilios = source_sess.execute(text("SELECT * FROM domicilios")).mappings().all()
                for d in domicilios:
                     # Copy fields, handle generic
                     d_data = dict(d)
                     # Clean up keys that might not exist in model or renamed
                     # Domicilio model in V5 is same structure? Assuming yes.
                     obj = clientes_models.Domicilio(**d_data)
                     dest_sess.merge(obj)
            
            dest_sess.commit()

        # 4. CONTACTOS -> PERSONAS + VINCULOS
        print("\n--- FASE 2.4: Contactos (Refactor a Personas/Vínculos) ---")
        if 'contactos' in source_tables:
            contactos = source_sess.execute(text("SELECT * FROM contactos")).mappings().all()
            for ct in contactos:
                ct_dict = dict(ct)
                
                # Create Persona
                import uuid
                persona_id = str(uuid.uuid4())
                
                persona = contactos_models.Persona(
                    id=persona_id,
                    nombre=ct_dict.get('nombre', 'Desconocido'),
                    apellido=ct_dict.get('apellido'),
                    domicilio_personal=ct_dict.get('domicilio_personal'),
                    notas_globales=ct_dict.get('notas'),
                    flags_estado=0 # Universal 4 Bytes default
                )
                dest_sess.add(persona)
                
                # Create Vinculo
                # Determine Identity
                entidad_tipo = None
                entidad_id = None
                
                if ct_dict.get('cliente_id'):
                    entidad_tipo = 'CLIENTE'
                    entidad_id = ct_dict['cliente_id']
                elif ct_dict.get('transporte_id'):
                    entidad_tipo = 'TRANSPORTE'
                    entidad_id = ct_dict['transporte_id']
                
                if entidad_tipo and entidad_id:
                    flags = 0
                    if ct_dict.get('estado', 1): # estado in old contacts was boolean?
                        flags |= CONTACTO_IS_ACTIVE
                        
                    vinculo = contactos_models.Vinculo(
                        id=ct_dict['id'], # Keep original ID as Vinculo ID if compatible UUID? Old contacts id CHAR(32).
                        persona_id=persona_id,
                        entidad_tipo=entidad_tipo,
                        entidad_id=entidad_id,
                        rol=ct_dict.get('puesto'),
                        roles=ct_dict.get('roles'), # JSON
                        canales_laborales=ct_dict.get('canales'), # JSON
                        notas_vinculo=ct_dict.get('notas'),
                        activo=bool(ct_dict.get('estado', True)),
                        flags_estado=flags
                    )
                    dest_sess.add(vinculo)
            dest_sess.commit()

        # 5. PEDIDOS
        print("\n--- FASE 2.5: Pedidos ---")
        if 'pedidos' in source_tables:
            pedidos = source_sess.execute(text("SELECT * FROM pedidos")).mappings().all()
            for pd in pedidos:
                pd_dict = dict(pd)
                
                flags = 0
                if pd_dict.get('liberado_despacho'):
                    flags |= PEDIDO_DISPATCH_RELEASED
                
                new_pedido = pedidos_models.Pedido(
                    id=pd_dict['id'],
                    fecha=parse_dt(pd_dict['fecha']),
                    cliente_id=pd_dict['cliente_id'],
                    total=pd_dict['total'],
                    nota=pd_dict.get('nota'),
                    estado=pd_dict.get('estado'),
                    tipo_facturacion=pd_dict.get('tipo_facturacion'),
                    origen=pd_dict.get('origen'),
                    created_at=parse_dt(pd_dict['created_at']),
                    domicilio_entrega_id=pd_dict.get('domicilio_entrega_id'),
                    transporte_id=pd_dict.get('transporte_id'),
                    flags_estado=flags
                )
                dest_sess.merge(new_pedido)
            
            # Items
            if 'pedidos_items' in source_tables:
                 items = source_sess.execute(text("SELECT * FROM pedidos_items")).mappings().all()
                 for it in items:
                     dest_sess.merge(pedidos_models.PedidoItem(**dict(it)))
            
            dest_sess.commit()

        print("\n[DONE] MIGRACION INTEGRAL COMPLETADA.")
        
    except Exception as e:
        print(f"\n[ERROR] FATAL: {e}")
        import traceback
        traceback.print_exc()
        # Rollback handled by standard exception, but we might want to clean up
    finally:
        source_sess.close()
        dest_sess.close()

if __name__ == "__main__":
    run_migration()
