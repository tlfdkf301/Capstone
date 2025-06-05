from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
from PIL import Image
from database import get_db
from models.recommendation import RecommendationHistory
from models.clothes import Clothes
from core.closet_utils import get_user_clothes, get_selected_clothing, get_selected_clothing2
from core.preprocessing_utils import apply_style_predictions
from core.dmlp_predictor import model, mlb, LABEL_MAP
from core.score_utils import tpo_score_table
from core.recommend_utils import run_recommendation
from core.response_utils import format_clothes_response
from core.ai_label_to_kfashion import maincategory_map
import json
import uuid
import os
router = APIRouter()

class RecommendImageUpdateRequest(BaseModel):
    imageUrl: str

class RecommendationRequest(BaseModel):
    selected_item_id: int
    tpo: str

class RecommendationResponse(BaseModel):
    id: int
    imageUrl: str
    description: str
    clothingIds: List[int]
    tpo: str
    created_at: str

class RecommendEditRequest(BaseModel):
    description: str

class RecommendEditResponse(BaseModel):
    result: str

class RecommendItem(BaseModel):
    id: int
    imageUrl: str
    description: str
    clothingIds: List[int]
    tpo: str
    created_at: str

@router.post("/recommend", response_model=RecommendationResponse)
def recommend_clothes(req: RecommendationRequest, request: Request, db: Session = Depends(get_db)):
    color_dict = request.app.state.color_dict
    feature_dict = request.app.state.feature_dict

    user_clothes = get_user_clothes(db=db)
    print("✅ [DEBUG] 선택된 item_id:", req.selected_item_id)
    print("✅ [DEBUG] user_clothes 구조:")
    for cat, items in user_clothes.items():
        print(f"  - {cat}: {[item[0] for item in items]}")

    user_clothes = apply_style_predictions(user_clothes, model, mlb, LABEL_MAP)
    selected_clothing = get_selected_clothing(str(req.selected_item_id), db)
    if not selected_clothing:
        raise HTTPException(status_code=404, detail="선택한 옷을 찾을 수 없습니다.")
    
    test1 = get_selected_clothing2(str(req.selected_item_id), db)
    


    result_dict = run_recommendation(
        selected_tpo=req.tpo,
        selected_clothing=test1,
        color_dict=color_dict,
        feature_dict=feature_dict,
        user_clothes=user_clothes,
        tpo_score_table=tpo_score_table
    )

    auto_description = f"{req.tpo}_TPO_추천{uuid.uuid4().hex[:8]}" # 추천description 자동생성

    flattened_item_ids = []
    for item_list in result_dict.values():
        for item_id in item_list:
            raw_id = item_id.split('_')[-1]
            flattened_item_ids.append(raw_id)

    selected_raw_id = str(req.selected_item_id).split('_')[-1]
    clothingIds = [int(selected_raw_id)] + [int(i) for i in flattened_item_ids]

    new_history = RecommendationHistory(
        selected_item_id=req.selected_item_id,
        tpo=req.tpo,
        clothingIds=clothingIds,
        description=auto_description, # 추천 description 자동생성
        created_at=datetime.utcnow()
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    # DB에서 전체 옷 목록 조회해서 매핑
    clothes_list = db.query(Clothes).all()
    clothes_dict = {str(item.id): item for item in clothes_list}

    UPLOAD_DIR = "static/uploads"  # 기존 옷 이미지 저장 경로
    RECOMMEND_DIR = "static/recommend"
    os.makedirs(RECOMMEND_DIR, exist_ok=True)
    
    grid_image = Image.new("RGB", (400, 400), color="white")
    positions = [(0, 0), (200, 0), (0, 200),(200,200)]
    for i, item_id in enumerate(clothingIds[:4]):
        item_obj = clothes_dict.get(str(item_id))
        if item_obj.image_url!=None:
            image_filename = os.path.basename(item_obj.image_url)
            full_path = os.path.join(UPLOAD_DIR, image_filename)
            if os.path.exists(full_path):
                img = Image.open(full_path).resize((200, 200))
                grid_image.paste(img, positions[i])

    image_filename = f"recommend_{new_history.id}.png"
    image_path = os.path.join(RECOMMEND_DIR, image_filename)
    grid_image.save(image_path)

    # ✅ 절대 URL 생성
    image_url = str(request.url_for("static", path=f"recommend/{image_filename}"))
    new_history.imageUrl = image_url
    db.commit()
    return {
        "id": new_history.id,
        "imageUrl": image_url,
        "description": auto_description,
        "clothingIds": clothingIds,
        "tpo": req.tpo,
        "created_at": new_history.created_at.strftime("%Y-%m-%dT%H:%M:%S")
    }

@router.get("/recommend/history")
def get_recommendation_history(db: Session = Depends(get_db)):
    history = (
        db.query(RecommendationHistory)
        .order_by(RecommendationHistory.created_at.desc())
        .all()
    )

    return [
        {
            "id": r.id,
            "selected_item_id": r.selected_item_id,
            "description":r.description,
            "tpo": r.tpo,
            "clothingIds": r.clothingIds,
            "imageUrl":r.imageUrl,
            "created_at": r.created_at.isoformat()
        } for r in history
    ]
    
@router.get("/recommend/{recommend_id}")
def get_single_recommendation(
    recommend_id: int,
    db: Session = Depends(get_db)
):
    recommendation = db.query(RecommendationHistory).filter_by(id=recommend_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="추천 기록을 찾을 수 없습니다.")
    
    def extract_ids(clothing_data):
        if isinstance(clothing_data, list):
            return [int(i) for i in clothing_data]
        elif isinstance(clothing_data, dict):
            ids = []
            for sublist in clothing_data.values():
                for val in sublist:
                    raw = val.split('_')[-1]
                    ids.append(int(raw))
            return ids
        return []

    return {
        "id": recommendation.id,
        "imageUrl": recommendation.imageUrl or "",
        "description": recommendation.description or "",
        "clothingIds": extract_ids(recommendation.clothingIds),
        "tpo": recommendation.tpo,
        "created_at": recommendation.created_at.strftime("%Y-%m-%dT%H:%M:%S")
    } 

@router.post("/recommend/edit/{recommend_id}", response_model=RecommendEditResponse)
def edit_recommend_description(
    recommend_id: int,
    body: RecommendEditRequest,  # ✅ 바디를 Pydantic 모델로 받음
    db: Session = Depends(get_db)
):
    recommendation = db.query(RecommendationHistory).filter_by(id=recommend_id).first()
    print(recommendation)
    if not recommendation:
        raise HTTPException(status_code=404, detail="추천 기록 없음")

    recommendation.description = body.description
    db.commit()
    return {"result": "ok"}

@router.post("/recommend/update-image/{recommend_id}", response_model=RecommendItem)
def update_recommend_image(
    recommend_id: int,
    body: RecommendImageUpdateRequest,
    db: Session = Depends(get_db)
):
    recommendation = db.query(RecommendationHistory).filter_by(id=recommend_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="추천 항목을 찾을 수 없습니다.")

    recommendation.imageUrl = body.imageUrl 
    db.commit()
    db.refresh(recommendation)

    def extract_ids(clothing_data):
        if isinstance(clothing_data, list):
            return [int(i) for i in clothing_data]
        elif isinstance(clothing_data, dict):
            ids = []
            for sublist in clothing_data.values():
                for val in sublist:
                    raw = val.split('_')[-1]
                    ids.append(int(raw))
            return ids
        return []

    return {
        "id": recommendation.id,
        "imageUrl": recommendation.imageUrl or "",
        "description": recommendation.description or "",
        "clothingIds": extract_ids(recommendation.clothingIds),
        "tpo": recommendation.tpo,
        "created_at": recommendation.created_at.strftime("%Y-%m-%dT%H:%M:%S")
    }