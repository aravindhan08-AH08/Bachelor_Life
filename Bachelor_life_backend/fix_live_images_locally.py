import os
import base64
import json
from sqlalchemy import text
from db.database import SessionLocal
from models.room_models import Room

db = SessionLocal()

def convert_to_b64_locally():
    print("--- LIVE PRODUCTION DATABASE IMAGE FIXER (LOCAL RUN) ---")
    print("Reading rooms from the database...")
    
    rooms = db.query(Room).all()
    fixed_count = 0
    
    for room in rooms:
        raw = room.image_url
        if not raw: continue
        
        # Normalize to list
        images = []
        if isinstance(raw, list):
            images = raw
        elif isinstance(raw, str):
            try:
                images = json.loads(raw.replace("'", '"'))
            except:
                images = [raw]
        else:
            images = [str(raw)]

        # Process each image in the list
        new_images = []
        changed = False
        
        for img_path in images:
            img_path = str(img_path).strip().replace('\\', '/')
            
            # If it's already Base64 or URL, keep it
            if img_path.startswith("data:") or img_path.startswith("http"):
                new_images.append(img_path)
                continue
                
            # It's a local path like 'static/room_images/abc.jpg'
            # Try to find it on THIS computer
            # Paths might be relative to Bachelor_life_backend or Bachelor-life
            search_paths = [
                img_path, # Try literal
                os.path.join("Bachelor_life_backend", img_path),
                os.path.join("..", img_path),
                os.path.join("..", "Bachelor_life_backend", img_path)
            ]
            
            found_data = None
            for p in search_paths:
                if os.path.exists(p) and os.path.isfile(p):
                    print(f"  - Found file locally: {p}")
                    with open(p, "rb") as f:
                        file_data = f.read()
                        b64 = base64.b64encode(file_data).decode('utf-8')
                        ext = os.path.splitext(p)[1].replace('.', '') or "jpeg"
                        found_data = f"data:image/{ext};base64,{b64}"
                        break
            
            if found_data:
                new_images.append(found_data)
                changed = True
            else:
                # File not found on this computer either
                print(f"  ! Warning: File {img_path} not found on this computer. Keeping as is.")
                new_images.append(img_path)

        if changed:
            room.image_url = new_images
            fixed_count += 1
            print(f"  - FIXED Room {room.id} ({room.title})")

    if fixed_count > 0:
        db.commit()
        print(f"\nSUCCESS! Fixed {fixed_count} rooms in the production database with actual image data.")
    else:
        print("\nNo local file paths found in the database or all files were already fixed.")

    db.close()

if __name__ == "__main__":
    convert_to_b64_locally()
