from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import DB_USERNAME, DB_PASSWORD, DB_HOSTNAME, DB_PORT, DATABASE
import os
import urllib.parse

# Priority: Use DATABASE_URL (standard for Vercel/Neon)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # SQLAlchemy requires "postgresql://" not "postgres://"
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif "postgresql://" in DATABASE_URL and "+psycopg2" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
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