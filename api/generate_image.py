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
import time
load_dotenv()

router = APIRouter()

SEGMIND_API_KEY_BOTTOM = os.getenv("SEGMIND_API_KEY_BOTTOM")
SEGMIND_API_KEY_TOP = os.getenv("SEGMIND_API_KEY_TOP")
SEGMIND_API_URL = "https://api.segmind.com/v1/try-on-diffusion"

class GenerateImageRequest(BaseModel):
    user_image_id: str
    top_id: int
    bottom_id: int

def make_absolute_url(path: str) -> str:
    if path.startswith("http"):
        return path
    return f"http://13.125.42.2:8000{path}"

@router.post("/generate-image")
def generate_image(req: GenerateImageRequest, db: Session = Depends(get_db)):
    print("📥 [합성 요청 시작]")
    print("🔍 요청된 user_image_id:", req.user_image_id)

    # 1. 유저 이미지 조회
    user_img = db.query(UserImage).filter_by(image_id=req.user_image_id).first()
    print("🧩 user_img from DB:", user_img)

    if not user_img:
        print("❌ user_img가 DB에 존재하지 않음!")
        raise HTTPException(status_code=404, detail="User image not found")

    image_url = user_img.image_url
    if image_url.startswith("http"):
        user_image_path = image_url.replace("http://13.125.42.2:8000", "").lstrip("/")
    else:
        user_image_path = image_url.lstrip("/")

    print("📂 user_img.image_url:", image_url)
    print("📂 실제 파일 경로:", user_image_path)
    print("📂 실제 파일 존재 여부:", os.path.exists(user_image_path))

    if not os.path.exists(user_image_path):
        print("❌ 실제 이미지 파일이 존재하지 않음!")
        raise HTTPException(status_code=404, detail="User image not found")

    # 2. 옷 정보 조회
    top = db.query(Clothes).filter_by(id=req.top_id).first()
    bottom = db.query(Clothes).filter_by(id=req.bottom_id).first()

    print("👕 top:", top)
    print("👖 bottom:", bottom)

    if not top or not bottom:
        raise HTTPException(status_code=404, detail="Top or bottom image file not found")

    # ✅ 경로 정규화 함수
    def normalize_path(url_or_path: str):
        if url_or_path.startswith("http"):
            return url_or_path.replace("http://13.125.42.2:8000", "").lstrip("/")
        return url_or_path.lstrip("/")

    top_path = normalize_path(top.image_url)
    bottom_path = normalize_path(bottom.image_url)

    def to_base64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    # 3. 하의 합성 API 호출
    headers_bottom = {"x-api-key": SEGMIND_API_KEY_BOTTOM}
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

    print("🔧 하의 합성 요청 중...")
    res1 = requests.post(SEGMIND_API_URL, json=payload1, headers=headers_bottom)
    print("📡 하의 응답 상태:", res1.status_code)

    if res1.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Bottom merge failed: {res1.text}")

    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(res1.content)

    time.sleep(3)

    # 4. 상의 합성 API 호출
    headers_top = {"x-api-key": SEGMIND_API_KEY_TOP}
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

    print("🔧 상의 합성 요청 중...")
    res2 = requests.post(SEGMIND_API_URL, json=payload2, headers=headers_top)
    print("📡 상의 응답 상태:", res2.status_code)

    if res2.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Top merge failed: {res2.text}")

    with open(final_path, "wb") as f:
        f.write(res2.content)

    print("✅ 합성 완료:", final_path)

    return {
        "image_id": final_id,
        "generated_image_url": make_absolute_url(f"/static/generated/{final_id}.jpg")
    }
