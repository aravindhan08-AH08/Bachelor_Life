from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from db.database import get_db
from models.room_models import Room
from models.owner_models import Owner
from typing import Optional, List
import shutil
import os
import base64

router = APIRouter(prefix="/rooms", tags=["Rooms"])

# 1. GET ALL ROOMS
@router.get("/")
def get_all_rooms(db: Session = Depends(get_db)):
    rooms = db.query(Room).filter(Room.is_approved == True, Room.is_available == True).all()
    
    result = []
    for r in rooms:
        data = {c.name: getattr(r, c.name) for c in r.__table__.columns}
        
        # Handle Image URL Optimization
        raw_images = data.get("image_url")
        if isinstance(raw_images, list) and len(raw_images) > 0:
            data["image_url"] = [raw_images[0]] # Return only first image as a list
        elif isinstance(raw_images, str) and raw_images.startswith("["):
             import json
             try:
                 parsed = json.loads(raw_images.replace("'", '"'))
                 if parsed: data["image_url"] = [parsed[0]]
             except: pass
             
        result.append(data)
    return result

# 1.5 GET SINGLE ROOM DETAILS
@router.get("/{room_id}")
def get_room_details(room_id: int, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    result = {c.name: getattr(room, c.name) for c in room.__table__.columns}
    if room.owner:
        result["owner_name"] = room.owner.owner_name
        result["owner_email"] = room.owner.email
        result["owner_phone"] = room.owner.phone
        
    return result

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_room(
    owner_email: str = Form(...),
    title: str = Form(...),
    location: str = Form(...),
    rent: int = Form(...),
    deposit: int = Form(0),
    room_type: str = Form(...),
    description: str = Form(""),
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
    cctv: bool = Form(False),
    semi_furnished: bool = Form(False),
    gender: str = Form("Any"),
    is_available: bool = Form(True),
    files: List[UploadFile] = File(...),
    video_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    if sharing_capacity > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 persons only allowed!")

    owner = db.query(Owner).filter(Owner.email == owner_email).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner email not found!")

    # Base64 Image Processing (Vercel Friendly)
    base64_images = []
    for file in files:
        if file.filename:
            content = await file.read()
            ext = file.filename.split('.')[-1].lower()
            mime = f"image/{ext}" if ext != 'jpg' else "image/jpeg"
            base64_str = f"data:{mime};base64,{base64.b64encode(content).decode()}"
            base64_images.append(base64_str)

    new_room = Room(
        title=title, location=location, rent=rent, room_type=room_type,
        description=description, max_persons=sharing_capacity,
        bachelor_allowed=bachelor_allowed, wifi=wifi, ac=ac, 
        attached_bath=attached_bath, deposit=deposit,
        kitchen_access=kitchen_access, parking=parking, laundry=laundry,
        security=security, gym=gym, cctv=cctv, 
        semi_furnished=semi_furnished, gender=gender,
        image_url=base64_images,
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
    rent: int = Form(...),
    deposit: int = Form(0),
    room_type: str = Form(...),
    description: str = Form(""),
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
    cctv: bool = Form(False),
    semi_furnished: bool = Form(False),
    gender: str = Form("Any"),
    is_available: bool = Form(True),
    files: List[UploadFile] = File(None),
    video_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    owner = db.query(Owner).filter(Owner.email == owner_email).first()
    if not owner or room.owner_id != owner.id:
        raise HTTPException(status_code=403, detail="Owner email mismatch!")

    if files:
        base64_images = []
        for file in files:
            if file.filename:
                content = await file.read()
                ext = file.filename.split('.')[-1].lower()
                mime = f"image/{ext}" if ext != 'jpg' else "image/jpeg"
                base64_str = f"data:{mime};base64,{base64.b64encode(content).decode()}"
                base64_images.append(base64_str)
        room.image_url = base64_images

    room.title = title
    room.location = location
    room.rent = rent
    room.deposit = deposit
    room.room_type = room_type
    room.max_persons = sharing_capacity
    room.description = description
    room.bachelor_allowed = bachelor_allowed
    room.wifi = wifi
    room.ac = ac
    room.attached_bath = attached_bath
    room.kitchen_access = kitchen_access
    room.parking = parking
    room.laundry = laundry
    room.security = security
    room.gym = gym
    room.cctv = cctv
    room.semi_furnished = semi_furnished
    room.gender = gender
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