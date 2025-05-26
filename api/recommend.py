import core.closet_utils
print(dir(core.closet_utils))  # get_user_clothes가 뜨는지 확인
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from database import get_db
from core.closet_utils import get_user_clothes, get_selected_clothing
from core.preprocessing_utils import apply_style_predictions
# from core.dmlp_predictor import predict_top3_tpo, model, mlb, LABEL_MAP
from core.dmlp_predictor import predict_top3_tpo, model, mlb, LABEL_MAP
from core.score_utils import calculate_tpo_scores, merge_scores_global_standardization, sort_items_by_score, tpo_score_table
from core.apriori_utils import score_recommendation_dict_sorted_key
from core.recommend_utils import run_recommendation  # 추천 로직 함수

router = APIRouter()

# 요청 스키마
class RecommendationRequest(BaseModel):
    selected_item_id: str  # 예: "상의_103"
    tpo: str               # 예: "데이트"

# 응답 스키마
class RecommendedItem(BaseModel):
    category: str
    item_ids: List[str]

class RecommendationResponse(BaseModel):
    recommend_id: str
    selected: Dict[str, Any]
    recommendations: Dict[str, List[Dict[str, Any]]]

@router.post("/recommend", response_model=RecommendationResponse)
def recommend_clothes(req: RecommendationRequest, request: Request, db: Session = Depends(get_db)):
    # 1. 룰 테이블 (전역 상태에서 가져옴)
    color_dict = request.app.state.color_dict
    feature_dict = request.app.state.feature_dict

    # 2. 옷장 불러오기
    user_clothes = get_user_clothes(user_id=1, db=db)

    # 3. 스타일 예측 적용
    user_clothes = apply_style_predictions(user_clothes, model, mlb, LABEL_MAP)

    # 4. 선택 옷 가져오기
    selected_clothing = get_selected_clothing(req.selected_item_id, db)
    if not selected_clothing:
        raise HTTPException(status_code=404, detail="선택한 옷을 찾을 수 없습니다.")

    # 5. 추천 실행
    result_dict = run_recommendation(
        selected_tpo=req.tpo,
        selected_clothing=selected_clothing,
        color_dict=color_dict,
        feature_dict=feature_dict,
        user_clothes=user_clothes,
        tpo_score_table=tpo_score_table
    )

    return RecommendationResponse(
        recommend_id="r001",  # 추후 고유 ID 생성 로직으로 대체 가능
        selected=selected_clothing,
        recommendations=result_dict
    )