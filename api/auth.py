from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    user_id: str

@router.post("/login")
def login(req: LoginRequest):
    return {"login": True, "user_id": req.user_id}