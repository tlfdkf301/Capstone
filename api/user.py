import os
import uuid
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
from database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from models.user_image import UserImage
router = APIRouter()

# 저장 디렉토리 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
UPLOAD_DIR = os.path.join(PROJECT_DIR, "static","user_images")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/user/image")
async def upload_user_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    image_id = f"user_{uuid.uuid4().hex[:8]}"
    file_ext = os.path.splitext(image.filename)[-1] or ".jpg"
    filename = f"{image_id}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await image.read())

    image_url = f"/static/user_images/{filename}"

    # ✅ DB에 저장
    user_image = UserImage(image_id=image_id, image_url=image_url)
    db.add(user_image)
    db.commit()

    return {
        "image_id": image_id,
        "image_url": image_url
    }

@router.get("/user/recentimage")
def get_latest_user_image(db: Session = Depends(get_db)):
    image = db.query(UserImage).order_by(UserImage.created_at.desc()).first()
    if not image:
        raise HTTPException(status_code=404, detail="No image found")
    return {
        "image_id": image.image_id,
        "image_url": image.image_url
    }