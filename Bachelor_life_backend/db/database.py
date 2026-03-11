from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import DB_USERNAME, DB_PASSWORD, DB_HOSTNAME, DB_PORT, DATABASE
import os
import urllib.parse

# Priority: Use DATABASE_URL (standard for Vercel/Neon/Supabase)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # 1. Fix protocol first (must be postgresql+psycopg2 for SQLAlchemy)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif "postgresql://" in DATABASE_URL and "+psycopg2" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

    # 2. Handle '@' in password Safely
    # We want to encode the password but keep the rest (host, port, db, params)
    try:
        # Split into main part and query part
        if "?" in DATABASE_URL:
            main_part, query_part = DATABASE_URL.split("?", 1)
        else:
            main_part, query_part = DATABASE_URL, ""

        # Parse prefix and rest
        prefix, rest = main_part.split("://", 1)
        if "@" in rest:
            creds, destination = rest.rsplit("@", 1)
            if ":" in creds:
                user, password = creds.split(":", 1)
                # Re-encode password safely (unquote first to avoid double-encoding)
                clean_password = urllib.parse.unquote(password)
                encoded_password = urllib.parse.quote_plus(clean_password)
                main_part = f"{prefix}://{user}:{encoded_password}@{destination}"
            
        # Reconstruct URL
        if query_part:
            DATABASE_URL = f"{main_part}?{query_part}"
            if "sslmode" not in query_part:
                DATABASE_URL += "&sslmode=require"
        else:
            DATABASE_URL = main_part + "?sslmode=require"

    except Exception as e:
        print(f"URL Parsing Error: {e}")
else:
    # Build from components (Local Setup)
    if all([DB_USERNAME, DB_PASSWORD, DB_HOSTNAME, DATABASE]):
        encoded_password = urllib.parse.quote_plus(str(DB_PASSWORD))
        port = DB_PORT or "5432"
        DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{encoded_password}@{DB_HOSTNAME}:{port}/{DATABASE}"
        
        if DB_HOSTNAME != "localhost" and "127.0.0.1" not in DB_HOSTNAME:
            DATABASE_URL += "?sslmode=require"

if not DATABASE_URL:
    # Fallback
    if os.getenv("VERCEL"):
         DATABASE_URL = "sqlite://"
    else:
         DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    DATABASE_URL, 
    pool_size=5,         # Vercel-la neraiya connections open aagaama thadukkum
    max_overflow=10, 
    pool_pre_ping=True,  
    pool_recycle=300     
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()