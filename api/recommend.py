from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db
from models.recommendation import RecommendationHistory
from core.closet_utils import get_user_clothes, get_selected_clothing
from core.preprocessing_utils import apply_style_predictions
from core.dmlp_predictor import model, mlb, LABEL_MAP
from core.score_utils import tpo_score_table
from core.recommend_utils import run_recommendation
from core.response_utils import format_clothes_response

router = APIRouter()

# 요청 모델
class RecommendationRequest(BaseModel):
    selected_item_id: str  # 예: "outer_12"
    tpo: str               # 예: "데이트"

# 응답 모델
class RecommendationResponse(BaseModel):
    recommend_id: str
    selected: Dict[str, Any]
    recommendations: Dict[str, List[Dict[str, Any]]]

# 추천 실행 API
@router.post("/recommend", response_model=RecommendationResponse)
def recommend_clothes(req: RecommendationRequest, request: Request, db: Session = Depends(get_db)):
    # 1. 전역 룰 테이블 불러오기
    color_dict = request.app.state.color_dict
    feature_dict = request.app.state.feature_dict

    # 2. 옷장 전체 불러오기
    user_clothes = get_user_clothes(user_id=1, db=db)

    # 3. 스타일 예측 (style_probs 없으면 예측)
    user_clothes = apply_style_predictions(user_clothes, model, mlb, LABEL_MAP)

    # 4. 선택된 옷 가져오기
    selected_clothing = get_selected_clothing(req.selected_item_id, db)
    if not selected_clothing:
        raise HTTPException(status_code=404, detail="선택한 옷을 찾을 수 없습니다.")

    # 5. 추천 알고리즘 실행
    result_dict = run_recommendation(
        selected_tpo=req.tpo,
        selected_clothing=selected_clothing,
        color_dict=color_dict,
        feature_dict=feature_dict,
        user_clothes=user_clothes,
        tpo_score_table=tpo_score_table
    )

    # 6. 추천 결과 저장
    new_history = RecommendationHistory(
        user_id=1,
        selected_item_id=req.selected_item_id,
        tpo=req.tpo,
        recommended_items=result_dict,
        created_at=datetime.utcnow()
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)


    # 응답 포맷 가공
    formatted_result = {
        cat: [format_clothes_response(item) for item in items]
        for cat, items in result_dict.items()
    }

    formatted_selected = format_clothes_response(selected_clothing)

    return {
        "recommend_id": str(new_history.id),
        "selected": formatted_selected,
        "tpo": req.tpo,
        "recommendations": [
            {"mainCategory": cat, "items": formatted_result[cat]} for cat in formatted_result
        ]
    }

# 추천 기록 조회 API
@router.get("/recommend/history")
def get_recommendation_history(db: Session = Depends(get_db)):
    history = (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.user_id == 1)
        .order_by(RecommendationHistory.created_at.desc())
        .all()
    )

    return [
        {
            "recommend_id": r.id,
            "selected_item_id": r.selected_item_id,
            "tpo": r.tpo,
            "recommendations": r.recommended_items,
            "created_at": r.created_at.isoformat()
        }
        for r in history
    ]
