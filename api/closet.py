from fastapi import APIRouter, UploadFile, File, Form
from typing import List

router = APIRouter()

@router.post("/closet/upload")
async def upload_clothes(
    image: UploadFile = File(...),
    user_id: str = Form(...)
):
    # 이미지 저장, AI 호출, DB 저장
    return {"message": "옷 업로드 성공", "user_id": user_id}

@router.get("/closet/")
def get_closet(user_id: str):
    # 유저별 옷장 JSON 반환
    return {"items": []}