from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import DB_USERNAME, DB_PASSWORD, DB_HOSTNAME, DB_PORT, DATABASE
import os

# Priority: Use DATABASE_URL (standard for Vercel/Neon)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to individual components
    port = DB_PORT or "5432"
    if all([DB_USERNAME, DB_PASSWORD, DB_HOSTNAME, DATABASE]):
        DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{port}/{DATABASE}"
        # Add SSL mode if it's not local
        if DB_HOSTNAME != "localhost" and "127.0.0.1" not in DB_HOSTNAME:
             if "?" not in DATABASE_URL:
                 DATABASE_URL += "?sslmode=require"
             else:
                 DATABASE_URL += "&sslmode=require"

if not DATABASE_URL:
    # Local fallback
    if os.getenv("VERCEL"):
         print("ERROR: DATABASE_URL is not set in Vercel. FALLING BACK TO MEMORY SQLite (Unstable/Read-Only Issue).")
         DATABASE_URL = "sqlite://"
    else:
         DATABASE_URL = "sqlite:///./test.db"
         print("Using Local SQLite: test.db")

print(f"Connecting to Database...")
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()