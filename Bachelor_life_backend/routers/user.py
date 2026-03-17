from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.user_models import Customer  # Correct Model-ah import pannunga
from schema.user_schema import UserCreate, UserResponse, LoginRequest
from core.security import get_password_hash, verify_password
from typing import List

router = APIRouter(prefix="/user", tags=["User"])

# 1. Create User
@router.post("/", response_model=UserResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.email == data.email).first()
    if existing:
        raise HTTPException(400, "User email already exists")

    hashed_pwd = get_password_hash(data.password)

    new_user = Customer( 
        name=data.name,
        phone=data.phone,
        email=data.email,
        gender=data.gender,
        hashed_password=hashed_pwd
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        db.rollback()
        # Log the error for debugging
        print(f"DEBUG: signup error: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

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

# 5. User Login
@router.post("/login")
def login_user(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Customer).filter(Customer.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Try hash verification first
    try:
        is_verified = verify_password(data.password, user.hashed_password)
    except Exception:
        # Fallback to plain text for legacy data
        is_verified = (data.password == user.hashed_password)

    if not is_verified:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone
        }
    }