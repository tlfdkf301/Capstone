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
    clothes = db.query(Clothes).all()
    return [format_clothes_response(c) for c in clothes]

@router.get("/closet/frequent")
def get_frequent_clothes(db: Session = Depends(get_db)):
    clothes = db.query(Clothes).all()
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
    # item_id: int
    maincategory: Optional[str]=None
    category: Optional[str] = None
    color: Optional[str] = None
    fit: Optional[str] = None
    length: Optional[str] = None
    material: Optional[str] = None
    sleeve_length: Optional[str] = None
    collar: Optional[str] = None
    # style_probs: Optional[Dict[str, float]] = None

# @router.post("/closet/edit")
# def edit_clothing(data: ClothesUpdateRequest, db: Session = Depends(get_db)):
#     clothing = db.query(Clothes).filter(Clothes.id == data.item_id).first()
#     if not clothing:
#         raise HTTPException(status_code=404, detail="해당 옷이 없습니다.")

#     update_fields = data.dict(exclude_unset=True)
#     update_fields.pop("item_id")
#     for key, value in update_fields.items():
#         setattr(clothing, key, value)

#     db.commit()
#     db.refresh(clothing)
#     return clothing


# @router.patch("/closet/{item_id}")
# def edit_clothes(item_id: int, update: ClothesUpdateRequest, db: Session = Depends(get_db)):
#     clothes = db.query(Clothes).get(item_id)
#     if not clothes:
#         raise HTTPException(status_code=404, detail="Item not found")

#     for field, value in update.dict(exclude_unset=True).items():
#         setattr(clothes, field, value)

#     db.commit()
#     db.refresh(clothes)
#     return format_clothes_response(clothes)

@router.patch("/closet/edit/{item_id}")
def edit_clothes(item_id: int, update: ClothesUpdateRequest, db: Session = Depends(get_db)):
    clothes = db.query(Clothes).get(item_id)
    if not clothes:
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in update.dict(exclude_unset=True).items():
        if value == "string":  # placeholder 값은 무시
            continue
        setattr(clothes, field, value)

    db.commit()
    db.refresh(clothes)
    return format_clothes_response(clothes)

@router.delete("/closet/{item_id}")
def delete_clothing(item_id: int, db: Session = Depends(get_db)):
    clothing = db.query(Clothes).filter(Clothes.id == item_id).first()
    if not clothing:
        raise HTTPException(status_code=404, detail="해당 옷이 없습니다.")

    db.delete(clothing)
    db.commit()
    return {"message": "삭제 완료", "item_id": item_id}