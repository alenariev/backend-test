import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    async def send_email_async(to_email: str, subject: str, html_content: str) -> bool:
        """Вспомогательный асинхронный метод для отправки Email через SMTP Yandex."""
        # Проверяем, настроена ли почта
        if not settings.SENDER_EMAIL or settings.SENDER_EMAIL == "your-yandex-email@yandex.ru":
            logger.warning(f"SMTP Yandex не настроен. Пропущена отправка письма на {to_email}")
            return False

        # Создаем HTML-письмо
        message = MIMEMultipart("alternative")
        message["From"] = settings.SENDER_EMAIL
        message["To"] = to_email
        message["Subject"] = subject

        html_part = MIMEText(html_content, "html", "utf-8")
        message.attach(html_part)

        try:
            # Асинхронное подключение к SMTP Яндекса
            await aiosmtplib.send(
                message,
                hostname="smtp.yandex.ru",
                port=465,
                username=settings.SENDER_EMAIL,
                password=settings.SENDER_PASSWORD,
                use_tls=True,
                timeout=10.0
            )
            logger.info(f"Письмо успешно отправлено на адрес: {to_email}")
            return True
        except Exception as e:
            logger.error(f"Не удалось отправить Email на {to_email}. Ошибка: {str(e)}")
            return False

    async def send_notifications(self, name: str, email: str, phone: str, comment: str, ai_sentiment: str, ai_reply: str):
        """Отправляет два письма: владельцу сайта и копию пользователю."""
        
        # 1. HTML-шаблон для тебя (владельца)
        owner_subject = f"🔥 Новая заявка на сайте от {name}"
        owner_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #d4af37;">Получена новая заявка!</h2>
                <p><b>Имя:</b> {name}</p>
                <p><b>Email:</b> {email}</p>
                <p><b>Телефон:</b> {phone}</p>
                <p><b>Сообщение:</b> {comment}</p>
                <hr style="border: 0; border-top: 1px solid #ccc;">
                <p><b>🤖 Анализ ИИ-помощника:</b></p>
                <p><b>Тональность:</b> <span style="color: green; font-weight: bold;">{ai_sentiment}</span></p>
                <p><b>Сгенерированный автоответ:</b> <i>"{ai_reply}"</i></p>
            </body>
        </html>
        """
        
        # 2. HTML-шаблон для пользователя (копия)
        user_subject = f"Здравствуйте, {name}! Ваше обращение получено"
        user_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #eee; border-radius: 10px;">
                <h2 style="color: #d4af37; text-align: center;">Здравствуйте, {name}!</h2>
                <p>Спасибо за интерес к моему портфолио и за ваше сообщение. Оно успешно доставлено мне на почту.</p>
                <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #d4af37; margin: 20px 0;">
                    <p style="margin: 0; font-weight: bold; color: #555;">Ответ моего AI-ассистента:</p>
                    <p style="margin: 10px 0 0 0; font-style: italic; color: #333;">"{ai_reply}"</p>
                </div>
                <p>Я обязательно ознакомлюсь с вашим предложением лично и свяжусь с вами в ближайшее время!</p>
                <br>
                <hr style="border: 0; border-top: 1px solid #eee;">
                <p style="font-size: 0.9em; color: #777; text-align: center;">
                    С уважением,<br>
                    <b>Алёна Рив</b><br>
                    Junior Python Fullstack Developer
                </p>
            </body>
        </html>
        """

        # Запускаем отправку обоих писем
        await self.send_email_async(settings.OWNER_EMAIL, owner_subject, owner_html)
        await self.send_email_async(email, user_subject, user_html)