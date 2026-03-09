from db.database import SessionLocal
from models.room_models import Room
import json

db = SessionLocal()
rooms = db.query(Room).all()
for room in rooms:
    print(f"ID: {room.id}, Title: {room.title}")
    print(f"Image URL Raw: {room.image_url}")
    print(f"Image URL Type: {type(room.image_url)}")
    print("-" * 20)
db.close()
