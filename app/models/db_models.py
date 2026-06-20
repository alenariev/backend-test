from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class DBContactRequest(Base):
    __tablename__ = "contact_requests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    comment = Column(Text, nullable=False)
    
    # Поля для сохранения результатов работы ИИ
    ai_sentiment = Column(String(50), nullable=True) # Позитивный / Негативный / Нейтральный
    ai_reply = Column(Text, nullable=True) # Сгенерированный ИИ ответ
    
    created_at = Column(DateTime, default=datetime.utcnow)