from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from models.clothes import Clothes
from database import get_db
import uuid
import shutil
import os

# YOLO, ResNet 모델 import
from models.yolo import run_yolo
from models.resnet import run_resnet

# 속성 매핑
from core.feature_mapper import (
    map_ai_attributes_to_features,           # 스타일 점수화용
    map_ai_attributes_to_kfashion_dict       # DB 저장용 한글 변환
)
from core.ai_label_to_kfashion import category_map, maincategory_map  # ✅ 카테고리 한글 매핑

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
UPLOAD_DIR = os.path.join(PROJECT_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/closet/upload")
def upload_clothing_image(
    image: UploadFile = File(...),
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
        raw_maincategory = category_result["mainCategory"]  # ex) 'top'
        raw_category = category_result["category"]          # ex) 't-shirt'

        # ✅ 한글 매핑
        maincategory = maincategory_map.get(raw_maincategory, raw_maincategory)  # ex) '상의'
        category = category_map.get(raw_category, raw_category)                  # ex) '티셔츠'

    except Exception as e:
        return {"error": f"YOLO 예측 실패: {str(e)}"}

    try:
        attributes = run_resnet(file_path)
    except Exception as e:
        return {"error": f"ResNet 예측 실패: {str(e)}"}

    # 3. 속성 매핑
    features = map_ai_attributes_to_features(attributes)        # 스타일 점수화용
    print(features)
    mapped = map_ai_attributes_to_kfashion_dict(attributes)     # DB 저장용 한글 변환

    # 4. DB 저장 (style_probs는 저장하지 않음)
    new_clothes = Clothes(
        maincategory=maincategory,        # ✅ 한글로 저장
        category=category,                # ✅ 한글로 저장
        image_url=image_url,
        color=mapped.get("color"),
        fit=mapped.get("fit"),
        length=mapped.get("length"),
        material=mapped.get("material"),
        sleeve_length=mapped.get("sleeve_length"),
        collar=None,           # AI가 예측 안 하면 None
        style_probs=None       # ✅ 추천 시점에 실시간 예측하므로 저장 안 함
    )

    db.add(new_clothes)
    db.commit()
    db.refresh(new_clothes)

    return new_clothes
