from sqlalchemy import Column, String, DateTime
from database import Base
from datetime import datetime

class UserImage(Base):
    __tablename__ = "user_images"

    image_id = Column(String, primary_key=True, nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)