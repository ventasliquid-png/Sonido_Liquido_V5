import sys
import os
import uuid

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from core.database import SessionLocal
from backend.logistica import service as logistica_service, models as logistica_models
from backend.maestros import service as maestros_service, models as maestros_models
# from backend.agenda import service as agenda_service, models as agenda_models

def verify_filters():
    print("--- Verifying Filters ---")
    db = SessionLocal()
    try:
        # 1. Logistica: Empresas
        print("\nTesting Logistica: Empresas")
        empresa_active = logistica_models.EmpresaTransporte(nombre="Test Active", activo=True)
        empresa_inactive = logistica_models.EmpresaTransporte(nombre="Test Inactive", activo=False)
        db.add_all([empresa_active, empresa_inactive])
        db.commit()

        res_active = logistica_service.LogisticaService.get_empresas(db, status="active")
        res_inactive = logistica_service.LogisticaService.get_empresas(db, status="inactive")
        res_all = logistica_service.LogisticaService.get_empresas(db, status="all")

        print(f"Active count (should include 'Test Active'): {len(res_active)}")
        print(f"Inactive count (should include 'Test Inactive'): {len(res_inactive)}")
        print(f"All count (should include both): {len(res_all)}")

        assert any(e.nombre == "Test Active" for e in res_active)
        assert not any(e.nombre == "Test Inactive" for e in res_active)
        assert any(e.nombre == "Test Inactive" for e in res_inactive)
        assert not any(e.nombre == "Test Active" for e in res_inactive)
        assert any(e.nombre == "Test Active" for e in res_all)
        assert any(e.nombre == "Test Inactive" for e in res_all)
        print("✅ Logistica: Empresas Filters OK")

        # 2. Maestros: Ramos
        print("\nTesting Maestros: Ramos")
        ramo_active = maestros_models.Ramo(nombre="Test Active", activo=True)
        ramo_inactive = maestros_models.Ramo(nombre="Test Inactive", activo=False)
        db.add_all([ramo_active, ramo_inactive])
        db.commit()

        res_active = maestros_service.MaestrosService.get_ramos(db, status="active")
        res_inactive = maestros_service.MaestrosService.get_ramos(db, status="inactive")
        res_all = maestros_service.MaestrosService.get_ramos(db, status="all")

        assert any(r.nombre == "Test Active" for r in res_active)
        assert not any(r.nombre == "Test Inactive" for r in res_active)
        assert any(r.nombre == "Test Inactive" for r in res_inactive)
        assert any(r.nombre == "Test Active" for r in res_all)
        print("✅ Maestros: Ramos Filters OK")

        # 3. Maestros: Vendedores
        print("\nTesting Maestros: Vendedores")
        vendedor_active = maestros_models.Vendedor(nombre="Test Active", activo=True, comision_porcentaje=0)
        vendedor_inactive = maestros_models.Vendedor(nombre="Test Inactive", activo=False, comision_porcentaje=0)
        db.add_all([vendedor_active, vendedor_inactive])
        db.commit()

        res_active = maestros_service.MaestrosService.get_vendedores(db, status="active")
        res_inactive = maestros_service.MaestrosService.get_vendedores(db, status="inactive")
        res_all = maestros_service.MaestrosService.get_vendedores(db, status="all")

        assert any(v.nombre == "Test Active" for v in res_active)
        assert not any(v.nombre == "Test Inactive" for v in res_active)
        assert any(v.nombre == "Test Inactive" for v in res_inactive)
        assert any(v.nombre == "Test Active" for v in res_all)
        print("✅ Maestros: Vendedores Filters OK")

        # 4. Maestros: Listas Precios
        print("\nTesting Maestros: Listas Precios")
        lista_active = maestros_models.ListaPrecios(nombre="Test Active", activo=True, coeficiente=1.0)
        lista_inactive = maestros_models.ListaPrecios(nombre="Test Inactive", activo=False, coeficiente=1.0)
        db.add_all([lista_active, lista_inactive])
        db.commit()

        res_active = maestros_service.MaestrosService.get_listas_precios(db, status="active")
        res_inactive = maestros_service.MaestrosService.get_listas_precios(db, status="inactive")
        res_all = maestros_service.MaestrosService.get_listas_precios(db, status="all")

        assert any(l.nombre == "Test Active" for l in res_active)
        assert not any(l.nombre == "Test Inactive" for l in res_active)
        assert any(l.nombre == "Test Inactive" for l in res_inactive)
        assert any(l.nombre == "Test Active" for l in res_all)
        print("✅ Maestros: Listas Precios Filters OK")

        # 5. Agenda: Personas
        # print("\nTesting Agenda: Personas")
        # persona_active = agenda_models.Persona(nombre_completo="Test Active", activo=True)
        # persona_inactive = agenda_models.Persona(nombre_completo="Test Inactive", activo=False)
        # db.add_all([persona_active, persona_inactive])
        # db.commit()

        # res_active = agenda_service.AgendaService.get_personas(db, status="active")
        # res_inactive = agenda_service.AgendaService.get_personas(db, status="inactive")
        # res_all = agenda_service.AgendaService.get_personas(db, status="all")

        # assert any(p.nombre_completo == "Test Active" for p in res_active)
        # assert not any(p.nombre_completo == "Test Inactive" for p in res_active)
        # assert any(p.nombre_completo == "Test Inactive" for p in res_inactive)
        # assert any(p.nombre_completo == "Test Active" for p in res_all)
        # print("✅ Agenda: Personas Filters OK")

        # Cleanup
        print("\nCleaning up...")
        db.delete(empresa_active)
        db.delete(empresa_inactive)
        db.delete(ramo_active)
        db.delete(ramo_inactive)
        db.delete(vendedor_active)
        db.delete(vendedor_inactive)
        db.delete(lista_active)
        db.delete(lista_inactive)
        # db.delete(persona_active)
        # db.delete(persona_inactive)
        db.commit()
        print("✅ Cleanup OK")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verify_filters()
