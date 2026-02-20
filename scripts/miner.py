
import os
import re
import pdfplumber
import pandas as pd
from datetime import datetime
import sqlite3
import uuid

# Directorios
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INGESTA_DIR = os.path.join(BASE_DIR, "INGESTA_FACTURAS")

# Bitmask Constants (Mapped from backend/clientes/constants.py)
FLAG_IS_ACTIVE = 0x01
FLAG_IS_VIRGIN = 0x02
FLAG_FISCAL_REQUIRED = 0x04
FLAG_ARCA_VALIDATED = 0x08
FLAG_DOC_A_PERMITTED = 0x10

# Target Flags for ARCA Ingestion:
# Active (1) + Fiscal (4) + Arca (8) = 13.
# We explicitly REMOVE Virgin (2) because an invoice implies operation/history.
TARGET_FLAGS_GOLD_CANDIDATE = FLAG_IS_ACTIVE | FLAG_FISCAL_REQUIRED | FLAG_ARCA_VALIDATED # 13

def normalize_cuit(cuit_str):
    if not cuit_str: return None
    return cuit_str.replace("-", "").replace(" ", "").strip()

def extract_data_from_pdf(pdf_path):
    data = {"archivo": os.path.basename(pdf_path), "cuit": None, "razon_social": None, "domicilio": None, "tipo_comprobante": None}
    ISSUER_CUIT = "30715603973"
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = pdf.pages[0].extract_text(layout=True) or "" 
            
            # --- 1. CUIT ---

            regex_hyphen = r'\b(20|23|27|30|33)-(\d{8})-(\d)\b'
            regex_plain  = r'\b(20|23|27|30|33)(\d{8})(\d)\b'
            
            matches = re.findall(regex_hyphen, text)
            if not matches:
                # Try plain regex on ORIGINAL text first (preserves boundaries)
                matches = re.findall(regex_plain, text)
            
            if not matches:
                # Last resort: Clean text (risky for boundaries but good for spacing issues)
                clean_text = text.replace(" ", "").replace("-", "")
                matches = re.findall(regex_plain, clean_text)

            
            valid_cuit = None
            for m in matches:
                formatted = f"{m[0]}-{m[1]}-{m[2]}"
                plain = f"{m[0]}{m[1]}{m[2]}"
                
                if plain != ISSUER_CUIT:
                    valid_cuit = formatted
                    break 
            
            data["cuit"] = valid_cuit
            
            # --- 2. DOMICILIO ---
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if "Domicilio" in line or "Dirección" in line or "Direccion" in line:
                    cleaned = re.sub(r'(Domicilio.*?|Direcci.*?):', '', line, flags=re.IGNORECASE).strip()
                    if len(cleaned) > 5:
                        # Heuristic: Check context
                        context_found = False
                        for j in range(max(0, i-5), i):
                            prev = lines[j].lower()
                            if "cliente" in prev or "señor" in prev or "razon social" in prev:
                                context_found = True
                                break
                        
                        if context_found:
                            data["domicilio"] = cleaned
                            break
                        elif not data["domicilio"]:
                            data["domicilio"] = cleaned

    except Exception as e:
        print(f"Err {os.path.basename(pdf_path)}: {e}")
        
    return data

