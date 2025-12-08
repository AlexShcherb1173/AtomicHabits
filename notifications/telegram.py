import requests
from django.conf import settings


def send_telegram_message(chat_id: str, text: str) -> bool:
    """
    Отправка сообщения пользователю в Telegram.
    Возвращает True при успехе, False при ошибке.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        # Токен не настроен — логируем или молча выходим
        return False

    url = f"{settings.TELEGRAM_API_URL}/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        return bool(data.get("ok"))
    except Exception:
        return False