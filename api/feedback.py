from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Feedback(BaseModel):
    user_id: str
    selected_item_id: str
    recommended: List[str]
    selected: List[str]
    tpo: str

@router.post("/feedback/")
def save_feedback(feedback: Feedback):
    # DB 또는 파일에 저장
    return {"feedback_saved": True}