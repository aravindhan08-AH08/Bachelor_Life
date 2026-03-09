from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from routers import room, Booking, user, owner, user_dashboard
from db.database import Base, engine

from models import owner_models, user_models, room_models, booking_models

app = FastAPI(title="Welcome to BachelorLife Backend")

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Database creation failed: {e}")

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