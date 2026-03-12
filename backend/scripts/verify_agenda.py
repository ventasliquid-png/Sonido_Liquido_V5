import sys
import os

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from core.database import SessionLocal
from backend.agenda import service as agenda_service, models as agenda_models

def verify_agenda():
    print("--- Verifying Agenda Filters ---")
    db = SessionLocal()
    try:
        # 5. Agenda: Personas
        print("\nTesting Agenda: Personas")
        persona_active = agenda_models.Persona(nombre_completo="Test Active", activo=True)
        persona_inactive = agenda_models.Persona(nombre_completo="Test Inactive", activo=False)
        db.add_all([persona_active, persona_inactive])
        db.commit()

        res_active = agenda_service.AgendaService.get_personas(db, status="active")
        res_inactive = agenda_service.AgendaService.get_personas(db, status="inactive")
        res_all = agenda_service.AgendaService.get_personas(db, status="all")

        print(f"Active count: {len(res_active)}")
        print(f"Inactive count: {len(res_inactive)}")
        print(f"All count: {len(res_all)}")

        assert any(p.nombre_completo == "Test Active" for p in res_active)
        assert not any(p.nombre_completo == "Test Inactive" for p in res_active)
        assert any(p.nombre_completo == "Test Inactive" for p in res_inactive)
        assert not any(p.nombre_completo == "Test Active" for p in res_inactive)
        assert any(p.nombre_completo == "Test Active" for p in res_all)
        assert any(p.nombre_completo == "Test Inactive" for p in res_all)
        print("✅ Agenda: Personas Filters OK")

        # Cleanup
        print("\nCleaning up...")
        db.delete(persona_active)
        db.delete(persona_inactive)
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
    verify_agenda()
