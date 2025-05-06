from fastapi import APIRouter

router = APIRouter()

@router.get("/recommendation/")
async def recommend():
    return {"recommended_items": ["o1", "b3"]}