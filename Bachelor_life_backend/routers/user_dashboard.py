from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.booking_models import Booking
from models.room_models import Room
from typing import List

router = APIRouter(prefix="/user-dashboard", tags=["User Dashboard"])

@router.get("/my-bookings")
def get_my_bookings(user_id: int, db: Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
    
    result = []
    for b in bookings:
        room = db.query(Room).filter(Room.id == b.room_id).first()
        result.append({
            "id": b.id,
            "room_id": b.room_id,
            "room_title": room.title if room else "N/A",
            "room_location": room.location if room else "N/A",
            "status": b.status
        })
    
    return result
