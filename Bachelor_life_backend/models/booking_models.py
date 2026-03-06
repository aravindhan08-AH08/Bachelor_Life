from sqlalchemy.orm import relationship 
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from db.database import Base
import datetime

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String, default="Interested")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    room = relationship("Room", back_populates="bookings")