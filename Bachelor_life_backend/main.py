from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from routers import room, Booking, user, owner, user_dashboard
from db.database import Base, engine

from models import owner_models, user_models, room_models, booking_models

app = FastAPI(title="Welcome to BachelorLife Backend")

Base.metadata.create_all(bind=engine)

if not os.path.exists("static/images"):
    os.makedirs("static/images")

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