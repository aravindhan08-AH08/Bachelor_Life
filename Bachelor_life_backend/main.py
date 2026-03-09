import os
import sys

# Intha path fixing code Vercel-la folders-ah kandupidi kka uthavum
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Force Redeploy - Timestamp: March 09, 2026 - 19:35 (Final SHA256 Fix)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from routers import room as room_router, Booking as booking_router, user as user_router, owner as owner_router, user_dashboard as user_dashboard_router
from db.database import Base, engine
from models import Owner, Customer, Room, Booking # Ensures models are in metadata

from fastapi.responses import JSONResponse
import traceback

app = FastAPI(title="Welcome to BachelorLife Backend")

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exception_handlers import http_exception_handler

# Global Exception Handler (Only for UNHANDLED server crashes)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # If it's a known FastAPI error (like 400, 404, 422), let FastAPI handle it
    if isinstance(exc, (StarletteHTTPException, HTTPException, RequestValidationError)):
        return await http_exception_handler(request, exc)
    
    # Generic Server Crash Details (Like DB Connection loss or missing columns)
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Database/System Error: {type(exc).__name__} - {str(exc)}"
        }
    )

# Enable CORS for all origins (Important for Vercel/Same-Origin issues)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Tables Creation & Auto-Migration
try:
    print("DEBUG: Attempting to create tables...")
    Base.metadata.create_all(bind=engine)
    
    # AUTO-MIGRATION: Add gender column if it doesn't exist
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS gender VARCHAR;"))
            conn.execute(text("ALTER TABLE owners ADD COLUMN IF NOT EXISTS gender VARCHAR;"))
            conn.commit()
            print("DEBUG: Auto-migration success (gender column ensured).")
        except Exception as migration_error:
            print(f"DEBUG: Migration skipped/failed: {migration_error}")
            
    print("DEBUG: Tables created successfully.")
except Exception as e:
    print(f"Database creation failed: {e}")

# Health Check Diagnostic
# Version: 1.0.3 - Detailed Diagnostics
@app.get("/ping")
def ping():
    db_status = "Unknown"
    env_detected = "DATABASE_URL" in os.environ
    mode = "Cloud" if env_detected else "Local Fallback"
    
    # Advanced URL diagnostics
    raw_url = os.getenv("DATABASE_URL", "None")
    db_user = "None"
    safe_url = "None"
    
    if raw_url != "None":
        try:
            # Simple parsing for diagnostics
            if "://" in raw_url:
                prefix, rest = raw_url.split("://", 1)
                if "@" in rest:
                    creds, host = rest.rsplit("@", 1)
                    if ":" in creds:
                        db_user = creds.split(":", 1)[0]
                    else:
                        db_user = creds
                    safe_url = f"{prefix}://{db_user}:****@{host}"
        except:
            db_user = "Parsing-Error"

    try:
        from sqlalchemy import text, inspect
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "Connected"
            
            # Show tables for debugging
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            if tables:
                db_status += f" (Tables: {', '.join(tables)})"
            else:
                db_status += " (No tables found!)"

    except Exception as e:
        error_detail = str(e)
        if "password authentication failed" in error_detail:
            db_status = "Disconnected: Wrong Password or Username"
        elif "Cannot assign requested address" in error_detail:
            db_status = "Disconnected: IPv6/Direct connection failed (Switch to Pooler!)"
        else:
            db_status = f"Disconnected: {error_detail[:150]}"

    return {
        "version": "1.0.3",
        "status": "online", 
        "db_status": db_status,
        "env_check": f"DATABASE_URL detected: {env_detected}",
        "db_username": db_user,
        "database_url_preview": safe_url,
        "mode": mode,
        "vercel_env": os.getenv("VERCEL", "Not-Detected")
    }

# Static files handled by Vercel directly or skip folder creation for read-only environment
# app.mount("/static", StaticFiles(directory="static"), name="static")
# If you still want to mount it, make sure the directory is already in your git repo.
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home():
    return {"message": "Welcome to BachelorLife"}

@app.get("/init-db")
def init_db():
    try:
        from models import Owner, Customer, Room, Booking
        Base.metadata.create_all(bind=engine)
        
        # SQL to ensure gender column exists (Since create_all won't update existing tables)
        from sqlalchemy import text
        with engine.connect() as conn:
            # 1. Check/Add in Customers table
            conn.execute(text("ALTER TABLE customers ADD COLUMN IF NOT EXISTS gender VARCHAR;"))
            # 2. Check/Add in Owners table
            conn.execute(text("ALTER TABLE owners ADD COLUMN IF NOT EXISTS gender VARCHAR;"))
            conn.commit()
            
        return {"message": "Database tables and columns initialized successfully"}
    except Exception as e:
        return {"error": str(e), "traceback": traceback.format_exc()}

# Routers inclusion
app.include_router(owner_router.router, tags=["Owner"])
app.include_router(user_router.router, tags=["User"])
app.include_router(room_router.router, tags=["Rooms"])
app.include_router(booking_router.router, tags=["Booking"])
app.include_router(user_dashboard_router.router, tags=["User Dashboard"])