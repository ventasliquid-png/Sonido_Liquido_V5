
import sys
import os
import uuid
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# FORCE SQLITE LOCAL
DATABASE_URL = "sqlite:///pilot.db"
from backend.contactos import service, schemas, models
from backend.clientes.models import Cliente
from backend.logistica.models import EmpresaTransporte
# Import Legacy Models to satisfy relationships
import backend.agenda.models
import backend.auth.models
import backend.pedidos.models
import backend.productos.models

def run_test():
    print("🧪 INICIO TEST QA: ESCENARIO 'PEDRO POLIVALENTE' (MULTIPLEX V6)")
    print("=============================================================")
    
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 1. Buscar Entidades para Vincular (Cliente y Transporte)
        print("\n🔍 Paso 1: Buscando entidades existentes...")
        cliente = db.query(Cliente).first()
        transporte = db.query(EmpresaTransporte).first()
        
        if not cliente or not transporte:
            print("❌ ERROR: No hay suficientes datos en DB (Falta Cliente o Transporte).")
            return

        print(f"   ✅ Cliente encontrado: {cliente.razon_social} (ID: {cliente.id})")
        print(f"   ✅ Transporte encontrado: {transporte.nombre} (ID: {transporte.id})")

        # 2. Crear Persona "Pedro Polivalente"
        print("\n👤 Paso 2: Creando Persona 'Pedro Polivalente'...")
        pedro_data = schemas.ContactoCreate(
            nombre="Pedro",
            apellido="Polivalente",
            domicilio_personal="Calle Falsa 123",
            notas="Experto en logística y compras.",
            canales=[
                schemas.CanalContacto(tipo="WHATSAPP", valor="+5491100001111", etiqueta="Personal")
            ]
        )
        # Nota: create_contacto espera crear un vínculo inicial si le pasamos IDs, 
        # pero aquí queremos probar la creación "pura" o híbrida. 
        # Vamos a crearlo "puro" primero (sin vinculos iniciales en payload, si service lo permite).
        # Service create_contacto permite ids nulos.
        
        pedro = service.create_contacto(db, pedro_data)
        print(f"   ✅ Persona creada. ID: {pedro.id}")
        print(f"   Datos Personales: {pedro.nombre} {pedro.apellido} - Apps: {len(pedro.canales_personales)}")

        # 3. Vincular a Transporte (Jefe de Taller)
        print("\n🔗 Paso 3: Agregando Vínculo 1 (Transporte - Jefe de Taller)...")
        vinculo_transporte_data = schemas.ContactoCreate(
            nombre="Ignorado", apellido="Ignorado", # Payload dummy requerido por schema
            transporte_id=transporte.id,
            puesto="Jefe de Taller",
            referencia_origen="Contratado 2020",
            canales=[
                schemas.CanalContacto(tipo="EMAIL", valor="taller@transporte.com", etiqueta="Laboral")
            ]
        )
        v1 = service.add_vinculo(db, pedro.id, vinculo_transporte_data)
        if v1:
            print(f"   ✅ Vínculo Transporte creado. ID: {v1.id} - Rol: {v1.rol}")
        else:
            print("   ❌ Falló creación Vínculo Transporte.")

        # 4. Vincular a Cliente (Comprador)
        print("\n🔗 Paso 4: Agregando Vínculo 2 (Cliente - Comprador)...")
        vinculo_cliente_data = schemas.ContactoCreate(
            nombre="Ignorado", apellido="Ignorado",
            cliente_id=cliente.id,
            puesto="Comprador Senior",
            roles=["DECISOR", "PAGOS"],
            canales=[
                schemas.CanalContacto(tipo="EMAIL", valor="compras@cliente.com", etiqueta="Laboral")
            ]
        )
        v2 = service.add_vinculo(db, pedro.id, vinculo_cliente_data)
        if v2:
            print(f"   ✅ Vínculo Cliente creado. ID: {v2.id} - Rol: {v2.rol}")
        else:
            print("   ❌ Falló creación Vínculo Cliente.")

        # 5. Verificación de Integridad (Lectura)
        print("\n🧐 Paso 5: Verificando 'Billetera de Vínculos' (GET)...")
        db.expire_all() # Forzar reload
        pedro_reload = service.get_contacto(db, pedro.id)
        
        print(f"   Persona: {pedro_reload.nombre_completo}")
        print(f"   Total Vínculos: {len(pedro_reload.vinculos)}")
        
        for v in pedro_reload.vinculos:
            entity_name = "Desconocido"
            if v.entidad_tipo == "CLIENTE": entity_name = f"Cliente ({cliente.razon_social})"
            if v.entidad_tipo == "TRANSPORTE": entity_name = f"Transporte ({transporte.nombre})"
            
            status_icon = "🟢" if v.activo else "🔴"
            print(f"      - {status_icon} [{v.entidad_tipo}] {entity_name}: {v.rol}")

        # 6. Prueba de Independencia (Apagar Transporte)
        print("\n🛑 Paso 6: Apagando Vínculo Transporte...")
        # Update via service logic or manual?
        # Service update_contacto es complejo para vinculos específicos.
        # Usaremos manipulación directa para simular "click en switch".
        # O mejor, usamos update_contacto apuntando al transporte.
        
        update_payload = schemas.ContactoUpdate(
            nombre="Pedro", apellido="Polivalente", # Requeridos por Pydantic aunque opcionales en update logic
            transporte_id=transporte.id,
            estado=False # APAGAR
        )
        service.update_contacto(db, pedro.id, update_payload)
        
        db.expire_all()
        pedro_final = service.get_contacto(db, pedro.id)
        
        print("   Estado Final:")
        for v in pedro_final.vinculos:
            status_icon = "🟢" if v.activo else "🔴"
            print(f"      - {status_icon} {v.entidad_tipo}: {v.rol}")
            
        # Validación Automática
        v_trans = next(v for v in pedro_final.vinculos if v.entidad_tipo == 'TRANSPORTE')
        v_clie = next(v for v in pedro_final.vinculos if v.entidad_tipo == 'CLIENTE')
        
        if not v_trans.activo and v_clie.activo:
            print("\n✅ RESULTADO: ÉXITO TOTAL. Los vínculos son independientes.")
        else:
            print("\n❌ RESULTADO: FALLO. Interdependencia detectada.")

        # Limpieza (Opcional)
        # service.delete_contacto(db, pedro.id)
        # print("\n🧹 Limpieza realizada (Pedro eliminado).")

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_test()
