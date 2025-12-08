import requests
from django.conf import settings


def send_telegram_message(chat_id: str, text: str) -> bool:
    """
    Отправка сообщения пользователю в Telegram.
    Возвращает True при успехе, False при ошибке.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    base_url = settings.TELEGRAM_API_URL

    if not token:
        return False

    url = f"{base_url}/bot{token}/sendMessage"
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