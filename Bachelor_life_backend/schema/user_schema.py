from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    name: str 
    phone: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(BaseModel):
    id: int
    name: str  
    email: EmailStr
    phone: str

    class Config:
        from_attributes = True 