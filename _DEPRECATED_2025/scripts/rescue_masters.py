
import psycopg2
import sqlite3
import pandas as pd
import uuid
import datetime

import os
# Config
IOWA_CONFIG = {
    "host": "104.197.57.226",
    "user": "postgres",
    "password": os.getenv('DB_PASSWORD'),
    "dbname": "postgres",
    "sslmode": "require"
}
LOCAL_DB = "pilot.db"

MASTERS = [
    'condiciones_iva', 
    'segmentos', 
    'listas_precios', 
    'provincias',
    'tasas_iva',          # Added for Grid V3
    'unidades',           # Added for Grid V3
    'tipos_contacto'      # Added for Contacts
]

def get_iowa_connection():
    return psycopg2.connect(**IOWA_CONFIG)

def get_local_connection():
    return sqlite3.connect(LOCAL_DB)

def rescue_masters():
    print("--- RESCUE MASTERS: IOWA -> LOCAL ---")
    
    remote_conn = None
    local_conn = None
    
    try:
        remote_conn = get_iowa_connection()
        local_conn = get_local_connection()
        cursor = local_conn.cursor()
        
        for table in MASTERS:
            try:
                print(f"\nProcessing {table}...")
                
                # Check if local is empty? Or just merge?
                # User said "why is it not loaded?". Implies empty.
                # Let's count local first
                cursor.execute(f"SELECT count(*) FROM {table}")
                local_count = cursor.fetchone()[0]
                
                if local_count > 0:
                    print(f"  Local has {local_count} items. Skipping to avoid duplicates/conflicts (Simple Mode).")
                    continue
                    
                # Fetch Remote
                df = pd.read_sql(f"SELECT * FROM {table}", remote_conn)
                print(f"  Remote has {len(df)} items.")
                
                if df.empty:
                    continue
                    
                # Insert
                # Get local columns schema
                cursor.execute(f"PRAGMA table_info({table})")
                local_columns = [r[1] for r in cursor.fetchall()]
                
                success_count = 0
                for _, row in df.iterrows():
                    insert_data = {}
                    for col in local_columns:
                        if col in row:
                            val = row[col]
                             # Conversions
                            if isinstance(val, uuid.UUID):
                                val = str(val)
                            elif isinstance(val, (datetime.date, datetime.datetime, pd.Timestamp)):
                                val = str(val)
                            elif isinstance(val, (dict, list)):
                                 import json
                                 val = json.dumps(val)
                            if pd.isna(val):
                                val = None
                            insert_data[col] = val
                        else:
                            insert_data[col] = None
                            
                    cols = list(insert_data.keys())
                    vals = list(insert_data.values())
                    placholders = ",".join(["?"] * len(cols))
                    col_string = ",".join(cols)
                    
                    try:
                        sql = f"INSERT INTO {table} ({col_string}) VALUES ({placholders})"
                        cursor.execute(sql, vals)
                        success_count += 1
                    except Exception as e:
                        print(f"  ❌ Error inserting row: {e}")
                
                print(f"  ✅ Imported {success_count} rows into {table}.")
                local_conn.commit()
                
            except Exception as e:
                print(f"  ❌ Error processing table {table}: {e}")
                
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        if remote_conn: remote_conn.close()
        if local_conn: local_conn.close()

if __name__ == "__main__":
    rescue_masters()
