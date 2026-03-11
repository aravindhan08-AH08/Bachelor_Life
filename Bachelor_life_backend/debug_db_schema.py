from db.database import engine
from sqlalchemy import text

def check_db():
    with engine.connect() as conn:
        print("--- Tables ---")
        res = conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';"))
        for row in res:
            print(row[0])
            
        print("\n--- Constraints for bookings ---")
        res = conn.execute(text("""
            SELECT
                conname, 
                pg_get_constraintdef(c.oid)
            FROM
                pg_constraint c
            JOIN
                pg_namespace n ON n.oid = c.connamespace
            WHERE
                conname LIKE 'bookings%';
        """))
        for row in res:
            print(f"{row[0]}: {row[1]}")

if __name__ == "__main__":
    check_db()
