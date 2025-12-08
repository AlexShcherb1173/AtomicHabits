import os
import time
import requests

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings  # noqa
from notifications.models import TelegramLinkToken, TelegramProfile  # noqa

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


def handle_start(chat_id, text, username=None):
    """
    Ожидаем /start <token>. Если токен валиден, привязываем Telegram к пользователю.
    """
    parts = text.strip().split(maxsplit=1)
    if len(parts) == 1:
        send_message(chat_id, "Привет! Открой ссылку из приложения AtomicHabits, чтобы привязать Telegram.")
        return

    token = parts[1]

    try:
        link_token = TelegramLinkToken.objects.select_related("user").get(token=token)
    except TelegramLinkToken.DoesNotExist:
        send_message(chat_id, "❌ Неверный или устаревший токен. Сгенерируйте новую ссылку в приложении.")
        return

    if not link_token.is_valid():
        send_message(chat_id, "❌ Токен устарел или уже использован. Сгенерируйте новую ссылку в приложении.")
        return

    user = link_token.user

    # создаём/обновляем TelegramProfile
    profile, created = TelegramProfile.objects.update_or_create(
        user=user,
        defaults={
            "chat_id": str(chat_id),
            "username": username or "",
            "is_active": True,
        },
    )

    # помечаем токен использованным
    link_token.is_used = True
    link_token.save(update_fields=["is_used"])

    send_message(
        chat_id,
        f"✅ Телеграм успешно привязан к аккаунту {user.username}.\n"
        f"Теперь вы будете получать напоминания о привычках.",
    )


def main():
    last_update_id = None
    print("Bot polling started...")

    while True:
        data = get_updates(offset=last_update_id)
        if data.get("ok"):
            for update in data.get("result", []):
                last_update_id = update["update_id"] + 1

                message = update.get("message") or {}
                chat = message.get("chat") or {}
                chat_id = chat.get("id")
                username = chat.get("username")
                text = message.get("text", "")

                if not chat_id or not text:
                    continue

                if text.startswith("/start"):
                    handle_start(chat_id, text, username=username)
                else:
                    # по желанию — обработка других команд
                    send_message(chat_id, "Напишите /start по ссылке из приложения, чтобы привязать аккаунт.")
        time.sleep(1)


if __name__ == "__main__":
    if not settings.TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN не задан в .env")
    else:
        main()