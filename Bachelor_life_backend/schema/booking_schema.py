from pydantic import BaseModel

class BookingCreate(BaseModel):
    room_id: int
    user_id: int 

class BookingResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    status: str
    owner_name: str
    owner_phone: str
    
    class Config:
        from_attributes = True