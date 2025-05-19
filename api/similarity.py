from fastapi import APIRouter
from pydantic import BaseModel
import json

router = APIRouter()

@router.get("/similarity_table/")
def get_similarity():
    with open("data/similarity_table.json", "r") as f:
        data = json.load(f)
    return data

class UpdateRequest(BaseModel):
    new_item_id: str

@router.post("/update_similarity/")
def update_similarity(req: UpdateRequest):
    # 기존 JSON 불러와서 유사도 갱신
    return {"message": "similarity table updated", "new_scores": {}}