from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, JSON 
from sqlalchemy.orm import relationship
from db.database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    location = Column(String)
    deposit = Column(Integer, default=0)
    rent = Column(Integer)
    room_type = Column(String)
    description = Column(String)
    bachelor_allowed = Column(Boolean, default=True)
    max_persons = Column(Integer, default=1)
    is_approved = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("owners.id"))
    
    # Amenities
    wifi = Column(Boolean, default=False)
    ac = Column(Boolean, default=False)
    attached_bath = Column(Boolean, default=False)
    kitchen_access = Column(Boolean, default=False)
    parking = Column(Boolean, default=False)
    laundry = Column(Boolean, default=False)
    security = Column(Boolean, default=False)
    gym = Column(Boolean, default=False)
    cctv = Column(Boolean, default=False)
    semi_furnished = Column(Boolean, default=False)
    gender = Column(String, default="Any")
    image_url = Column(JSON, nullable=True)

    owner = relationship("Owner", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")