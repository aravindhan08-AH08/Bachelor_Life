from pydantic import BaseModel
from typing import Optional, List # List import sethukonga

class RoomCreate(BaseModel):
    title: str
    location: str
    rent: int
    deposit: int
    room_type: str
    description: str
    # Idhu dhaan sharing limit (1 to 4)
    max_persons: int = 1
    bachelor_allowed: bool = True
    wifi: bool = False
    ac: bool = False
    attached_bath: bool = False
    kitchen_access: bool = False
    parking: bool = False
    laundry: bool = False
    security: bool = False
    gym: bool = False

class RoomResponse(RoomCreate):
    id: int
    is_approved: bool
    is_available: bool
    image_url: Optional[List[str]] = None
    
    class Config:
        from_attributes = True