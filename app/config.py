from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Junior Backend Service"
    DATABASE_URL: str = "sqlite:///./db.sqlite3"
    
    # AI
    OPENAI_API_KEY: str = ""
    
    # Email SMTP
    SENDER_EMAIL: str = ""
    SENDER_PASSWORD: str = ""
    OWNER_EMAIL: str = ""
    
    # Лимиты для Rate Limiting (по умолчанию 1 запрос в 60 секунд)
    RATE_LIMIT_SECONDS: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()