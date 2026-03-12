
import sys
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

# FORCE SQLITE LOCAL
DATABASE_URL = "sqlite:///pilot.db"

# Import Models
import backend.agenda.models # Legacy dependency
import backend.auth.models # Users
import backend.pedidos.models # Orders
import backend.productos.models # Products
from backend.contactos import service, schemas, models
from backend.clientes.models import Cliente
from backend.logistica.models import EmpresaTransporte

def run_edge_tests():
    print("🧪 INICIO TEST EDGE CASES (ROBUSTEZ)")
    print("====================================")
    
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # DEBUG: Listar todos
        todos = db.query(backend.contactos.models.Persona).all()
        print(f"   📊 Total Personas en DB: {len(todos)}")
        for p in todos:
            print(f"      - {p.nombre} {p.apellido} (ID: {p.id})")

        # Recuperar a Pedro Polivalente (creado en test anterior)
        # Buscamos por nombre para ser dinamicos
        pedros = service.get_contactos(db, q="Pedro")
        
        pedro_read = None
        for p in pedros:
            if len(p.vinculos) > 0:
                pedro_read = p
                print(f"👤 Pedro seleccionado (con {len(p.vinculos)} vínculos): ID {p.id}")
                break
        
        if not pedro_read:
             print("⚠️ Ningún Pedro tiene vínculos. Imposible probar duplicidad completa. Usando el primero para persistencia.")
             pedro_read = pedros[0] if pedros else None

        if not pedro_read:
            print("❌ No se encontró a Pedro Polivalente.")
            return

        pedro_id = pedro_read.id
        
        # --- PRUEBA 1: EL ATAQUE DE LOS CLONES (Duplicidad) ---
        print("\n⚔️ PRUEBA 1: DETECCION DE DUPLICADOS")
        
        # Identificar un vínculo existente
        if not pedro_read.vinculos:
             print("⚠️ Pedro no tiene vinculos. Saltando prueba de duplicados.")
        else:
            vinculo_existente = pedro_read.vinculos[0]
            tipo = vinculo_existente.entidad_tipo
            entidad_id = vinculo_existente.entidad_id
            print(f"   Intentando replicar vínculo con: {tipo} ID {entidad_id}")

            payload_duplicado = schemas.ContactoCreate(
                nombre="Pedro", apellido="Clone",
                cliente_id=entidad_id if tipo == 'CLIENTE' else None,
                transporte_id=entidad_id if tipo == 'TRANSPORTE' else None,
                puesto="Clon Malvado",
                estado=True
            )
            
            # Contamos vínculos antes
            count_before = len(pedro_read.vinculos)
            
            # Ejecutamos add_vinculo
            # Expectativa: Debería fallar o retornar el existente, o crearlo (si falla la prueba).
            # Analizaremos el comportamiento.
            try:
                nuevo_v = service.add_vinculo(db, pedro_id, payload_duplicado)
                
                # Recargamos para contar
                db.expire_all()
                pedro_reload = service.get_contacto(db, pedro_id)
                count_after = len(pedro_reload.vinculos)
                
                if count_after > count_before:
                    print(f"❌ FALLO: El sistema permitió crear un duplicado de {tipo}.")
                    print(f"   Antes: {count_before}, Después: {count_after}")
                else:
                    print("✅ ÉXITO: El sistema NO incrementó la cantidad de vínculos (u ocurrió un error controlado).")
                    
            except Exception as e:
                print(f"✅ ÉXITO (Excepción): El sistema rechazó la operación: {e}")

        # --- PRUEBA 2: MEMORIA DE ELEFANTE (Persistencia Personal) ---
        print("\n🐘 PRUEBA 2: PERSISTENCIA PERSONAL")
        
        nuevas_notas = "Le gusta el café amargo y es hincha de Racing."
        nuevo_celular = "+5491112345678"
        
        payload_update = schemas.ContactoUpdate(
            nombre="Pedro", 
            apellido="Polivalente",
            notas=nuevas_notas,
            canales=[
                schemas.CanalContacto(tipo="WHATSAPP", valor=nuevo_celular, etiqueta="Personal")
            ]
        )
        
        print("   Actualizando notas y canales personales...")
        service.update_contacto(db, pedro_id, payload_update)
        
        db.expire_all()
        pedro_final = service.get_contacto(db, pedro_id)
        
        # Verificaciones
        print(f"   Notas en DB: '{pedro_final.notas_globales}'")
        
        # Buscar canal
        canales = pedro_final.canales_personales or []
        found_cel = next((c for c in canales if c['tipo'] == 'WHATSAPP' and c['valor'] == nuevo_celular), None)
        
        if pedro_final.notas_globales == nuevas_notas and found_cel:
            print("✅ ÉXITO: Datos personales persistidos correctamente.")
        else:
            print("❌ FALLO: Datos personales no coinciden.")
            print(f"   Esperado celular: {nuevo_celular}")
            print(f"   Encontrados: {canales}")

    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN TEST: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    run_edge_tests()
