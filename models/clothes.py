# models/clothes.py

from sqlalchemy import Column, Integer, String, ARRAY, JSON, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Clothes(Base):
    __tablename__ = "clothes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    category = Column(String, nullable=False)  # 예: 상의, 하의
    features = Column(ARRAY(Text))             # 예: ["핏_루즈", "색상_검정"]
    style_probs = Column(JSON)                 # 예: {"모던": 0.5, "스트리트": 0.3}
    image_path = Column(Text)                  # 예: "/static/images/상의_103.jpg"
    created_at = Column(TIMESTAMP, default=datetime.utcnow)