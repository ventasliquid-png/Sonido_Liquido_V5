
import psycopg2
import sqlite3
import pandas as pd
import uuid

# Config
IOWA_CONFIG = {
    "host": "104.197.57.226",
    "user": "postgres",
    "password": "Spawn1482.",
    "dbname": "postgres",
    "sslmode": "require"
}
LOCAL_DB = "pilot.db"

def get_iowa_connection():
    return psycopg2.connect(**IOWA_CONFIG)

def get_local_connection():
    return sqlite3.connect(LOCAL_DB)

def rescue():
    print("--- RESCUE RAIDER: IOWA -> LOCAL ---")
    
    # 1. Get Local IDs
    try:
        local_conn = get_local_connection()
        local_ids = set(pd.read_sql("SELECT id FROM clientes", local_conn)['id'].astype(str))
        print(f"Local Clients: {len(local_ids)}")
    except Exception as e:
        print(f"Error reading local: {e}")
        return

    # 2. Get IOWA Data
    try:
        remote_conn = get_iowa_connection()
        # Fetch all clients
        df_remote = pd.read_sql("SELECT * FROM clientes", remote_conn)
        print(f"Remote Clients: {len(df_remote)}")
    except Exception as e:
        print(f"Error reading remote: {e}")
        return
        
    # 3. Identify Missing
    df_remote['id_str'] = df_remote['id'].astype(str)
    missing_df = df_remote[~df_remote['id_str'].isin(local_ids)]
    
    if missing_df.empty:
        print("✅ No missing clients found. Local DB is up to date (or ahead).")
        return

    print(f"🚨 FOUND {len(missing_df)} CLIENTS IN IOWA NOT IN LOCAL!")
    print(missing_df[['razon_social', 'created_at']].to_string())
    
    # 4. Insert Missing Clients
    cursor = local_conn.cursor()
    count = 0
    for _, row in missing_df.iterrows():
        # Prepare columns
        # We need to match SQLite schema. 
        # Pragma check? No, let's assume standard V5 schema.
        # But 'historial_cache' might be missing in IOWA df if IOWA schema is old, or present.
        # And IOWA might have 'legacy_id' etc.
        # Safest way: Explicit column mapping based on what pandas columns we have.
        
        # We strip internal pandas columns
        cols = [c for c in df_remote.columns if c not in ['id_str']]
        
        # Build INSERT
        # Note: SQLite uses ? placeholders.
        placholders = ",".join(["?"] * len(cols))
        col_names = ",".join(cols)
        values = [row[c] for c in cols]
        
        # Handle UUID/JSON conversion if needed?
        # Pandas reads UUID as UUID object usually? Or string?
        # Psycopg2 returns UUID objects. SQLite needs strings or bytes.
        values_converted = []
        for v in values:
            if isinstance(v, uuid.UUID):
                values_converted.append(str(v))
            elif isinstance(v, dict) or isinstance(v, list):
                import json
                values_converted.append(json.dumps(v))
            else:
                values_converted.append(v)

        try:
            sql = f"INSERT INTO clientes ({col_names}) VALUES ({placholders})"
            cursor.execute(sql, values_converted)
            count += 1
            print(f"  + Imported: {row['razon_social']}")
        except Exception as e:
            print(f"  ❌ Failed to import {row['razon_social']}: {e}")

    local_conn.commit()
    print(f"✅ Recovery Complete. Imported {count} clients.")
    
    # 5. TODO: Domicilios? 
    # Let's do a quick Domicilio rescue for these clients
    migrated_ids = missing_df['id_str'].tolist()
    if migrated_ids:
        print("Checking Domicilios for migrated clients...")
        # Need to format for SQL IN clause
        formatted_ids = ",".join([f"'{uid}'" for uid in migrated_ids])
        try:
            df_dom = pd.read_sql(f"SELECT * FROM domicilios WHERE cliente_id IN ({formatted_ids})", remote_conn)
            print(f"Found {len(df_dom)} domicilios.")
            
            for _, row in df_dom.iterrows():
                cols = list(df_dom.columns)
                placholders = ",".join(["?"] * len(cols))
                col_names = ",".join(cols)
                values = [row[c] for c in cols]
                values_converted = []
                for v in values:
                    if isinstance(v, uuid.UUID):
                        values_converted.append(str(v))
                    else:
                        values_converted.append(v)
                
                try:
                    sql = f"INSERT INTO domicilios ({col_names}) VALUES ({placholders})"
                    cursor.execute(sql, values_converted)
                    print(f"  + Domicilio imported.")
                except Exception as e:
                    print(f"  ❌ Domicilio error: {e}")
                    
            local_conn.commit()
        except Exception as e:
            print(f"Error fetching domicilios: {e}")

    remote_conn.close()
    local_conn.close()

if __name__ == "__main__":
    rescue()
