#!/usr/bin/env python3
"""Check Bit 3 status in sistema_status table."""

import sqlite3
import sys

db_path = "pilot_v5x.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()

    print("=== TABLAS DISPONIBLES ===")
    for t in tables:
        print(f"  {t[0]}")

    # Search for sistema_status
    print("\n=== BUSCANDO TABLA DE ESTADO DEL SISTEMA ===")
    system_tables = [t[0] for t in tables if 'sistema' in t[0].lower() or 'status' in t[0].lower()]

    if system_tables:
        print(f"✓ Encontradas: {system_tables}")
        for table in system_tables:
            print(f"\nEsquema de {table}:")
            cursor.execute(f"PRAGMA table_info({table})")
            cols = cursor.fetchall()
            for col in cols:
                print(f"  {col[1]} ({col[2]})")

            # Try to read data
            print(f"\nContenido de {table}:")
            cursor.execute(f"SELECT * FROM {table} LIMIT 5")
            data = cursor.fetchall()
            if data:
                for row in data:
                    print(f"  {row}")
            else:
                print("  (vacía)")
    else:
        print("✗ No encontrada tabla de estado del sistema")
        print("\nOpciones:")
        print("  1. La tabla podría tener otro nombre (buscar manualmente)")
        print("  2. El sistema de estado aún no está implementado")

    conn.close()

except Exception as e:
    print(f"✗ Error: {e}", file=sys.stderr)
    sys.exit(1)
