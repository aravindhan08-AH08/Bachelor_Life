import os
import sys

# Intha path fixing code Vercel-la folders-ah kandupidi kka uthavum
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Force Redeploy - Timestamp: March 09, 2026 - 14:55 (Fixing Connection)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from routers import room, Booking, user, owner, user_dashboard
from db.database import Base, engine

from models import owner_models, user_models, room_models, booking_models

from fastapi.responses import JSONResponse
import traceback

app = FastAPI(title="Welcome to BachelorLife Backend")

# Global Exception Handler for Debugging (Important for Vercel 500 errors)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error_type": type(exc).__name__,
            "error_detail": str(exc),
            "traceback": traceback.format_exc()
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

# Database Tables Creation (Ensure models are imported before this)
try:
    print("DEBUG: Attempting to create tables...")
    Base.metadata.create_all(bind=engine)
    print("DEBUG: Tables created successfully.")
except Exception as e:
    print(f"Database creation failed: {e}")
    # Don't crash here, but diagnostics reflect on /ping

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

# Routers inclusion
app.include_router(owner.router, tags=["Owner"])
app.include_router(user.router, tags=["User"])
app.include_router(room.router, tags=["Rooms"])
app.include_router(Booking.router, tags=["Booking"])
app.include_router(user_dashboard.router, tags=["User Dashboard"])