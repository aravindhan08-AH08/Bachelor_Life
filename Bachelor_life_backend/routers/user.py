from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.user_models import Customer  # Correct Model-ah import pannunga
from schema.user_schema import UserCreate, UserResponse
from core.security import get_password_hash
from typing import List

router = APIRouter(prefix="/user", tags=["User"])

# 1. Create User
@router.post("/", response_model=UserResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.email == data.email).first()
    if existing:
        raise HTTPException(400, "User email already exists")

    hashed_pwd = get_password_hash(data.password)

    new_user = Customer( # This is use the User model or table
        name=data.name,
        phone=data.phone,
        email=data.email,
        hashed_password=hashed_pwd
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# 2. Get All Users
@router.get("/", response_model=List[UserResponse])
def get_all_user(db: Session = Depends(get_db)):
    users = db.query(Customer).all()

    return users

# 3. Get User by ID
@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(Customer).filter(Customer.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not Found")
    return user

# 4. Update User
@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(Customer).filter(Customer.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not Found")

    
    user.name = data.name
    user.phone = data.phone
    user.email = data.email
    
    if data.password:
        user.hashed_password = get_password_hash(data.password)

    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Update failed")