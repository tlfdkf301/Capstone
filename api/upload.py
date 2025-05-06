from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/upload_clothes/")
async def upload_clothes(image: UploadFile = File(...)):
    return {"filename": image.filename}