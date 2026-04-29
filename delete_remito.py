import sqlite3
conn = sqlite3.connect('C:/dev/V5-LS/data/V5_LS_MASTER.db')
cursor = conn.cursor()
cursor.execute("SELECT id FROM remitos WHERE numero_legal='0016-00001-00002531'")
row = cursor.fetchone()
if row:
    remito_id = row[0]
    cursor.execute("DELETE FROM remitos_items WHERE remito_id=?", (remito_id,))
    cursor.execute("DELETE FROM remitos WHERE id=?", (remito_id,))
    conn.commit()
    print(f"Remito {remito_id} deleted successfully.")
else:
    print("Remito not found.")
conn.close()
