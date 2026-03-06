from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from db.database import get_db
from models.booking_models import Booking
from models.room_models import Room
from models.owner_models import Owner
from schema.booking_schema import BookingCreate 

router = APIRouter(prefix="/booking", tags=["Booking"])

# 1. CREATE BOOKING
@router.post("/", status_code=201)
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    # Room check and availability check
    room = db.query(Room).filter(Room.id == data.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found!")
    
    if not room.is_available:
        raise HTTPException(status_code=400, detail="This room is already filled or unavailable!")

    new_booking = Booking(
        room_id=data.room_id,
        user_id=data.user_id,
        status="Pending"
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return {
        "message": "Booking request sent to Owner!",
        "booking_id": new_booking.id,
        "booking": {c.name: getattr(new_booking, c.name) for c in new_booking.__table__.columns}
    }

# 2. APPROVE BOOKING (With Auto-Hide Logic)
@router.put("/approve/{booking_id}")
def approve_booking(
    booking_id: int, 
    owner_email: str = Form(...),
    db: Session = Depends(get_db)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found!")

    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found!")

    owner = db.query(Owner).filter(Owner.id == room.owner_id).first()
    if not owner or owner.email.strip().lower() != owner_email.strip().lower():
        raise HTTPException(status_code=403, detail="Permission denied!")

    booking.status = "Confirmed"

    confirmed_count = db.query(Booking).filter(
        Booking.room_id == room.id, 
        Booking.status == "Confirmed"
    ).count()


    if confirmed_count >= room.max_persons:
        room.is_available = False
    
    db.commit()
    db.refresh(booking)

    availability_msg = "Room is still available for more sharing." if room.is_available else "Room is now full and hidden from listings."

    return {
        "message": f"Booking successfully confirmed! {availability_msg}",
        "status": booking.status,
        "current_confirmed": confirmed_count,
        "room_limit": room.max_persons
    }