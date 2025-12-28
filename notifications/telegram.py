"""
Telegram-интеграция.
Содержит вспомогательные функции для отправки сообщений пользователям
через Telegram Bot API.
Используется:
- Celery-задачами (напоминания о привычках);
- может быть использовано и в синхронных сценариях (по желанию).
"""

from typing import Optional

import requests
from django.conf import settings


def send_telegram_message(chat_id: str, text: str) -> bool:
    """
    Отправляет сообщение пользователю в Telegram.
    Использует Telegram Bot API метод `sendMessage`.
    :param chat_id: Telegram chat_id пользователя
    :param text: Текст сообщения (поддерживается HTML-разметка)
    :return: True — если сообщение успешно отправлено,
             False — если произошла ошибка или бот не настроен
    Поведение:
    - если TELEGRAM_BOT_TOKEN не задан → сразу False
    - при сетевой ошибке / ошибке API → False
    """

    token: Optional[str] = settings.TELEGRAM_BOT_TOKEN
    base_url: str = settings.TELEGRAM_API_URL

    # Если бот не настроен — ничего не отправляем
    if not token:
        return False

    url = f"{base_url}/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=10,
        )
        data = response.json()
        return bool(data.get("ok"))
    except Exception:
        # Любая ошибка (network / JSON / timeout) → считаем отправку неуспешной
        return False