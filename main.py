from fastapi import FastAPI
from api.auth import router as auth_router
from api.closet import router as closet_router
from api.recommend import router as recommend_router
from api.feedback import router as feedback_router
from api.similarity import router as similarity_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# 정적 이미지 경로
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "Fastapi server is running"}

# 라우터 등록
app.include_router(auth_router)
app.include_router(closet_router)
app.include_router(recommend_router)
app.include_router(feedback_router)
app.include_router(similarity_router)

# 가상환경 활성화 : venv\Scripts\Activate.ps1
# 서버실행 : uvicorn main:app --reload