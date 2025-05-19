from fastapi import APIRouter, Query

router = APIRouter()

@router.get("/recommendation/")
def recommend(
    selected_item_id: str = Query(...),
    tpo: str = Query(...),
    user_id: str = Query(...)
):
    # 스타일 예측 → TPO 점수 + 유사도 점수 → 추천
    return {"recommended_items": ["o1", "b2"]}