from db.database import SessionLocal
from models.booking_models import Booking

db = SessionLocal()

# Update statuses
pending_bookings = db.query(Booking).filter(Booking.status == "Pending").all()
for b in pending_bookings:
    b.status = "Requested"

confirmed_bookings = db.query(Booking).filter(Booking.status == "Confirmed").all()
for b in confirmed_bookings:
    b.status = "Approved"

if len(pending_bookings) > 0 or len(confirmed_bookings) > 0:
    db.commit()
    print(f"Updated {len(pending_bookings)} pending to Requested and {len(confirmed_bookings)} confirmed to Approved.")
else:
    print("No booking statuses needed update.")

db.close()
