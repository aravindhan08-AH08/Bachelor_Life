from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.owner_models import Owner
from models.room_models import Room
from models.booking_models import Booking 
from schema.owner_schema import OwnerCreate, OwnerResponse, OwnerDashboardResponse
# from core.security import get_password_hash # Idhai ippo use panna poradhu illa

router = APIRouter(prefix="/owner", tags=["Owner"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Get all Owners
@router.get("/", response_model=list[OwnerResponse])
def get_all_owner(db: Session = Depends(get_db)):
    return db.query(Owner).all()

# 2. Owner Create (Password modified to store as plain text)
@router.post("/", response_model=OwnerResponse)
def create_owner(data: OwnerCreate, db: Session = Depends(get_db)):
    existing = db.query(Owner).filter(Owner.email == data.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")

    # hashed_pwd = get_password_hash(data.password) # Intha line-ah thookiyachu

    new_owner = Owner(
        owner_name=data.owner_name,
        phone=data.phone,
        email=data.email,
        hashed_password=data.password # Direct-ah original password store aagum
    )
    db.add(new_owner)
    db.commit()
    db.refresh(new_owner)
    return new_owner

# 3. Get Owner Dashboard
@router.get("/dashboard")
def get_owner_dashboard(owner_email: str, db: Session = Depends(get_db)):
    owner = db.query(Owner).filter(Owner.email == owner_email).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    
    my_rooms = db.query(Room).filter(Room.owner_id == owner.id).all()
    room_ids = [room.id for room in my_rooms]
    my_bookings = db.query(Booking).filter(Booking.room_id.in_(room_ids)).all()

    return {
        "owner_name": owner.owner_name,
        "total_rooms": len(my_rooms),
        "rooms": [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in my_rooms],
        "bookings_received": [{c.name: getattr(b, c.name) for c in b.__table__.columns} for b in my_bookings]
    }

# 4. Approve Booking from Dashboard
@router.put("/dashboard/approve-booking/{booking_id}")
def dashboard_approve_booking(booking_id: int, owner_email: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    owner = db.query(Owner).filter(Owner.id == room.owner_id).first()
    
    if not owner or owner.email.strip().lower() != owner_email.strip().lower():
        raise HTTPException(
            status_code=403, 
            detail="Permission denied! Room owner email is different."
        )

    booking.status = "Confirmed"
    room.is_available = False
    
    db.commit()
    return {"message": "Booking confirmed from dashboard!"}