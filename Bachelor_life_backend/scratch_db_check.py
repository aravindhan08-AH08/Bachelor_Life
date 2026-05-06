import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

# Add backend to path
backend_path = r'c:\Bachelor-life\Bachelor_life_backend'
sys.path.append(backend_path)

from db.database import engine

def check_db():
    print("Checking Database Connection...")
    try:
        with engine.connect() as conn:
            print("Connected successfully!")
            
            # Check tables
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = [row[0] for row in result]
            print(f"Tables found: {tables}")
            
            if 'customers' in tables:
                res = conn.execute(text("SELECT count(*) FROM customers"))
                count = res.scalar()
                print(f"Customers count: {count}")
                
                # Check columns
                res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'customers'"))
                cols = [row[0] for row in res]
                print(f"Customer columns: {cols}")
            else:
                print("CRITICAL: 'customers' table MISSING!")

            if 'owners' in tables:
                res = conn.execute(text("SELECT count(*) FROM owners"))
                count = res.scalar()
                print(f"Owners count: {count}")
                
                res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'owners'"))
                cols = [row[0] for row in res]
                print(f"Owner columns: {cols}")
            else:
                print("CRITICAL: 'owners' table MISSING!")

    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    check_db()
