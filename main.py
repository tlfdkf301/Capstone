from fastapi import FastAPI
from api import upload_router, recommend_router

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Fastapi server is running"}

app.include_router(upload_router)
app.include_router(recommend_router)


# 가상환경 활성화 : venv\Scripts\Activate.ps1
# 서버실행 : uvicorn main:app --reload