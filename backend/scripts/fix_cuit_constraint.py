import sys
import os
from sqlalchemy import text

# Add project root to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(root_dir)
sys.path.append(os.path.join(root_dir, 'backend'))

from core.database import SessionLocal

def remove_unique_constraint():
    db = SessionLocal()
    try:
        print("Checking constraints on 'clientes' table...")
        
        # Check for unique indexes on cuit
        # Specific PG SQL to list indexes
        sql_check = text("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'clientes' AND indexdef LIKE '%cuit%';
        """)
        
        indexes = db.execute(sql_check).fetchall()
        for idx in indexes:
            print(f"Found index: {idx[0]} ({idx[1]})")
            if "UNIQUE" in idx[1].upper():
                print(f"Dropping UNIQUE constraint/index: {idx[0]}")
                db.execute(text(f"DROP INDEX {idx[0]}"))
                # Re-create as non-unique index if needed for performance, but models.py says index=True
                # SQLAlchemy usually names it ix_clientes_cuit.
                # If we drop it, we should recreate it as normal index.
                print(f"Re-creating index {idx[0]} as non-unique...")
                db.execute(text(f"CREATE INDEX {idx[0]} ON clientes (cuit)"))
        
        db.commit()
        print("Constraint update complete.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    remove_unique_constraint()
