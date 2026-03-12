import sys
import os
from decimal import Decimal
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal, engine, Base
from backend.maestros import models as m_models
from backend.productos import models as p_models
from backend.clientes import models as c_models
from backend.agenda import models as a_models
from backend.proveedores import models as prov_models
from backend.auth import models as auth_models
from backend.logistica import models as logistica_models # Added explicit import # Added explicit import # Added explicit import

def seed_data():
    db = SessionLocal()
    try:
        print("--- Iniciando Poblado de Datos (Seeding) ---")

        # 1. TASAS IVA
        print("🌱 Sembrando Tasas IVA...")
        ivas = [
            {"nombre": "IVA 21%", "valor": 21.00},
            {"nombre": "IVA 10.5%", "valor": 10.50},
            {"nombre": "Exento", "valor": 0.00},
        ]
        for data in ivas:
            exists = db.query(m_models.TasaIVA).filter_by(nombre=data["nombre"]).first()
            if not exists:
                db.add(m_models.TasaIVA(**data))
        db.commit()

        # 2. UNIDADES
        print("🌱 Sembrando Unidades...")
        unidades = [
            {"codigo": "UN", "nombre": "Unidad"},
            {"codigo": "MT", "nombre": "Metro"},
            {"codigo": "LT", "nombre": "Litro"},
            {"codigo": "HR", "nombre": "Hora"},
            {"codigo": "KG", "nombre": "Kilogramo"},
        ]
        for data in unidades:
            exists = db.query(m_models.Unidad).filter_by(codigo=data["codigo"]).first()
            if not exists:
                db.add(m_models.Unidad(**data))
        db.commit()

        # 3. RUBROS (Con códigos de 3 letras MAYÚSCULAS)
        print("🌱 Sembrando Rubros...")
        rubros = [
            {"codigo": "AUD", "nombre": "AUDIO PROFESIONAL"},
            {"codigo": "ILU", "nombre": "ILUMINACIÓN"},
            {"codigo": "VID", "nombre": "VIDEO"},
            {"codigo": "EST", "nombre": "ESTRUCTURAS"},
            {"codigo": "CAB", "nombre": "CABLES Y CONECTORES"},
            {"codigo": "SER", "nombre": "SERVICIOS"},
        ]
        
        rubro_map = {}
        for data in rubros:
            rubro = db.query(p_models.Rubro).filter_by(codigo=data["codigo"]).first()
            if not rubro:
                rubro = p_models.Rubro(**data)
                db.add(rubro)
                db.commit()
                db.refresh(rubro)
            rubro_map[data["codigo"]] = rubro

        # 4. PRODUCTOS DE EJEMPLO
        print("🌱 Sembrando Productos de Ejemplo...")
        
        # Recuperar referencias
        iva_21 = db.query(m_models.TasaIVA).filter_by(valor=21.00).first()
        uni_un = db.query(m_models.Unidad).filter_by(codigo="UN").first()
        rubro_aud = rubro_map.get("AUD")

        if iva_21 and uni_un and rubro_aud:
            # Producto 1: Micrófono
            sku_mic = "MIC-SM58"
            if not db.query(p_models.Producto).filter_by(codigo_visual=sku_mic).first():
                prod = p_models.Producto(
                    codigo_visual=sku_mic,
                    nombre="Micrófono Shure SM58",
                    descripcion="Micrófono dinámico vocal legendario.",
                    rubro_id=rubro_aud.id,
                    tasa_iva_id=iva_21.id,
                    unidad_stock_id=uni_un.id,
                    unidad_compra_id=uni_un.id,
                    tipo_producto="VENTA",
                    activo=True
                )
                db.add(prod)
                db.commit()
                db.refresh(prod)
                
                # Costos
                costo = p_models.ProductoCosto(
                    producto_id=prod.id,
                    costo_reposicion=150.00, # USD ficticio
                    margen_mayorista=30.00,
                    iva_alicuota=21.00,
                    moneda_costo="USD"
                )
                db.add(costo)
                db.commit()

        # 5. CLIENTES DE EJEMPLO
        print("🌱 Sembrando Clientes de Ejemplo...")
        clientes = [
            {
                "razon_social": "Eventos Corporativos S.A.",
                "cuit": "30-11223344-5",
                "nombre_fantasia": "EventCorp",
                "whatsapp_empresa": "+5491112345678"
            },
            {
                "razon_social": "Juan Pérez Sonido",
                "cuit": "20-99887766-1",
                "nombre_fantasia": "JP Sound",
                "whatsapp_empresa": "+5491187654321"
            }
        ]

        for data in clientes:
            if not db.query(c_models.Cliente).filter_by(cuit=data["cuit"]).first():
                cli = c_models.Cliente(**data)
                db.add(cli)
        db.commit()

        print("✅ ¡Poblado de datos completado con éxito!")

    except Exception as e:
        print(f"❌ Error durante el seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
