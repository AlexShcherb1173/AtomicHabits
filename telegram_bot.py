import requests
import time
from django.conf import settings
import os
import django

# Инициализация Django (чтобы работать с моделями)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from notifications.models import TelegramProfile  # noqa


BASE_URL = f"{settings.TELEGRAM_API_URL}/bot{settings.TELEGRAM_BOT_TOKEN}"


def get_updates(offset=None):
    params = {"timeout": 30, "offset": offset}
    resp = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=35)
    return resp.json()


def send_message(chat_id, text):
    requests.post(
        f"{BASE_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )


def main():
    last_update_id = None

    while True:
        data = get_updates(offset=last_update_id)
        if data.get("ok"):
            for update in data.get("result", []):
                last_update_id = update["update_id"] + 1
                message = update.get("message") or {}
                chat = message.get("chat") or {}
                chat_id = chat.get("id")
                text = message.get("text", "")

                if not chat_id or not text:
                    continue

                if text.startswith("/start"):
                    # Здесь можно просто сказать пользователю его chat_id
                    send_message(
                        chat_id,
                        f"Привет! Твой chat_id: {chat_id}. "
                        f"Передай его разработчику/сервису, чтобы включить напоминания.",
                    )

        time.sleep(1)


if __name__ == "__main__":
    if not settings.TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN не задан в настройках.")
    else:
        main()