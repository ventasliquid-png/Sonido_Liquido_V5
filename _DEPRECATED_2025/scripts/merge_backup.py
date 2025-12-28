
import sqlite3
import os

MAIN_DB = "pilot.db"
BACKUP_DB = r"c:\dev\Sonido_Liquido_V5\_BACKUPS_IOWA\pilot_backup_20251214_002745.sqlite"

TABLES_TO_MERGE = [
    "clientes",
    "domicilios", # Critical for client info
    "pedidos",
    "pedidos_items"
]

def merge_backup():
    if not os.path.exists(MAIN_DB):
        print(f"Main DB {MAIN_DB} not found!")
        return
    if not os.path.exists(BACKUP_DB):
        print(f"Backup DB {BACKUP_DB} not found!")
        return

    conn = sqlite3.connect(MAIN_DB)
    cursor = conn.cursor()

    try:
        # Attach Backup
        print(f"Attaching {BACKUP_DB} as 'backup'...")
        cursor.execute(f"ATTACH DATABASE '{BACKUP_DB}' AS backup")
        
        for table in TABLES_TO_MERGE:
            print(f"\nMerging table '{table}'...")
            
            # Get columns to ensure matching schema or handle dynamic?
            # Ideally schema is same. If not, we might fail.
            # "INSERT OR IGNORE INTO main.table SELECT * FROM backup.table"
            
            # Count before
            cursor.execute(f"SELECT count(*) FROM {table}")
            count_before = cursor.fetchone()[0]
            
            try:
                # Dynamic column matching is safer in case schema drifted
                cursor.execute(f"PRAGMA table_info({table})")
                cols_main = [r[1] for r in cursor.fetchall()]
                col_str = ", ".join(cols_main)
                
                # Check if backup has same columns? 
                # Simplest is just try insert. If columns missing in backup, we need to specify.
                # Let's try matching columns that exist in both.
                
                cursor.execute(f"PRAGMA backup.table_info({table})")
                cols_backup = [r[1] for r in cursor.fetchall()]
                
                common_cols = [c for c in cols_main if c in cols_backup]
                
                if not common_cols:
                    print(f"  ❌ No common columns for {table}. Skipping.")
                    continue
                    
                col_list_str = ", ".join(common_cols)
                
                sql = f"""
                INSERT OR IGNORE INTO main.{table} ({col_list_str})
                SELECT {col_list_str} FROM backup.{table}
                """
                cursor.execute(sql)
                conn.commit()
                
                cursor.execute(f"SELECT count(*) FROM {table}")
                count_after = cursor.fetchone()[0]
                
                print(f"  ✅ Added {count_after - count_before} new records. (Total: {count_after})")
                
            except Exception as e:
                print(f"  ❌ Error merging {table}: {e}")
                
    except Exception as e:
        print(f"Critical Error: {e}")
    finally:
        conn.close()
        print("\n--- Merge Complete ---")

if __name__ == "__main__":
    merge_backup()
