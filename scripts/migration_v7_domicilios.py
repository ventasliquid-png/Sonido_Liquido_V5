import sqlite3
import uuid

# Configuration
DB_PATH = 'pilot.db'

def add_column_if_not_exists(cursor, table, column_def):
    """Adds a column to a table if it doesn't already exist."""
    column_name = column_def.split()[0]
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")
        print(f"✅ Added column '{column_name}' to '{table}'.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"ℹ️ Column '{column_name}' already exists in '{table}'. Skipping.")
        else:
            print(f"❌ Error adding column '{column_name}': {e}")

def migrate_v7_domicilios():
    print("🚀 Starting V7 Domicilios Migration...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Add new columns
    print("\n--- Schema Updates ---")
    add_column_if_not_exists(cursor, "domicilios", "piso TEXT")
    add_column_if_not_exists(cursor, "domicilios", "depto TEXT")
    add_column_if_not_exists(cursor, "domicilios", "maps_link TEXT")
    add_column_if_not_exists(cursor, "domicilios", "notas_logistica TEXT")
    add_column_if_not_exists(cursor, "domicilios", "contacto_id INTEGER")

    # 2. Data Rescue & Split
    print("\n--- Data Rescue (Splitting Pipes) ---")
    cursor.execute("SELECT id, calle, numero FROM domicilios")
    domicilios = cursor.fetchall()

    count_migrated = 0
    for dom_id, calle, numero in domicilios:
        updates = {}
        
        # Check 'calle' for pipe (Legacy format: Calle|Piso|Depto)
        if calle and '|' in calle:
            parts = calle.split('|')
            updates['calle'] = parts[0].strip()
            if len(parts) > 1 and parts[1].strip():
                updates['piso'] = parts[1].strip()
            if len(parts) > 2 and parts[2].strip():
                updates['depto'] = parts[2].strip()
            print(f"  🔹 Splitting Calle '{calle}' -> {updates}")

        # Check 'numero' for pipe (Rare but possible: 123|PB)
        if numero and '|' in numero:
            parts = numero.split('|')
            updates['numero'] = parts[0].strip()
            if len(parts) > 1 and parts[1].strip():
                # If piso was not set by calle splitted, set it here
                if 'piso' not in updates:
                     updates['piso'] = parts[1].strip()
            print(f"  🔹 Splitting Numero '{numero}' -> {updates}")

        if updates:
            # Construct UPDATE query dynamically
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values())
            values.append(dom_id)
            
            cursor.execute(f"UPDATE domicilios SET {set_clause} WHERE id = ?", values)
            count_migrated += 1

    conn.commit()
    conn.close()
    
    print(f"\n✅ Migration Complete. {count_migrated} addresses updated.")

if __name__ == "__main__":
    migrate_v7_domicilios()
