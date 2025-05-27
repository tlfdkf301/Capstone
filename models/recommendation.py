# 추천 기록 조회
from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, default=1)
    selected_item_id = Column(String)
    tpo = Column(String)
    recommended_items = Column(JSON)  # Dict[str, List[str]] or List of dicts
    created_at = Column(DateTime, default=datetime.utcnow)