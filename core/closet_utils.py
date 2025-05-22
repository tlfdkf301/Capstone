#DB 테이블 clothes에서 사용자 옷 리스트 조회
#user_clothes = {카테고리: [[id, style_probs, feature1, ...], ...]} 형태로 변환

from sqlalchemy.orm import Session
from models.clothes import Clothes  # SQLAlchemy 모델
from collections import defaultdict

def get_user_clothes(user_id: int, db: Session) -> dict:
    clothes_list = db.query(Clothes).filter(Clothes.user_id == user_id).all()

    user_clothes = defaultdict(list)
    for item in clothes_list:
        item_id = str(item.id)
        category = item.category
        style_probs = item.style_probs or {}
        features = item.features or []
        user_clothes[category].append([item_id, style_probs] + features)

    return dict(user_clothes)

def get_selected_clothing(selected_item_id: str, db: Session) -> list | None:
    """
    예: '상의_103' → DB에서 해당 옷 조회 → [id, style_probs, feature1, ...] 반환
    """
    try:
        category, raw_id = selected_item_id.split("_")
        item_id = int(raw_id)
    except ValueError:
        return None

    item = db.query(Clothes).filter(
        Clothes.id == item_id,
        Clothes.category == category
    ).first()

    if item is None:
        return None

    return [str(item.id), item.style_probs or {}] + (item.features or [])