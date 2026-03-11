import os
import sys

# Intha path fixing code Vercel-la folders-ah kandupidi kka uthavum
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Force Redeploy - Timestamp: March 09, 2026 - 20:10 (Fix: View Details endpoint)
# Version: 1.0.8 - Added Single Room GET route
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
    tb = traceback.format_exc()
    print(f"CRITICAL ERROR: {exc}\n{tb}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Server Error: {type(exc).__name__} - {str(exc)}",
            "traceback": tb if os.getenv("VERCEL") else "Check logs"
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
            
            # Rooms Table Updates
            conn.execute(text("ALTER TABLE rooms ADD COLUMN IF NOT EXISTS gender VARCHAR DEFAULT 'Any';"))
            conn.execute(text("ALTER TABLE rooms ADD COLUMN IF NOT EXISTS cctv BOOLEAN DEFAULT FALSE;"))
            conn.execute(text("ALTER TABLE rooms ADD COLUMN IF NOT EXISTS semi_furnished BOOLEAN DEFAULT FALSE;"))
            
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
        # Detailed connection attempt
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                db_status = "Connected"
                
                # Show tables for debugging
                try:
                    inspector = inspect(engine)
                    tables = inspector.get_table_names()
                    if tables:
                        db_status += f" (Tables: {', '.join(tables)})"
                    else:
                        db_status += " (No tables found!)"
                except Exception as inspect_err:
                    db_status += f" (Connected, but inspection failed: {str(inspect_err)})"
        except Exception as conn_err:
            error_detail = str(conn_err)
            if "password authentication failed" in error_detail:
                db_status = "Disconnected: Wrong Password or Username"
            elif "Cannot assign requested address" in error_detail:
                db_status = "Disconnected: IPv6/Direct connection failed (Switch to Pooler!)"
            else:
                db_status = f"Disconnected: {error_detail[:150]}"

    except Exception as general_err:
        db_status = f"System Error during Ping: {str(general_err)}"

    return {
        "version": "1.0.8",
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
@app.get("/fix-images")
def fix_images_endpoint():
    try:
        from sqlalchemy.orm import Session
        from db.database import SessionLocal
        from models.room_models import Room
        import json

        db: Session = SessionLocal()
        rooms = db.query(Room).all()
        fixed_count = 0
        logs = []

        # High-quality default Base64 image
        DEFAULT_B64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBwgHBgkIBwgKCgkLDRYPDQwMDRsUFRAWIB0iIiAdHx8kKDQsJCYxJx8fLT0tMTU3Ojo6Iys/RD84QzQ5OjcBCgoKDQwNGg8PGjclHyU3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3Nzc3N//AABEIAGQAZAMBEAACEQEDEQH/xAAbAAACAwEBAQAAAAAAAAAAAAABAgMEBQEGB//EADcQAAIBAwIDBQYEBgMAAAAAAAECEQADEiEEMUEFIlFhchNxgZGxwTJBobIUQmKy0vBCU+H/egvBRRRWaKKKKpSiiitBRRRQ2CiitMV9h7K4Sxc+BeI7D1mvsfZnCuLDxf1mufp1fK8mKFeRXURRRRWkUUUVpYUUUVpYUUUVpYUUZ9l+S6v+y6zV+Zfkv7LtZqfMvyZ9l+S+07Waryfkt6X5KbRarzL8mdYq0WiqfMLkdZqpzC5HWfkv7LVTiFyO7Sqq8SuV2pVeIXI7OqvELkd86vELkd86vELkd361eIXK79avELkd86vELkd86vELkd361eIXI7v1q8QuV3fOfGr8/2XKv055WfH51fkXKs8Hznxq/P9lyqfC759KvP9lyp+G3z6Veff7Llc4TfOfSr8P2XK7wm+Z6Vf6/ZcrnC75nPSrfv9lyucLvmevCre/2XKrhd8m69atev2XKrhd8m69atWv2XKvh98m69arVq9lyr4XfPp1q1ar2XKvhd+Z6datWq9lyr4XfPp1q1er2XKvhd+Z6datWr2XKvhfOenWrVa9ZsqvhN8z0q1etXU2Sq+E3zPSrVq9dLZKp4PfMdN6tWr10llqpg98x03PXVq1evoLJVPB75jpueuvz79lyv/2Q=="

        for room in rooms:
            raw = room.image_url
            if not raw: 
                logs.append(f"Room {room.id}: Empty")
                continue
            
            orig_type = str(type(raw))
            images = []
            if isinstance(raw, list):
                images = raw
            elif isinstance(raw, str):
                raw = raw.strip()
                if raw.startswith("[") and raw.endswith("]"):
                    try:
                        images = json.loads(raw.replace("'", '"'))
                    except:
                        content = raw[1:-1]
                        images = [item.strip().strip('"').strip("'") for item in content.split(",")]
                else:
                    images = [raw]
            
            # Clean up formatting
            images = [str(img).strip().replace('\\"', '"').replace('\"', '"').strip('"').strip("'") for img in images if img]

            # Vercel Migration: Replace local paths with Default Base64
            if images and len(images) > 0:
                s0 = images[0]
                if s0.startswith("static/") or s0.startswith("/static/"):
                    logs.append(f"Room {room.id} ({room.title}) had local path. Replaced with fallback Base64.")
                    images = [DEFAULT_B64]

            # Save as proper list
            room.image_url = images
            fixed_count += 1
            logs.append(f"Room {room.id} fixed. Start: {str(images[0])[:30]}...")
        
        db.commit()
        db.close()
        return {
            "status": "success",
            "message": f"Successfully fixed {fixed_count} rooms in the database.",
            "details": logs
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }

@app.get("/fix-db")
def fix_database():
    try:
        from sqlalchemy import text
        logs = []
        with engine.connect() as conn:
            # 1. Check if "users" table exists and rename to "customers" if needed
            res = conn.execute(text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');"))
            if res.scalar():
                conn.execute(text("ALTER TABLE users RENAME TO customers;"))
                logs.append("Renamed 'users' table to 'customers'.")
            
            # 2. Find and drop ALL foreign keys on bookings(user_id)
            # This query finds the constraint name regardless of what it's called
            find_fk_query = text("""
                SELECT conname 
                FROM pg_constraint 
                WHERE conrelid = 'bookings'::regclass 
                AND contype = 'f' 
                AND pg_get_constraintdef(oid) LIKE '%user_id%';
            """)
            fks = conn.execute(find_fk_query).fetchall()
            for fk in fks:
                conn.execute(text(f"ALTER TABLE bookings DROP CONSTRAINT IF EXISTS {fk[0]};"))
                logs.append(f"Dropped legacy constraint: {fk[0]}")

            # 3. Create the correct constraint pointing to "customers"
            try:
                conn.execute(text("ALTER TABLE bookings ADD CONSTRAINT bookings_user_id_fkey FOREIGN KEY (user_id) REFERENCES customers(id) ON DELETE CASCADE;"))
                logs.append("Created correct foreign key: bookings -> customers(id)")
            except Exception as e:
                logs.append(f"Constraint creation failed (maybe table missing?): {str(e)}")

            # 4. Ensure all rooms are approved
            conn.execute(text("UPDATE rooms SET is_approved = True WHERE is_approved = False;"))
            logs.append("Ensured all rooms are approved.")
            
            conn.commit()
        return {"status": "success", "steps_taken": logs}
    except Exception as e:
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}

app.include_router(owner_router.router, tags=["Owner"])
app.include_router(user_router.router, tags=["User"])
app.include_router(room_router.router, tags=["Rooms"])
app.include_router(booking_router.router, tags=["Booking"])
app.include_router(user_dashboard_router.router, tags=["User Dashboard"])