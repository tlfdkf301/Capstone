# models/clothes.py
from database import Base
from sqlalchemy import Column, Integer, String, ARRAY, JSON, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Clothes(Base):
    __tablename__ = "clothes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, default=1)
    category = Column(String)  # top, bottom, outer, dress
    image_url = Column(String)

    # 옷 특징
    color = Column(String)
    fit = Column(String)
    length = Column(String)
    material = Column(String)
    sleeve_length = Column(String)
    collar = Column(String)

    # 스타일 예측 결과
    style_probs = Column(JSON)  # {"casual": 0.7, "formal": 0.2, ...}