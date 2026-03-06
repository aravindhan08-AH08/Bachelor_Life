from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any 

class OwnerBase(BaseModel):
    owner_name: str
    phone: str
    email: EmailStr

class OwnerCreate(OwnerBase):
    password: str 

class OwnerResponse(OwnerBase):
    id: int
    class Config:
        from_attributes = True 

class OwnerDashboardResponse(BaseModel):
    owner_name: str
    total_rooms: int
    rooms: List[dict] 
    bookings_received: List[dict]

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True 

class RoomBase(BaseModel):
    room_name: str
    price: int
    deposit: int = 0 

class RoomCreate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int
    owner_id: int
    class Config:
        from_attributes = True