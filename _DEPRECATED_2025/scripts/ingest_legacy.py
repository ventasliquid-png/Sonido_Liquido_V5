import pandas as pd
import os
import difflib

LEGACY_FILE = r"C:\Users\USUARIO\Downloads\clientes discovery.xls"
CANDIDATES_FILE = r"c:\dev\Sonido_Liquido_V5\BUILD_PILOTO\data\clientes_candidatos.csv"
OUTPUT_FILE = r"c:\dev\Sonido_Liquido_V5\BUILD_PILOTO\data\clientes_limpios.csv"

def extract_legacy_data():
    print(f"--- Parsing Legacy File: {LEGACY_FILE} ---")
    try:
        df = pd.read_excel(LEGACY_FILE, header=None)
        rows, cols = df.shape
        
        legacy_db = []
        
        for r in range(rows):
            # Check for Block Start (Código:)
            val_0 = str(df.iat[r, 0]).strip()
            # print(f"DEBUG ROW {r}: '{val_0}'") 
            if val_0 == "Código:":
                print(f"DEBUG: Found Block at row {r}")
                # Extract Name (Col 3 usually)
                try:
                    name = str(df.iat[r, 3]).strip()
                    print(f"   Name Raw: {name}")
                except: name = ""
                
                if name == "nan": continue
                
                # Extract CUIT (Search roughly 10-15 rows down)
                cuit = ""
                found_cuit = False
                for r_sub in range(r, min(r+20, rows)):
                    if found_cuit: break
                    for c_scan in range(6): # Scan first 6 cols
                        try:
                            val = str(df.iat[r_sub, c_scan]).strip()
                            if val == "C.U.I.T.:":
                                # Value is likely in next col
                                cuit = str(df.iat[r_sub, c_scan+1]).strip()
                                # print(f"   Found CUIT at ({r_sub},{c_scan}): {cuit}")
                                found_cuit = True
                                break
                        except: pass
                
                if name and cuit and cuit != "nan":
                    legacy_db.append({"name": name, "cuit": cuit})
                    
        print(f"✅ Extracted {len(legacy_db)} legacy clients.")
        return legacy_db
        
    except Exception as e:
        print(f"❌ Error parsing legacy: {e}")
        return []

def fuzzy_match_cuit(candidate_name, legacy_db):
    best_match = None
    best_ratio = 0.0
    
    candidate_norm = str(candidate_name).upper().strip()
    
    for item in legacy_db:
        legacy_name = str(item['name']).upper().strip()
        
        # 1. Exact contain (Candidate is substring of Legacy)
        if candidate_norm in legacy_name and len(candidate_norm) > 4: 
             return item['cuit'], 1.0
        
        # 2. Difflib Ratio
        ratio = difflib.SequenceMatcher(None, candidate_norm, legacy_name).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = item['cuit']
            best_name_log = legacy_name
            
    # if best_ratio > 0.4:
    #    print(f"   Best for '{candidate_norm}': '{best_name_log}' ({best_ratio:.2f})")
    
    if best_ratio > 0.6: # Threshold
        return best_match, best_ratio
    return "", 0.0

def enrich():
    if not os.path.exists(CANDIDATES_FILE):
        print("Candidates file not found.")
        return

    df_cand = pd.read_csv(CANDIDATES_FILE)
    print(f"--- Candidates Loaded: {len(df_cand)} ---")
    # print(df_cand.head()) # Debug header
    
    legacy_data = extract_legacy_data()
    if not legacy_data:
        print("No legacy data found.")
        return

    # Add columns if missing
    if "cuit" not in df_cand.columns:
        df_cand["cuit"] = ""
    else:
        # Fill NaN with empty string
        df_cand["cuit"] = df_cand["cuit"].fillna("")

    if "nombre_final" not in df_cand.columns:
        df_cand["nombre_final"] = df_cand["nombre"]
    if "alias" not in df_cand.columns:
        df_cand["alias"] = ""
    if "estado" not in df_cand.columns:
        df_cand["estado"] = "PENDIENTE"

    matches = 0
    print("--- Starting Enrichment ---")
    for idx, row in df_cand.iterrows():
        # Only enrich if CUIT is missing
        curr_cuit = str(row['cuit']).strip()
        if curr_cuit == "" or curr_cuit == "nan":
            cand_name = str(row['nombre']).strip()
            # print(f"Processing: {cand_name}")
            cuit_found, score = fuzzy_match_cuit(cand_name, legacy_data)
            if cuit_found:
                df_cand.at[idx, 'cuit'] = cuit_found
                matches += 1
                if matches % 10 == 0: print(f"Matched {matches}...")
                # print(f"MATCH: {cand_name} -> {cuit_found} (Score: {score:.2f})")

    print(f"✅ Enriched {matches} clients with CUITs.")
    
    df_cand.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
    print(f"💾 Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    enrich()