def main():
    print("--- INICIANDO MINERÍA DE FACTURAS (V2 - INTELLIGENT UPSERT) ---")
    
    if not os.path.exists(INGESTA_DIR):
        print(f"Directorio no encontrado: {INGESTA_DIR}")
        return

    files = [f for f in os.listdir(INGESTA_DIR) if f.lower().endswith('.pdf')]
    print(f"Encontrados {len(files)} archivos PDF.\n")
    
    conn = sqlite3.connect(os.path.join(BASE_DIR, "pilot.db"))
    # Enable name-based access
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    count_new = 0
    count_updated = 0
    count_skipped = 0

    for f in files:
        path = os.path.join(INGESTA_DIR, f)
        datos = extract_data_from_pdf(path)
        
        # Fallback Name (Filename)
        if not datos["razon_social"]:
             clean_name = f.replace('.pdf', '')
             # Try to extract name after numbers "20240101_Factura_123_CLIENTE_NAME"
             match_name = re.search(r'\d{8,}.*?\s+(.+)$', clean_name)
             if match_name:
                datos["razon_social"] = match_name.group(1).strip()
             else:
                datos["razon_social"] = clean_name
        
        cuit = datos["cuit"]
        nombre = datos["razon_social"]
        dom_text = datos["domicilio"]
        
        if not nombre: 
            print(f"[-] SKIPPING {f}: No se pudo determinar Razón Social.")
            continue

        print(f"Procesando: {nombre:<30} | CUIT: {cuit or 'N/A'}")

        # --- INTELLIGENT UPSERT LOGIC ---
        existing_client = None
        
        # 1. Search by CUIT
        if cuit:
            cursor.execute("SELECT * FROM clientes WHERE cuit = ?", (cuit,))
            existing_client = cursor.fetchone()
            
        # 2. Search by Name (Fuzzy) if no CUIT match
        if not existing_client:
             cursor.execute("SELECT * FROM clientes WHERE razon_social LIKE ?", (f"%{nombre}%",))
             existing_client = cursor.fetchone()

        if existing_client:
            # === ESCENARIO A & B: UPDATE (UPSERT) ===
            client_id = existing_client['id']
            current_flags = existing_client['flags_estado'] or 0
            current_state = existing_client['estado_arca']
            
            # Logic: Remove Virgin Bit (0x02) -> Invoice implies operation
            # Add Fiscal (0x04) & Arca (0x08) -> We have official data
            new_flags = (current_flags & ~FLAG_IS_VIRGIN) | FLAG_FISCAL_REQUIRED | FLAG_ARCA_VALIDATED
            
            # Logic: Peaje de Calidad (Yellow State) logic
            # If already VALIDATED (Gold), we maintain it? User said "Si es Dorado Virgen -> 13". 
            # If it's pure Gold (29?), we shouldn't downgrade to 13?
            # User said: "Si el cliente ya existe y es 'Dorado Virgen' (Flag 15), realizar UPDATE a 13."
            # User said: "Si existe pero es nivel inferior... inyectá datos y llevalo a Nivel 13."
            # So target is 13.
            
            target_state = 'PENDIENTE_AUDITORIA'
            
            # Update Query
            try:
                cursor.execute("""
                    UPDATE clientes 
                    SET flags_estado = ?,
                        estado_arca = ?,
                        cuit = COALESCE(?, cuit),  -- Update CUIT if ours is better
                        updated_at = ?
                    WHERE id = ?
                """, (new_flags, target_state, cuit, datetime.now(), client_id))
                
                # Update/Insert Address if provided and "Fiscal" slot is empty or needs update?
                # Simplify: Just add the extracted address as a new delivery address if it doesn't exist logistically
                # Or update fiscal? User said "Inyectá datos fiscales".
                # Let's try to update the "Fiscal" address if it exists, or insert new one.
                
                if dom_text:
                    # Check for fiscal address
                    cursor.execute("SELECT id FROM domicilios WHERE cliente_id = ? AND es_fiscal = 1", (client_id,))
                    fiscal_dom = cursor.fetchone()
                    
                    if fiscal_dom:
                        cursor.execute("UPDATE domicilios SET calle = ?, activo = 1 WHERE id = ?", (dom_text, fiscal_dom['id']))
                    else:
                        dom_id = str(uuid.uuid4())
                        cursor.execute("""
                            INSERT INTO domicilios (id, cliente_id, calle, es_fiscal, activo)
                            VALUES (?, ?, ?, 1, 1)
                        """, (dom_id, client_id, dom_text))
                
                print(f"   [↺] ACTUALIZADO: {nombre} -> Flags: {new_flags} (Nivel 13)")
                count_updated += 1
                
            except Exception as e:
                print(f"   [!] Error actualizando: {e}")

        else:
            # === ESCENARIO C: NEW INSERT ===
            try:
                new_id = str(uuid.uuid4())
                
                # Temp CUIT logic for Hash?
                is_temporal = False
                if not cuit:
                    import hashlib
                    hash_obj = hashlib.md5(nombre.encode())
                    h = hash_obj.hexdigest()[:8].upper()
                    cuit = f"99-{h}-9"
                    is_temporal = True
                
                # Flags for New: 13 (Active|Fiscal|Arca). No Virgin.
                # If temporal, we might not want Fiscal/Arca? 
                # User instructions focused on ARCA PDFs which imply Valid CUIT.
                # If we don't have CUIT, it's not "Arca Validated".
                if is_temporal:
                    # Fallback to Pink/Basic?
                    # Active(1) | Virgin(2)? Or just Active?
                    final_flags = FLAG_IS_ACTIVE | FLAG_IS_VIRGIN
                    final_state = 'PENDIENTE'
                else:
                    final_flags = TARGET_FLAGS_GOLD_CANDIDATE # 13
                    final_state = 'PENDIENTE_AUDITORIA'

                # INSERT
                # Ensure 'legacy_id_bas' is null, 'activo' map to 1
                # Auto-assign codigo_interno? Service does it. Here we use SQL.
                # Get max codigo_interno
                cursor.execute("SELECT MAX(codigo_interno) FROM clientes")
                row = cursor.fetchone()
                max_code = row[0] if row[0] is not None else 0
                next_code = max_code + 1

                cursor.execute("""
                    INSERT INTO clientes (
                        id, razon_social, cuit, 
                        flags_estado, estado_arca, 
                        activo, requiere_auditoria, 
                        codigo_interno, created_at, updated_at,
                        estrategia_precio
                    )
                    VALUES (?, ?, ?, ?, ?, 1, 1, ?, ?, ?, 'MAYORISTA_FISCAL')
                """, (
                    new_id, nombre, cuit, 
                    final_flags, final_state, 
                    next_code, datetime.now(), datetime.now()
                ))
                
                # Add Address
                if dom_text:
                     dom_id = str(uuid.uuid4())
                     cursor.execute("""
                        INSERT INTO domicilios (id, cliente_id, calle, es_fiscal, activo, es_entrega)
                        VALUES (?, ?, ?, 1, 1, 1)
                     """, (dom_id, new_id, dom_text))
                
                print(f"   [+] CREADO: {nombre} -> Flags: {final_flags} (Nivel 13)")
                count_new += 1
                
            except Exception as e:
                print(f"   [!] Error insertando: {e}")

    conn.commit()
    conn.close()
    print(f"\n[FIN] Resumen: {count_new} Nuevos | {count_updated} Actualizados | {count_skipped} Saltados.")

if __name__ == "__main__":
    main()
