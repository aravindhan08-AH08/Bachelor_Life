import os
import sys

# Intha path fixing code Vercel-la folders-ah kandupidi kka uthavum
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import room, Booking, user, owner, user_dashboard
from db.database import Base, engine

from models import owner_models, user_models, room_models, booking_models

app = FastAPI(title="Welcome to BachelorLife Backend")

# Enable CORS for all origins (Important for Vercel/Same-Origin issues)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database creation failed: {e}")

# Health Check Diagnostic
@app.get("/ping")
def ping():
    db_status = "Unknown"
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "Connected"
    except Exception as e:
        db_status = f"Disconnected: {str(e)}"

    return {
        "status": "online", 
        "db_status": db_status,
        "base_dir": BASE_DIR
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