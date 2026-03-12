
import sqlite3

def list_tables():
    conn = sqlite3.connect('pilot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    
    print("Tables in pilot.db:")
    for t in tables:
        print(f" - {t[0]}")

if __name__ == "__main__":
    list_tables()
