from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models.owner_models import Owner
from models.room_models import Room
from models.booking_models import Booking 
from schema.owner_schema import OwnerCreate, OwnerResponse, OwnerDashboardResponse
from schema.user_schema import LoginRequest
from core.security import get_password_hash, verify_password, create_access_token

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

# 2. Owner Create (Fixed with password hashing)
@router.post("/", response_model=OwnerResponse)
def create_owner(data: OwnerCreate, db: Session = Depends(get_db)):
    existing = db.query(Owner).filter(Owner.email == data.email).first()
    if existing:
        raise HTTPException(400, "Email already exists")

    hashed_pwd = get_password_hash(data.password)

    new_owner = Owner(
        owner_name=data.owner_name,
        phone=data.phone,
        email=data.email,
        gender=data.gender,
        hashed_password=hashed_pwd
    )
    db.add(new_owner)
    db.commit()
    db.refresh(new_owner)
    return new_owner

# 5. Owner Login
@router.post("/login")
def login_owner(data: LoginRequest, db: Session = Depends(get_db)):
    owner = db.query(Owner).filter(Owner.email == data.email).first()
    if not owner:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Try hash verification first
    try:
        is_verified = verify_password(data.password, owner.hashed_password)
    except Exception:
        # Fallback to plain text for legacy data (optional, but avoids breaking existing owners)
        is_verified = (data.password == owner.hashed_password)

    if not is_verified:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": owner.email})

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": owner.id,
            "name": owner.owner_name,
            "email": owner.email,
            "phone": owner.phone
        }
    }

# 3. Get Owner Dashboard
@router.get("/dashboard")
def get_owner_dashboard(owner_email: str, db: Session = Depends(get_db)):
    from models.user_models import Customer
    owner = db.query(Owner).filter(Owner.email == owner_email).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    
    my_rooms = db.query(Room).filter(Room.owner_id == owner.id).all()
    room_ids = [room.id for room in my_rooms]
    
    # Detailed bookings with user info
    my_bookings = db.query(Booking, Customer).join(Customer, Booking.user_id == Customer.id).filter(Booking.room_id.in_(room_ids)).all()

    bookings_data = []
    for b, c in my_bookings:
        bookings_data.append({
            "id": b.id,
            "room_id": b.room_id,
            "status": b.status,
            "user_name": c.name,
            "user_phone": c.phone,
            "user_email": c.email
        })

    # Room images optimization for dashboard
    rooms_data = []
    for r in my_rooms:
        d = {col.name: getattr(r, col.name) for col in r.__table__.columns}
        if isinstance(d.get("image_url"), list) and len(d["image_url"]) > 0:
            d["image_url"] = [d["image_url"][0]]
        rooms_data.append(d)

    return {
        "owner_name": owner.owner_name,
        "total_rooms": len(my_rooms),
        "rooms": rooms_data,
        "bookings_received": bookings_data
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

    booking.status = "Approved" # Changed from 'Confirmed'
    
    # Check if room should be hidden
    approved_count = db.query(Booking).filter(Booking.room_id == room.id, Booking.status == "Approved").count()
    if approved_count >= room.max_persons:
        room.is_available = False
    
    db.commit()
    return {"message": "Booking approved successfully!"}

# 4a. Reject Booking from Dashboard
@router.put("/dashboard/reject-booking/{booking_id}")
def dashboard_reject_booking(booking_id: int, owner_email: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    room = db.query(Room).filter(Room.id == booking.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    owner = db.query(Owner).filter(Owner.id == room.owner_id).first()
    if not owner or owner.email.strip().lower() != owner_email.strip().lower():
        raise HTTPException(status_code=403, detail="Permission denied")

    booking.status = "Rejected"
    db.commit()
    return {"message": "Booking request rejected"}
