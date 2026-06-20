import os
import time
import logging
from collections import defaultdict
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.controllers import contact_controller

# 1. Настраиваем логирование в файл logs/app.log
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app_logger")

# 2. Инициализируем базу данных
try:
    import app.models.db_models as db_models
    db_models.Base.metadata.create_all(bind=engine)
    logger.info("База данных SQLite успешно инициализирована.")
except Exception as e:
    logger.error(f"Критическая ошибка инициализации БД: {e}")

# 3. Создаем экземпляр FastAPI
app = FastAPI(
    title="Alena Riev API",
    description="Backend API для лендинга-презентации с интеграцией ИИ и отправкой почты",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redocs"
)

# 4. Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Rate Limiting на уровне Middleware (Защита от спама)
client_requests_tracker = defaultdict(float)
RATE_LIMIT_SECONDS = 60 

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == "/api/contact" and request.method == "POST":
        client_ip = request.client.host
        current_time = time.time()
        last_request_time = client_requests_tracker[client_ip]
        
        if current_time - last_request_time < RATE_LIMIT_SECONDS:
            logger.warning(f"Превышен Rate Limit для IP: {client_ip}. Запрос заблокирован.")
            # Вместо raise HTTPException возвращаем чистый JSONResponse напрямую из Middleware
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Слишком много запросов. Пожалуйста, подождите {int(RATE_LIMIT_SECONDS - (current_time - last_request_time))} сек."
                }
            )
        
        client_requests_tracker[client_ip] = current_time

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Запрос: {request.method} {request.url.path} | "
        f"Статус: {response.status_code} | "
        f"Время обработки: {process_time:.4f}s"
    )
    return response

# 6. Глобальный обработчик непредвиденных ошибок (теперь возвращает JSONResponse)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Необработанное исключение при запросе {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Произошла непредвиденная ошибка на сервере. Администратор уже уведомлен."
        }
    )

app.include_router(contact_controller.router)