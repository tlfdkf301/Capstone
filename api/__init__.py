# api/__init__.py
from .upload import router as upload_router
from .recommend import router as recommend_router

__all__ = ["upload_router", "recommend_router"]