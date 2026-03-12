
import sqlite3
import pandas as pd

try:
    conn = sqlite3.connect('pilot.db')
    
    # Check if column exists first
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(clientes)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'estado_arca' not in columns:
        print("❌ Column 'estado_arca' DOES NOT EXIST in table 'clientes'.")
    else:
        # Query for validated clients
        query = "SELECT id, razon_social, cuit, estado_arca FROM clientes WHERE estado_arca = 'VALIDADO' OR estado_arca LIKE '%GOLD%'"
        df = pd.read_sql_query(query, conn)
        
        if not df.empty:
            print(f"✅ FOUND {len(df)} VALIDATED (Green/Gold) CLIENTS:")
            print(df.to_string(index=False))
        else:
            print("⚠️ NO clients found with estado_arca = 'VALIDADO'.")
            
            # Show distribution of existing states just in case
            print("\n--- State Distribution ---")
            dist_query = "SELECT estado_arca, COUNT(*) as count FROM clientes GROUP BY estado_arca"
            dist_df = pd.read_sql_query(dist_query, conn)
            print(dist_df.to_string(index=False))

    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
