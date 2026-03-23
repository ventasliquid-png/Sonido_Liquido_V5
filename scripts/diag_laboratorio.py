import sqlite3

def diag():
    conn = sqlite3.connect('pilot_v5x.db')
    cursor = conn.cursor()
    
    with open('diag_output.txt', 'w') as f:
        f.write("--- CLIENTS ---\n")
        cursor.execute("SELECT id, razon_social, cuit, flags_estado, estado_arca FROM clientes WHERE razon_social LIKE '%Laboratorio%'")
        clients = cursor.fetchall()
        for c in clients:
            f.write(f"CLIENT: {c}\n")
            client_id = c[0]
            
            cursor.execute("SELECT id, alias, calle, numero, es_fiscal, es_entrega, es_predeterminado, activo FROM domicilios WHERE cliente_id = ?", (client_id,))
            doms = cursor.fetchall()
            for d in doms:
                f.write(f"  DOM: {repr(d)}\n")

    conn.close()

if __name__ == "__main__":
    diag()
