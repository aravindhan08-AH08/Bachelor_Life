import os
import json
from db.database import SessionLocal
from models.room_models import Room

db = SessionLocal()
rooms = db.query(Room).all()

# Get absolute path of static folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static", "room_images")

print(f"Syncing database image paths with disk in: {STATIC_DIR}")
print("-" * 50)

disk_files = {f.lower(): f for f in os.listdir(STATIC_DIR)}

updated_count = 0

for room in rooms:
    raw_images = room.image_url
    if not raw_images: continue
    
    images = []
    if isinstance(raw_images, list):
        images = raw_images
    elif isinstance(raw_images, str):
        try:
            images = json.loads(raw_images.replace("'", '"'))
        except:
            images = [raw_images]
    
    new_images = []
    modified = False
    
    for img in images:
        if not img or img.startswith("data:"):
            new_images.append(img)
            continue
        
        # Get filename
        filename = img.replace("\\", "/").split("/")[-1]
        
        # Check if it exists as is
        if os.path.exists(os.path.join(STATIC_DIR, filename)):
            new_images.append(f"static/room_images/{filename}")
            continue
            
        # Try space -> underscore
        alt1 = filename.replace(" ", "_")
        if alt1.lower() in disk_files:
            new_images.append(f"static/room_images/{disk_files[alt1.lower()]}")
            modified = True
            continue
            
        # Try underscore -> space
        alt2 = filename.replace("_", " ")
        if alt2.lower() in disk_files:
            new_images.append(f"static/room_images/{disk_files[alt2.lower()]}")
            modified = True
            continue
            
        # If still not found, keep as is
        new_images.append(img)

    if modified:
        room.image_url = new_images
        print(f"Updated Room {room.id}: {new_images}")
        updated_count += 1

if updated_count > 0:
    db.commit()
    print(f"Successfully updated {updated_count} rooms.")
else:
    print("No updates needed.")

db.close()
