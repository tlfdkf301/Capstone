from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from models.clothes import Clothes
from database import get_db
import uuid
import shutil
import os

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/closet/upload")
def upload_clothing_image(
    image: UploadFile = File(...),
    category: str = Form(...),  # top, bottom, outer, dress
    db: Session = Depends(get_db)
):
    # 1. 이미지 저장
    filename = f"{uuid.uuid4().hex}_{image.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_url = f"/static/uploads/{filename}"  # 프론트 전달용

    # 2. AI 서버 호출 (여기서는 더미 결과)
    ai_result = {
        "color": "black",
        "fit": "loose",
        "length": "long",
        "material": "cotton",
        "sleeve_length": "long sleeves",
        "collar": "v-neck",
        "style_probs": {
            "casual": 0.6,
            "formal": 0.3,
            "sporty": 0.1
        }
    }

    # 3. DB 저장
    new_clothes = Clothes(
        user_id=1,
        category=category,
        image_url=image_url,
        **ai_result
    )
    db.add(new_clothes)
    db.commit()
    db.refresh(new_clothes)

    return new_clothes