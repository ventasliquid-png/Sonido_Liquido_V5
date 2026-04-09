import sqlite3
import unicodedata
import re

DB_PATH = 'C:/dev/V5-LS/data/V5_LS_STAGING.db'

def normalize(name):
    if not name: return ""
    text = unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore').decode('ASCII').upper()
    text = text.replace('.', '')
    text = re.sub(r'[^A-Z0-9]', ' ', text)
    tokens = [t for t in text.split() if len(t) >= 2]
    tokens.sort()
    return "".join(tokens)

def audit():
    print(f"--- [AUDITORÍA] Iniciando escaneo de duplicados en: {DB_PATH} ---")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute("SELECT id, razon_social, cuit, razon_social_canon FROM clientes")
    rows = cur.fetchall()
    
    canons = {}
    duplicates_found = 0
    
    for rid, name, cuit, canon in rows:
        # Re-verify canon on the fly to ensure logic parity
        current_canon = normalize(name)
        
        if canon != current_canon:
            print(f"[!] DIVERGENCIA: {name} (DB: {canon} | Real: {current_canon})")
            
        if current_canon and current_canon not in ['CONSUMIDORFINAL', 'CLIENTEEVENTUAL']:
            if current_canon in canons:
                canons[current_canon].append((name, rid, cuit))
                duplicates_found += 1
            else:
                canons[current_canon] = [(name, rid, cuit)]
                
    print(f"[*] Escaneo completado. Clientes analizados: {len(rows)}")
    
    if duplicates_found > 0:
        print("\n[!!!] DUPLICADOS CANÓNICOS DETECTADOS:")
        for canon, matches in canons.items():
            if len(matches) > 1:
                print(f"\nClave: {canon}")
                for m_name, m_id, m_cuit in matches:
                    print(f"  - {m_name} (ID: {m_id} | CUIT: {m_cuit})")
    else:
        print("\n[OK] No se detectaron duplicados canónicos. Estado: NOMINAL GOLD.")
        
    conn.close()

if __name__ == "__main__":
    audit()
