from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.db_models import DBContactRequest

class ContactRepository:
    @staticmethod
    def create(db: Session, request_data: DBContactRequest) -> DBContactRequest:
        """Сохраняет новую заявку в базу данных."""
        db.add(request_data)
        db.commit()
        db.refresh(request_data)
        return request_data

    @staticmethod
    def get_total_count(db: Session) -> int:
        """Возвращает общее количество полученных заявок."""
        return db.query(func.count(DBContactRequest.id)).scalar()

    @staticmethod
    def get_sentiment_stats(db: Session) -> dict:
        """Возвращает статистику по тональности сообщений (позитивные, негативные и т.д.)."""
        results = (
            db.query(DBContactRequest.ai_sentiment, func.count(DBContactRequest.id))
            .group_by(DBContactRequest.ai_sentiment)
            .all()
        )
        # Превращаем результат запроса в удобный словарь
        return {sentiment if sentiment else "Не определено": count for sentiment, count in results}