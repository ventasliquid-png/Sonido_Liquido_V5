import sqlite3
import os

db_path = r'C:\dev\Sonido_Liquido_V5\pilot_v5x.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- [GHOST HUNT] Searching for addresses with empty 'calle' ---")
cursor.execute("SELECT id, alias, calle, numero, localidad FROM domicilios WHERE calle IS NULL OR calle = '' OR calle = ' '")
ghosts = cursor.fetchall()

for g in ghosts:
    dom_id = g[0]
    print(f"\nFOUND GHOST DOMICILIO: ID={dom_id} | Alias={g[1]} | Calle='{g[2]}'")
    
    # Find linked clients
    from_bridge = "SELECT cliente_id, alias, flags FROM domicilios_clientes WHERE domicilio_id = ?"
    cursor.execute(from_bridge, (dom_id,))
    links = cursor.fetchall()
    
    for l in links:
        cli_id = l[0]
        cursor.execute("SELECT razon_social, cuit FROM clientes WHERE id = ?", (cli_id,))
        client = cursor.fetchone()
        if client:
            print(f"  -> LINKED TO CLIENT: {client[0]} (CUIT: {client[1]}) | Bridge Alias='{l[1]}' | Flags={l[2]}")
        else:
            print(f"  -> LINKED TO NON-EXISTENT CLIENT ID: {cli_id}")

conn.close()
