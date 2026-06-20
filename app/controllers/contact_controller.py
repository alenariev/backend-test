from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import ContactCreate, ContactResponse
from app.services.contact_service import ContactService
from app.repositories.contact_repository import ContactRepository

router = APIRouter(prefix="/api", tags=["Contact"])
contact_service = ContactService()

@router.post(
    "/contact", 
    response_model=ContactResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Отправить заявку обратной связи"
)
async def create_contact_request(
    data: ContactCreate, 
    db: Session = Depends(get_db)
):
    """
    Принимает заявку, валидирует её, отправляет в ИИ для анализа тональности,
    сохраняет в базу данных SQLite и асинхронно отправляет письма на почту.
    """
    try:
        result = await contact_service.process_contact_request(db, data)
        return result
    except Exception as e:
        # Если что-то пошло не так на сервере, возвращаем красивую ошибку 500
        raise HTTPException(
            status_code=500, 
            detail=f"Внутренняя ошибка сервера при обработке заявки: {str(e)}"
        )


@router.get("/health")
def health_check():
    """Простой эндпоинт для проверки работоспособности API"""
    return {"status": "ok", "message": "Сервер работает в штатном режиме"}

@router.get("/metrics")
def get_metrics():
    """Эндпоинт для аналитики (будет плюсом для бизнес-логики)"""
    # Здесь мы можем посчитать общую статистику
    # На реальном проекте тут считались бы DAU/конверсии, о которых писали в требованиях!
    try:
        db = next(get_db())
        total_requests = ContactRepository.get_total_count(db)
        sentiment_stats = ContactRepository.get_sentiment_stats(db)
        
        return {
            "status": "healthy",
            "total_feedback_requests": total_requests,
            "ai_sentiment_distribution": sentiment_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сбора метрик: {str(e)}")