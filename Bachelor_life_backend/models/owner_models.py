from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.database import Base

class Owner(Base):
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True, index=True)
    owner_name = Column(String)
    phone = Column(String)
    email = Column(String, unique=True)
    gender = Column(String, nullable=True) # Adding gender
    hashed_password = Column(String)
    
    rooms = relationship("Room", back_populates="owner")