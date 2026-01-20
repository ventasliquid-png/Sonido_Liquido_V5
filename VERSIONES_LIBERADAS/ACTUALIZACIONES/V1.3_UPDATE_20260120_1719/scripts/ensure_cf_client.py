from backend.core.database import SessionLocal
from backend.clientes.models import Cliente
from backend.maestros.models import CondicionIva
import uuid

db = SessionLocal()

# 1. Check Condicion IVA 'Consumidor Final'
cond_cf = db.query(CondicionIva).filter(CondicionIva.nombre.ilike("%Consumidor Final%")).first()
if not cond_cf:
    print("Creating Condicion IVA: Consumidor Final")
    cond_cf = CondicionIva(nombre="Consumidor Final")
    db.add(cond_cf)
    db.commit()
    db.refresh(cond_cf)
else:
    print(f"Found Condicion IVA: {cond_cf.nombre}")

# 2. Check Cliente 'Mostrador' or 'Consumidor Final'
cliente = db.query(Cliente).filter(
    (Cliente.razon_social.ilike("%Mostrador%")) | 
    (Cliente.razon_social.ilike("%Consumidor Final%"))
).first()

if not cliente:
    print("Creating Cliente: Consumidor Final")
    cliente = Cliente(
        razon_social="CONSUMIDOR FINAL",
        cuit="00-00000000-0", # Generic CUIT
        condicion_iva_id=cond_cf.id,
        activo=True
    )
    db.add(cliente)
    db.commit()
    print("Cliente Created successfully.")
else:
    print(f"Found Cliente: {cliente.razon_social} (CUIT: {cliente.cuit})")
    # Ensure condition is correct
    if cliente.condicion_iva_id != cond_cf.id:
        print("Updating Condition to Consumidor Final")
        cliente.condicion_iva_id = cond_cf.id
        db.commit()

db.close()
