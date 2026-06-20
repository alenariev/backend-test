import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

# Схема для валидации входящего запроса (POST /api/contact)
class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Алёна"])
    phone: str = Field(..., min_length=5, max_length=20, examples=["+79991234567"])
    email: EmailStr = Field(..., examples=["alena@example.com"])
    comment: str = Field(..., min_length=5, max_length=1000, examples=["Привет! Нужен сайт."])

    # Кастомная валидация телефона с помощью регулярного выражения
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Разрешаем цифры, плюсы, скобки и дефисы
        phone_regex = re.compile(r"^\+?[0-9\s\-\(\)]+$")
        if not phone_regex.match(v):
            raise ValueError("Некорректный формат телефона")
        return v

# Схема для ответа сервера
class ContactResponse(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    comment: str
    ai_sentiment: Optional[str] = None
    ai_reply: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True # Позволяет Pydantic работать с объектами SQLAlchemy ORM