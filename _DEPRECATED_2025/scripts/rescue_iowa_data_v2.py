
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

def get_iowa_connection():
    return psycopg2.connect(**IOWA_CONFIG)

def get_local_connection():
    return sqlite3.connect(LOCAL_DB)

def rescue():
    print("--- RESCUE RAIDER v2: IOWA -> LOCAL ---")
    
    try:
        local_conn = get_local_connection()
        local_ids = set(pd.read_sql("SELECT id FROM clientes", local_conn)['id'].astype(str))
        print(f"Local Clients: {len(local_ids)}")
    except Exception as e:
        print(f"Error reading local: {e}")
        return

    try:
        remote_conn = get_iowa_connection()
        # Explicit columns to avoid potential IOWA vs Local mismatch
        # But for now SELECT * is easier if schema is mostly same.
        df_remote = pd.read_sql("SELECT * FROM clientes", remote_conn)
        print(f"Remote Clients: {len(df_remote)}")
    except Exception as e:
        print(f"Error reading remote: {e}")
        return
        
    df_remote['id_str'] = df_remote['id'].astype(str)
    missing_df = df_remote[~df_remote['id_str'].isin(local_ids)]
    
    if missing_df.empty:
        print("✅ No missing clients found.")
        return

    print(f"🚨 FOUND {len(missing_df)} CLIENTS IN IOWA NOT IN LOCAL!")
    
    cursor = local_conn.cursor()
    count = 0
    
    # Get local columns to match insert
    cursor.execute("PRAGMA table_info(clientes)")
    local_columns = [r[1] for r in cursor.fetchall()]
    
    for _, row in missing_df.iterrows():
        # Match IOWA columns to Local columns
        # Filter row dictionary
        
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
                # handle NaN
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
            sql = f"INSERT INTO clientes ({col_string}) VALUES ({placholders})"
            cursor.execute(sql, vals)
            count += 1
            print(f"  + Imported: {row['razon_social']}")
        except Exception as e:
            print(f"  ❌ Failed to import {row['razon_social']}: {e}")

    local_conn.commit()
    print(f"✅ Recovery Complete. Imported {count} clients.")
    
    remote_conn.close()
    local_conn.close()

if __name__ == "__main__":
    rescue()
