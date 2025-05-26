from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.auth import router as auth_router
from api.closet import router as closet_router
from api.recommend import router as recommend_router
from api.feedback import router as feedback_router
from api.similarity import router as similarity_router
from api.upload import router as upload_router
from core.rules_loader import load_rules_with_score, rules_to_dict_sorted_key
print("✅ FastAPI starting...")
app = FastAPI()

# CORS 허용 (필요 시 origin 제한 가능)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시 여기에 프론트 주소 지정
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 이미지 경로
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "Fastapi server is running"}

# 라우터 등록
print("✅ Registering routers")
app.include_router(auth_router)
app.include_router(closet_router)
app.include_router(recommend_router)
app.include_router(feedback_router)
app.include_router(similarity_router)
app.include_router(upload_router, prefix="/upload", tags=["upload"])

# 서버 시작 시 로딩
color_df, feature_df = load_rules_with_score()
color_dict = rules_to_dict_sorted_key(color_df, is_color=True)
feature_dict = rules_to_dict_sorted_key(feature_df, is_color=False)

# 전역으로 공유
app.state.color_dict = color_dict
app.state.feature_dict = feature_dict
print("✅ App is ready")
# 가상환경 활성화 : venv\Scripts\Activate.ps1
# 서버실행 : uvicorn main:app --reload
# http://localhost:8000/docs