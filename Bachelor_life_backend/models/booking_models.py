from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, UniqueConstraint
from db.database import Base
import datetime

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String, default="Interested")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (UniqueConstraint('room_id', 'user_id', name='_user_room_uc'),)

    room = relationship("Room", back_populates="bookings")