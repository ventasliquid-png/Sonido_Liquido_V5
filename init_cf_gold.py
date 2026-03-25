from backend.core.database import SessionLocal
from backend.clientes.models import Cliente
from backend.clientes.constants import ClientFlags

db = SessionLocal()
try:
    cliente = db.query(Cliente).filter(Cliente.cuit == '00000000000').first()
    if cliente:
        print(f"Found Consumidor Final: {cliente.razon_social} | Flags: {cliente.flags_estado}")
        if cliente.razon_social != 'MOSTRADOR / GENÉRICO' or not (cliente.flags_estado & 66):
            cliente.razon_social = 'MOSTRADOR / GENÉRICO'
            cliente.flags_estado |= (2 | 64) # Bits 1 and 6
            db.add(cliente)
            db.commit()
            print("Updated Consumidor Final to GOLD standards.")
    else:
        print("Consumidor Final (00000000000) not found in this DB.")
except Exception as e:
    print(f"Error checking CF: {e}")
finally:
    db.close()
