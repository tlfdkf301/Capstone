from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from models.clothes import Clothes
from database import get_db
import uuid
import shutil
import os

# YOLO, ResNet 모델 import
from models.yolo import run_yolo
from models.resnet import run_resnet
from core.feature_mapper import map_ai_attributes_to_features

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/closet/upload")
def upload_clothing_image(
    image: UploadFile = File(...),
    # category: str = Form(...),  # top, bottom, outer, dress
    db: Session = Depends(get_db)
):
    # 1. 이미지 저장
    filename = f"{uuid.uuid4().hex}_{image.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    image_url = f"/static/uploads/{filename}"  # 프론트 전달용

    # 2. AI 서버 호출 
    try:
        category_result = run_yolo(file_path)  
    except Exception as e:
        return {"error": f"YOLO 예측 실패: {str(e)}"}

    try:
        attributes = run_resnet(file_path)
    except Exception as e:
        return {"error": f"ResNet 예측 실패: {str(e)}"}
    
    features = map_ai_attributes_to_features(attributes)

    # 3. DB 저장
    new_clothes = Clothes(
        user_id=1,
        maincategory=category_result["mainCategory"],
        category=category_result["category"],
        image_url=image_url,
        color=attributes.get("color"),
        fit=attributes.get("pants_silhouette"),  # 예시: 하의 silhouette을 fit에 매핑
        length=attributes.get("top_length"),
        material=attributes.get("fiber"),
        sleeve_length=attributes.get("sleeve_length"),
        collar=None,  # AI가 collar 예측하지 않으면 None
        style_probs=None
    )

    db.add(new_clothes)
    db.commit()
    db.refresh(new_clothes)

    return new_clothes