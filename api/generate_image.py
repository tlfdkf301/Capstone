import os
import uuid
import base64
import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.user_image import UserImage
from database import get_db
from pydantic import BaseModel
from models.clothes import Clothes
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

SEGMIND_API_KEY_BOTTOM = os.getenv("SEGMIND_API_KEY_BOTTOM")
SEGMIND_API_KEY_TOP = os.getenv("SEGMIND_API_KEY_TOP")
SEGMIND_API_URL = "https://api.segmind.com/v1/try-on-diffusion"
print(SEGMIND_API_KEY_BOTTOM)
print(SEGMIND_API_KEY_BOTTOM)
class GenerateImageRequest(BaseModel):
    user_image_id: str
    top_id: int
    bottom_id: int

@router.post("/generate-image")
def generate_image(req: GenerateImageRequest, db: Session = Depends(get_db)):
    # 1. 유저 이미지 조회
    user_img = db.query(UserImage).filter_by(image_id=req.user_image_id).first()
    if not user_img or not os.path.exists(user_img.image_url.lstrip("/")):
        raise HTTPException(status_code=404, detail="User image not found")
    

    user_image_path = user_img.image_url.lstrip("/")

    top = db.query(Clothes).filter_by(id=req.top_id).first()
    bottom = db.query(Clothes).filter_by(id=req.bottom_id).first()

    if not top or not bottom:
        raise HTTPException(status_code=404, detail="Top or bottom image file not found")

    top_path = top.image_url.lstrip("/")
    bottom_path = bottom.image_url.lstrip("/")

    # 2. 이미지 base64 인코딩 함수 내부에 직접 작성
    def to_base64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    headers_bottom = {"x-api-key": SEGMIND_API_KEY_BOTTOM}
    print("BOTTOM API KEY:", SEGMIND_API_KEY_BOTTOM)
    # 3. 하의 합성 API 호출
    temp_path = f"static/generated/temp_{uuid.uuid4().hex[:6]}.jpg"
    payload1 = {
        "model_image": to_base64(user_image_path),
        "cloth_image": to_base64(bottom_path),
        "category": "Lower body",
        "num_inference_steps": 25,
        "guidance_scale": 2,
        "seed": 12467,
        "base64": False
    }
    res1 = requests.post(SEGMIND_API_URL, json=payload1, headers=headers_bottom)
    if res1.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Bottom merge failed: {res1.text}")
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(res1.content)

    headers_top = {"x-api-key": SEGMIND_API_KEY_TOP}
    print("TOP API KEY:", SEGMIND_API_KEY_TOP)
    # 4. 상의 합성 API 호출
    final_id = f"outfit_{uuid.uuid4().hex[:6]}"
    final_path = f"static/generated/{final_id}.jpg"
    payload2 = {
        "model_image": to_base64(temp_path),
        "cloth_image": to_base64(top_path),
        "category": "Upper body",
        "num_inference_steps": 25,
        "guidance_scale": 2,
        "seed": 12467,
        "base64": False
    }
    res2 = requests.post(SEGMIND_API_URL, json=payload2, headers=headers_top)
    if res2.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Top merge failed: {res2.text}")
    with open(final_path, "wb") as f:
        f.write(res2.content)


    return {
        "image_id": final_id,
        "generated_image_url": f"/static/generated/{final_id}.jpg"
    }