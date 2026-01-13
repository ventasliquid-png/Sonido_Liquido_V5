
import os
import re
import pdfplumber
import pandas as pd
from datetime import datetime
import sqlite3
import uuid

# Directorios

# Directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INGESTA_DIR = os.path.join(BASE_DIR, "INGESTA_FACTURAS")

def normalize_cuit(cuit_str):
    return cuit_str.replace("-", "").replace(" ", "").strip()

def extract_data_from_pdf(pdf_path):
    data = {"archivo": os.path.basename(pdf_path), "cuit": None, "razon_social": None, "domicilio": None}
    ISSUER_CUIT = "30715603973"
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = pdf.pages[0].extract_text(layout=True) or "" 
            
            # --- 1. CUIT ---
            # Search all CUIT-like patterns
            # Priority to hyphenated because it's safer
            regex_hyphen = r'\b(20|23|27|30|33)-(\d{8})-(\d)\b'
            regex_plain  = r'\b(20|23|27|30|33)(\d{8})(\d)\b'
            
            matches = re.findall(regex_hyphen, text)
            if not matches:
                clean_text = text.replace(" ", "").replace("-", "")
                matches = re.findall(regex_plain, clean_text)
            
            valid_cuit = None
            for m in matches:
                # Reconstruct plain for check
                plain = f"{m[0]}{m[1]}{m[2]}"
                formatted = f"{m[0]}-{m[1]}-{m[2]}"
                
                if plain != ISSUER_CUIT:
                    valid_cuit = formatted
                    break # Take first NON-ISSUER CUIT
            
            data["cuit"] = valid_cuit
            
            # --- 2. DOMICILIO ---
            # Skip lines that look like Issuer Address (Av. de los Incas, CABA etc - need info?)
            # Heuristic: Address usually comes AFTER "Señor(es)" or "Cliente" label if layout is standard.
            # If not, we skip the FIRST address match if it's near the top (Issuer header).
            
            lines = text.split('\n')
            for i, line in enumerate(lines):
                # Labels
                if "Domicilio" in line or "Dirección" in line or "Direccion" in line:
                    # Traer lo que sigue
                    cleaned = re.sub(r'(Domicilio.*?|Direcci.*?):', '', line, flags=re.IGNORECASE).strip()
                    
                    # Filtering Issuer Address Heuristics
                    # If line is very high up (header)? 
                    # Better: Check if it contains "Sonido Liquido" specific keywords if known, 
                    # or if it matches the text extracted from Header previously.
                    # User said: "Encabezado tiene datos del emisor".
                    
                    # Hack: The issuer address likely contains "Av. de los Incas" or similar?
                    # Since I don't know it, I will assume the Issuer address is the FIRST one found 
                    # IF and ONLY IF there is a second one.
                    # Or better: Look for Address ONLY after finding "Señor(es)" or "Cliente".
                    
                    if len(cleaned) > 5:
                        # Check context: Is "Cliente" or "Señor" nearby above?
                        # Scanning 5 lines up
                        context_found = False
                        for j in range(max(0, i-5), i):
                            prev = lines[j].lower()
                            if "cliente" in prev or "señor" in prev or "razon social" in prev:
                                context_found = True
                                break
                        
                        if context_found:
                            data["domicilio"] = cleaned
                            break # High confidence
                        elif not data["domicilio"]:
                             # Keep as candidate but keep looking
                             data["domicilio"] = cleaned

    except Exception as e:
        print(f"Err {os.path.basename(pdf_path)}: {e}")
        
    return data

def main():
    print("--- INICIANDO MINERÍA DE FACTURAS (V2) ---")
    
    if not os.path.exists(INGESTA_DIR):
        print(f"Directorio no encontrado")
        return

    files = [f for f in os.listdir(INGESTA_DIR) if f.lower().endswith('.pdf')]
    print(f"Encontrados {len(files)} archivos PDF.\n")
    
    resultados = []
    
    # Connect DB once
    conn = sqlite3.connect(os.path.join(BASE_DIR, "pilot.db"))
    cursor = conn.cursor()
    count_new = 0

    for f in files:
        path = os.path.join(INGESTA_DIR, f)
        # print(f"Procesando: {f}...", end="\r")
        
        datos = extract_data_from_pdf(path)
        
        # Fallback Name (Filename)
        if not datos["razon_social"]:
             clean_name = f.replace('.pdf', '')
             match_name = re.search(r'\d{8,}.*?\s+(.+)$', clean_name)
             if match_name:
                datos["razon_social"] = match_name.group(1).strip()
             else:
                datos["razon_social"] = clean_name
        
        cuit = datos["cuit"]
        nombre = datos["razon_social"]
        dom_text = datos["domicilio"]
        
        if not nombre: continue

        # --- DB LOGIC ---
        existing_id = None
        
        # 1. Check by CUIT (if we have one)
        if cuit:
            cursor.execute("SELECT id FROM clientes WHERE cuit = ?", (cuit,))
            res = cursor.fetchone()
            if res: existing_id = res[0]
            
        # 2. Check by Name (Fuzzy/Like)
        if not existing_id:
             cursor.execute("SELECT id FROM clientes WHERE razon_social LIKE ?", (f"%{nombre}%",))
             res = cursor.fetchone()
             if res: existing_id = res[0]
             
        if not existing_id:
            # INSERT
            print(f"[+] INSERTANDO: {nombre:<30} CUIT: {cuit or 'GENERANDO...'}")
            try:
                new_id = str(uuid.uuid4())
                
                # Temp CUIT logic
                is_temporal = False
                if not cuit:
                    import hashlib
                    hash_obj = hashlib.md5(nombre.encode())
                    h = hash_obj.hexdigest()[:8].upper()
                    cuit = f"99-{h}-9"
                    is_temporal = True
                
                cursor.execute("""
                    INSERT INTO clientes (id, razon_social, cuit, activo, requiere_auditoria, created_at)
                    VALUES (?, ?, ?, 1, ?, ?)
                """, (new_id, nombre, cuit, 1 if is_temporal else 0, datetime.now()))
                
                # Add Address
                if dom_text:
                     dom_id = str(uuid.uuid4())
                     cursor.execute("""
                        INSERT INTO domicilios (id, cliente_id, calle, es_fiscal, activo)
                        VALUES (?, ?, ?, 1, 1)
                     """, (dom_id, new_id, dom_text))
                
                count_new += 1
                
            except Exception as e:
                print(f"   [Error] {e}")
        else:
            # print(f"[=] YA EXISTE: {nombre}")
            pass

    conn.commit()
    conn.close()
    print(f"\n[FIN] Insertados {count_new} clientes nuevos.")

if __name__ == "__main__":
    main()
