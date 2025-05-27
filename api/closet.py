from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models.clothes import Clothes
from pydantic import BaseModel
from typing import Optional, Dict, List
from core.response_utils import format_clothes_response

router = APIRouter()

# 1. 전체 조회
@router.get("/closet")
def get_all_clothes(db: Session = Depends(get_db)):
    clothes = db.query(Clothes).filter(Clothes.user_id == 1).all()
    return [format_clothes_response(c) for c in clothes]

# 2. 상세 조회
@router.get("/closet/{item_id}")
def get_clothing_detail(item_id: int, db: Session = Depends(get_db)):
    clothing = db.query(Clothes).filter(Clothes.id == item_id).first()
    if not clothing:
        raise HTTPException(status_code=404, detail="해당 옷이 없습니다.")
    return clothing

# 3. 수정
class ClothesUpdateRequest(BaseModel):
    item_id: int
    color: Optional[str]
    fit: Optional[str]
    length: Optional[str]
    material: Optional[str]
    sleeve_length: Optional[str]
    collar: Optional[str]
    style_probs: Optional[Dict[str, float]]

@router.post("/closet/edit")
def edit_clothing(data: ClothesUpdateRequest, db: Session = Depends(get_db)):
    clothing = db.query(Clothes).filter(Clothes.id == data.item_id).first()
    if not clothing:
        raise HTTPException(status_code=404, detail="해당 옷이 없습니다.")

    update_fields = data.dict(exclude_unset=True)
    update_fields.pop("item_id")
    for key, value in update_fields.items():
        setattr(clothing, key, value)

    db.commit()
    db.refresh(clothing)
    return clothing

@router.delete("/closet/{item_id}")
def delete_clothing(item_id: int, db: Session = Depends(get_db)):
    clothing = db.query(Clothes).filter(Clothes.id == item_id).first()
    if not clothing:
        raise HTTPException(status_code=404, detail="해당 옷이 없습니다.")

    db.delete(clothing)
    db.commit()
    return {"message": "삭제 완료", "item_id": item_id}

@router.get("/closet/frequent", response_model=List[Clothes])
async def get_frequent_clothes(limit: int = Query(10, gt=0, le=100)):
    """
    이름은 frequent지만, 실제로는
    created_at 내림차순(최근 추가순)으로 limit 개수만큼 반환합니다.
    """
    # 전체 아이템 불러오기
    all_items: List[Clothes] = get_all_clothes()

    # created_at 으로 정렬 (datetime 혹은 ISO 문자열 비교)
    sorted_items = sorted(
        all_items,
        key=lambda item: item.created_at,
        reverse=True
    )
    return sorted_items[:limit]