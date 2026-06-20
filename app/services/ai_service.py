import logging
import json
from openai import AsyncOpenAI
from app.config import settings

# Настраиваем логер для этого файла
logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        # Инициализируем асинхронный клиент OpenAI
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze_and_generate_reply(self, name: str, comment: str) -> tuple[str, str]:
        """
        Обращается к OpenAI для анализа тональности и генерации персонализированного ответа.
        Возвращает кортеж: (тональность, автоответ).
        """
        # Если ключ не задан в .env, сразу уходим в fallback режим
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-api-key-here":
            logger.warning("OpenAI API Key не настроен. Активирован режим заглушки (Fallback).")
            return "Нейтральный", f"Здравствуйте, {name}! Спасибо за обращение. Я свяжусь с вами в ближайшее время."

        system_prompt = (
            "Ты — AI-ассистент на сайте веб-разработчика Алёны. Твоя задача — проанализировать "
            "сообщение потенциального клиента или работодателя и выдать ответ строго в формате JSON с двумя ключами:\n"
            "1. 'sentiment': строка, строго одно из значений: 'Позитивный', 'Нейтральный', 'Негативный'.\n"
            "2. 'reply': строка, вежливый, персонализированный, короткий ответ от лица Алёны на русском языке.\n"
            "Пример ответа:\n"
            '{"sentiment": "Позитивный", "reply": "Спасибо за теплые слова! Буду очень рада сотрудничеству."}'
        )

        try:
            # Делаем асинхронный запрос к GPT
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                response_format={"type": "json_object"}, # Гарантирует, что на выходе будет JSON
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Имя автора: {name}\nСообщение: {comment}"}
                ],
                max_tokens=200,
                temperature=0.7,
                timeout=7.0 # Жесткий таймаут, чтобы сервис не "зависал" при лагах OpenAI
            )
            
            # Парсим JSON-ответ от модели
            result_json = json.loads(response.choices[0].message.content)
            sentiment = result_json.get("sentiment", "Нейтральный")
            reply = result_json.get("reply", "Спасибо за ваше сообщение!")
            
            logger.info(f"ИИ успешно обработал запрос для {name}. Тональность: {sentiment}")
            return sentiment, reply

        except Exception as e:
            # Режим Graceful Fallback: если произошла ЛЮБАЯ ошибка (таймаут, неверный ключ, лимиты)
            logger.error(f"Ошибка при обращении к OpenAI API: {str(e)}. Активирован Fallback-режим.")
            
            fallback_sentiment = "Нейтральный"
            fallback_reply = (
                f"Здравствуйте, {name}! Спасибо за проявленный интерес к моему портфолио. "
                f"Я получила ваше сообщение и обязательно отвечу вам лично в ближайшее время!"
            )
            return fallback_sentiment, fallback_reply