import sqlite3
import uuid

def migrate():
    conn = sqlite3.connect('c:/dev/Sonido_Liquido_V5/pilot.db')
    cursor = conn.cursor()
    
    print("--- 1. Normalizando Provincias (Legacy -> ISO) ---")
    province_map = {
        'BA': 'B',
        'CABA': 'C',
        'CBA': 'X',
        'SF': 'S',
        'ER': 'E',
        'CORRIENTES': 'W',
        'MISIONES': 'N',
        'CHACO': 'H',
        'FORMOSA': 'P',
        'JUJUY': 'Y',
        'SALTA': 'A',
        'TUCUMAN': 'T',
        'SANTIAGO': 'G',
        'CATAMARCA': 'K',
        'RIOJA': 'F',
        'SAN JUAN': 'J',
        'MENDOZA': 'M',
        'SAN LUIS': 'D',
        'NEUQUEN': 'Q',
        'LP': 'L',
        'RN': 'R',
        'CHUBUT': 'U',
        'SC': 'Z',
        'TF': 'V'
    }
    
    for legacy, iso in province_map.items():
        cursor.execute("UPDATE domicilios SET provincia_id = ? WHERE provincia_id = ?", (iso, legacy))
        if cursor.rowcount > 0:
            print(f"Migrados {cursor.rowcount} registros de {legacy} -> {iso}")

    print("\n--- 2. Unificando Duplicados de GELATO ---")
    # Record balance:
    # 2fbeb6ebffc649ff81d1e324f410eed6 -> Gelato S.A. (KEEP)
    # 7649514785464010905380536767431e -> GELATO S.R.L. (DELETE)
    
    good_id = "2fbeb6ebffc649ff81d1e324f410eed6"
    bad_id = "7649514785464010905380536767431e"
    
    # Move orders
    cursor.execute("UPDATE pedidos SET cliente_id = ? WHERE cliente_id = ?", (good_id, bad_id))
    print(f"Movidos {cursor.rowcount} pedidos al cliente principal.")
    
    # Move domicilios
    cursor.execute("UPDATE domicilios SET cliente_id = ? WHERE cliente_id = ? AND es_fiscal = 0", (good_id, bad_id))
    print(f"Movidos {cursor.rowcount} domicilios al cliente principal.")
    
    # Delete bad client
    cursor.execute("DELETE FROM clientes WHERE id = ?", (bad_id,))
    print(f"Registro duplicado eliminado.")

    conn.commit()
    conn.close()
    print("\n--- MIGRACIÓN COMPLETADA ---")

if __name__ == "__main__":
    migrate()
