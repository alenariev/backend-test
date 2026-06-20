from sqlalchemy.orm import Session
from app.models.schemas import ContactCreate
from app.models.db_models import DBContactRequest
from app.repositories.contact_repository import ContactRepository
from app.services.ai_service import AIService
from app.services.email_service import EmailService

class ContactService:
    def __init__(self):
        self.ai_service = AIService()
        self.email_service = EmailService()

    async def process_contact_request(self, db: Session, schema_data: ContactCreate) -> DBContactRequest:
        """Оркестрирует процесс: валидация -> ИИ -> Сохранение в БД -> Отправка писем."""
        
        # 1. Отправляем текст в ИИ (сработает авто-fallback, если OpenAI недоступен)
        ai_sentiment, ai_reply = await self.ai_service.analyze_and_generate_reply(
            name=schema_data.name, 
            comment=schema_data.comment
        )

        # 2. Создаем объект модели SQLAlchemy
        db_request = DBContactRequest(
            name=schema_data.name,
            phone=schema_data.phone,
            email=schema_data.email,
            comment=schema_data.comment,
            ai_sentiment=ai_sentiment,
            ai_reply=ai_reply
        )

        # 3. Сохраняем в базу данных SQLite через репозиторий
        saved_request = ContactRepository.create(db, db_request)

        # 4. Асинхронно отправляем письма (не блокируя ответ клиенту)
        # Мы не пишем await перед отправкой, чтобы клиент мгновенно получил ответ 200 на фронтенде,
        # а отправка писем тихо завершилась на бэкенде.
        import asyncio
        asyncio.create_task(
            self.email_service.send_notifications(
                name=schema_data.name,
                email=schema_data.email,
                phone=schema_data.phone,
                comment=schema_data.comment,
                ai_sentiment=ai_sentiment,
                ai_reply=ai_reply
            )
        )

        return saved_request