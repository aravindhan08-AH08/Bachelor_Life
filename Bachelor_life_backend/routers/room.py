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
    rooms = db.query(Room).filter(Room.is_approved == True, Room.is_available == True).all()
    return [{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rooms]

# 1.5 GET SINGLE ROOM DETAILS
@router.get("/{room_id}")
def get_room_details(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Add owner details directly to the response object for frontend ease
    result = {c.name: getattr(room, c.name) for c in room.__table__.columns}
    if room.owner:
        result["owner_name"] = room.owner.owner_name
        result["owner_email"] = room.owner.email
        result["owner_phone"] = room.owner.phone
        
    return result

import base64

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_room(
    owner_email: str = Form(...),
# ... parameters remains same ...
    security: bool = Form(False),
    gym: bool = Form(False),
    cctv: bool = Form(False),
    semi_furnished: bool = Form(False),
    gender: str = Form("Any"),
    is_available: bool = Form(True),
    files: List[UploadFile] = File(...),
    video_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # Constraint Check
    if sharing_capacity > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 persons only allowed!")

    owner = db.query(Owner).filter(Owner.email == owner_email).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner email not found!")

    # Conversion to Base64 (Vercel Friendly)
    base64_images = []
    if files:
        for file in files:
            if file.filename:
                contents = await file.read()
                # Encode to base64
                encoded = base64.b64encode(contents).decode("utf-8")
                mime_type = file.content_type or "image/jpeg"
                base64_images.append(f"data:{mime_type};base64,{encoded}")

    new_room = Room(
        title=title, location=location, rent=rent, room_type=room_type,
        description=description, max_persons=sharing_capacity,
        bachelor_allowed=bachelor_allowed, wifi=wifi, ac=ac, 
        attached_bath=attached_bath, deposit=deposit,
        kitchen_access=kitchen_access, parking=parking, laundry=laundry,
        security=security, gym=gym, cctv=cctv, 
        semi_furnished=semi_furnished, gender=gender,
        image_url=base64_images, # Base64 data saved here
        is_available=is_available, owner_id=owner.id, is_approved=True 
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
        new_base64_images = []
        for file in files:
            if file.filename:
                contents = await file.read()
                encoded = base64.b64encode(contents).decode("utf-8")
                mime_type = file.content_type or "image/jpeg"
                new_base64_images.append(f"data:{mime_type};base64,{encoded}")
        room.image_url = new_base64_images

    # ... rest of the updates ...

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