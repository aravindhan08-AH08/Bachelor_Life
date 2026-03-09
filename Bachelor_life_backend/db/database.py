from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import DB_USERNAME, DB_PASSWORD, DB_HOSTNAME, DB_PORT, DATABASE
import os
import urllib.parse

# Priority: Use DATABASE_URL (standard for Vercel/Neon)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # 1. Remove query params (like pgbouncer)
    if "?" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.split("?", 1)[0]

    # 2. Fix protocol
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif "postgresql://" in DATABASE_URL and "+psycopg2" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)

    # 3. Handle '@' in password (Robust rsplit)
    try:
        # Format: protocol://user:pass@host:port/db
        prefix, rest = DATABASE_URL.split("://", 1)
        if "@" in rest:
            creds, destination = rest.rsplit("@", 1) # Split ONLY at the last '@'
            if ":" in creds:
                user, password = creds.split(":", 1)
                # Re-encode password safely
                encoded_password = urllib.parse.quote_plus(password)
                DATABASE_URL = f"{prefix}://{user}:{encoded_password}@{destination}"
    except Exception as e:
        print(f"URL Parsing Error: {e}")

    # 4. Add SSL
    if "sslmode" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"
else:
    # Build from components
    if all([DB_USERNAME, DB_PASSWORD, DB_HOSTNAME, DATABASE]):
        encoded_password = urllib.parse.quote_plus(str(DB_PASSWORD))
        port = DB_PORT or "5432"
        DATABASE_URL = f"postgresql+psycopg2://{DB_USERNAME}:{encoded_password}@{DB_HOSTNAME}:{port}/{DATABASE}"
        
        # Add SSL mode if it's not local
        if DB_HOSTNAME != "localhost" and "127.0.0.1" not in DB_HOSTNAME:
             if "?" not in DATABASE_URL:
                 DATABASE_URL += "?sslmode=require"
             else:
                 DATABASE_URL += "&sslmode=require"

if not DATABASE_URL:
    # Local fallback
    if os.getenv("VERCEL"):
         DATABASE_URL = "sqlite://" # In-memory fallback
    else:
         DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()