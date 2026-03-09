from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from db.database import get_db
from models.room_models import Room
from models.owner_models import Owner
from typing import Optional, List
import shutil
import os

router = APIRouter(prefix="/rooms", tags=["Rooms"])

UPLOAD_DIR = "static/room_images"
try:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
except OSError:
    print(f"Directory {UPLOAD_DIR} could not be created (read-only filesystem)")

# 1. GET ALL ROOMS
@router.get("/")
def get_all_rooms(db: Session = Depends(get_db)):
    # is_available True-ah irukura rooms mattum thaan list aagum (Full aana automatic-ah hidden aydum)
    rooms = db.query(Room).filter(Room.is_approved == True, Room.is_available == True).all()
    return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rooms]

# 2. CREATE ROOM (With Sharing Capacity Logic)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_room(
    owner_email: str = Form(...),
    title: str = Form(...),
    location: str = Form(...),
    deposit: int = Form(0),
    rent: int = Form(...),
    room_type: str = Form(...),
    description: str = Form(...),
    # sharing_capacity: 1 to 4 kulla thaan irukanum
    sharing_capacity: int = Form(1), 
    bachelor_allowed: bool = Form(True),
    wifi: bool = Form(False),
    ac: bool = Form(False),
    attached_bath: bool = Form(False),
    kitchen_access: bool = Form(False),
    parking: bool = Form(False),
    laundry: bool = Form(False),
    security: bool = Form(False),
    gym: bool = Form(False),
    is_available: bool = Form(True),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    # Constraint Check: Max 4 persons only
    if sharing_capacity > 4:
        raise HTTPException(
            status_code=400, 
            detail="Maximum 4 persons only allowed for sharing rooms!"
        )

    owner = db.query(Owner).filter(Owner.email == owner_email).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner email not found!")

    saved_paths = []
    if files:
        for file in files:
            if file.filename:
                file_path = f"{UPLOAD_DIR}/{file.filename}"
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                saved_paths.append(file_path)

    new_room = Room(
        title=title, location=location, rent=rent, room_type=room_type,
        description=description, 
        max_persons=sharing_capacity, # Inga capacity-ah save panrom
        bachelor_allowed=bachelor_allowed,
        wifi=wifi, ac=ac, attached_bath=attached_bath, deposit=deposit,
        kitchen_access=kitchen_access, parking=parking, laundry=laundry,
        security=security, gym=gym, 
        image_url=saved_paths, 
        is_available=is_available,
        owner_id=owner.id,
        is_approved=True 
    )
    
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    
    return {
        "message": "Room listed successfully!", 
        "room": {c.name: getattr(new_room, c.name) for c in new_room.__table__.columns}
    }

# 3. UPDATE ROOM
@router.put("/{room_id}")
async def update_room(
    room_id: int,
    owner_email: str = Form(...),
    title: str = Form(...),
    location: str = Form(...),
    deposit: int = Form(...),
    rent: int = Form(...),
    room_type: str = Form(...),
    sharing_capacity: int = Form(...),
    description: str = Form(...),
    is_available: bool = Form(True),
    files: List[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    if sharing_capacity > 4:
        raise HTTPException(status_code=400, detail="Maximum 4 persons only!")

    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    owner = db.query(Owner).filter(Owner.email == owner_email).first()
    if not owner or room.owner_id != owner.id:
        raise HTTPException(status_code=403, detail="Owner email mismatch!")

    if files:
        new_paths = []
        for file in files:
            file_path = f"{UPLOAD_DIR}/{file.filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            new_paths.append(file_path)
        room.image_url = new_paths

    room.title = title
    room.location = location
    room.rent = rent
    room.deposit = deposit
    room.room_type = room_type
    room.max_persons = sharing_capacity
    room.description = description
    room.is_available = is_available

    db.commit()
    db.refresh(room)
    return {c.name: getattr(room, c.name) for c in room.__table__.columns}

# 4. DELETE ROOM
@router.delete("/{room_id}")
def delete_room(room_id: int, owner_email: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    owner = db.query(Owner).filter(Owner.email == owner_email).first()
    
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if not owner or room.owner_id != owner.id:
        raise HTTPException(status_code=403, detail="Owner email mismatch!")

    db.delete(room)
    db.commit()
    return {"message": "Room deleted successfully"}