from fastapi import APIRouter, UploadFile, File
import os
from uuid import uuid4

router = APIRouter()

UPLOAD_DIR = "static/images"

@router.post("/upload_clothes/")
async def upload_clothes(image: UploadFile = File(...)):
    # 파일 확장자 추출
    ext = os.path.splitext(image.filename)[-1]

    # 고유한 파일명 생성 (UUID 사용)
    filename = f"{uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    #파일 저장
    with open(file_path, "wb") as buffer:
        content = await image.read()
        buffer.write(content)

    return {"filename": filename, "url":f"/static/images/{filename}"}