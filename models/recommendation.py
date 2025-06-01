# 추천 기록 조회
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"
    description = Column(String)
    id = Column(Integer, primary_key=True)
    selected_item_id = Column(String)
    tpo = Column(String)
    imageUrl = Column(String)
    clothingIds = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)