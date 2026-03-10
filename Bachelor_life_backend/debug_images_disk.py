import os
import json
from db.database import SessionLocal
from models.room_models import Room

db = SessionLocal()
rooms = db.query(Room).all()

# Get absolute path of static folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static", "room_images")

print(f"Checking images in: {STATIC_DIR}")
print("-" * 50)

disk_files = os.listdir(STATIC_DIR)
print(f"Files on disk: {disk_files}")
print("-" * 50)

for room in rooms:
    print(f"ID: {room.id}, Title: {room.title}")
    raw_images = room.image_url
    print(f"  Raw image_url field value: {repr(raw_images)}")
    
    images = []
    if isinstance(raw_images, list):
        images = raw_images
    elif isinstance(raw_images, str):
        try:
            images = json.loads(raw_images.replace("'", '"'))
        except Exception as e:
            print(f"  [!] String parsing error: {e}")
            images = [raw_images]
    
    if not images:
        print(" [!] No images found in this record.")
        continue

    for img in images:
        if not img: continue
        print(f"  Analyzing image entry: {repr(img)}")
        if img.startswith("data:"):
            print("  - Base64 data (should display normally)")
            continue
        
        # Clean the path
        # If the path in DB is "static/room_images/Screenshot 2026-01-09 110427.png"
        # We need to see if it exists.
        
        # Try relative to STATIC_DIR
        clean_img = img.replace("\\", "/").split("/")[-1] # Just get the filename
        file_path = os.path.join(STATIC_DIR, clean_img)
        exists = os.path.exists(file_path)
        print(f"  - Check file: {clean_img} -> {'EXISTS' if exists else 'MISSING'}")
        
        if not exists:
            # Maybe the path is relative to the backend root?
            root_path = os.path.join(BASE_DIR, img.replace("\\", "/"))
            if os.path.exists(root_path):
                print(f"    [!] Found relative to root: {img}")
            else:
                print(f"    [X] Not found at: {file_path}")
                print(f"    [X] Not found at: {root_path}")

print("-" * 50)
db.close()
