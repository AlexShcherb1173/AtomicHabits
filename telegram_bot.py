"""
Simple Telegram bot (long polling) for AtomicHabits.
Этот скрипт нужен, чтобы обработать deep-link привязку Telegram:
1) Пользователь в приложении вызывает GET /api/telegram/link/
   и получает ссылку вида: https://t.me/<BOT_USERNAME>?start=<token>
2) Пользователь открывает ссылку → Telegram отправляет боту сообщение:
   /start <token>
3) Бот:
   - проверяет, что токен существует и валиден (не истёк/не использован),
   - создаёт/обновляет TelegramProfile (chat_id, username),
   - помечает токен использованным.
Важно:
- Это НЕ Celery и НЕ вебхук. Это отдельный процесс (polling).
- Для продакшена лучше webhooks, но для dev/stage polling нормально.
"""

from __future__ import annotations

import os
import time
from typing import Any, Optional

import django
import requests

# Django setup (чтобы импортировать settings и модели)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings  # noqa: E402
from django.db import transaction  # noqa: E402
from notifications.models import TelegramLinkToken, TelegramProfile  # noqa: E402


def _base_url() -> str:
    """
    Построить базовый URL Telegram Bot API.
    :return: строка вида "https://api.telegram.org/bot<TOKEN>"
    """
    return f"{settings.TELEGRAM_API_URL}/bot{settings.TELEGRAM_BOT_TOKEN}"


def get_updates(offset: Optional[int] = None) -> dict[str, Any]:
    """
    Получить обновления от Telegram через long polling.
    :param offset: update_id, начиная с которого читать события (чтобы не получать старые повторно)
    :return: dict ответа Telegram API
    """
    params: dict[str, Any] = {"timeout": 30}
    if offset is not None:
        params["offset"] = offset

    resp = requests.get(f"{_base_url()}/getUpdates", params=params, timeout=35)
    resp.raise_for_status()
    return resp.json()


def send_message(chat_id: str | int, text: str) -> None:
    """
    Отправить сообщение в Telegram чат.
    :param chat_id: идентификатор чата (int или str)
    :param text: текст сообщения
    """
    requests.post(
        f"{_base_url()}/sendMessage",
        json={"chat_id": str(chat_id), "text": text},
        timeout=10,
    ).raise_for_status()


def handle_start(chat_id: str | int, text: str, username: Optional[str] = None) -> None:
    """
    Обработать команду /start.
    Ожидаем формат:
        /start <token>
    Если токен валиден:
    - создаём/обновляем TelegramProfile для пользователя,
    - помечаем TelegramLinkToken как использованный.
    :param chat_id: telegram chat id
    :param text: полный текст сообщения (например "/start abcdef")
    :param username: telegram username (если есть)
    """
    parts = text.strip().split(maxsplit=1)

    # /start без токена
    if len(parts) == 1:
        send_message(
            chat_id,
            "Привет! Открой ссылку из приложения AtomicHabits, чтобы привязать Telegram.",
        )
        return

    token = parts[1].strip()

    try:
        link_token = TelegramLinkToken.objects.select_related("user").get(token=token)
    except TelegramLinkToken.DoesNotExist:
        send_message(
            chat_id,
            "❌ Неверный или устаревший токен. Сгенерируйте новую ссылку в приложении.",
        )
        return

    if not link_token.is_valid():
        send_message(
            chat_id,
            "❌ Токен устарел или уже использован. Сгенерируйте новую ссылку в приложении.",
        )
        return

    user = link_token.user

    # Атомарно: привязали профиль + пометили токен использованным
    with transaction.atomic():
        TelegramProfile.objects.update_or_create(
            user=user,
            defaults={
                "chat_id": str(chat_id),
                "username": username or "",
                "is_active": True,
            },
        )
        link_token.is_used = True
        link_token.save(update_fields=["is_used"])

    send_message(
        chat_id,
        (
            f"✅ Телеграм успешно привязан к аккаунту {user.username}.\n"
            f"Теперь вы будете получать напоминания о привычках."
        ),
    )


def _extract_message(
    update: dict[str, Any],
) -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Вытащить chat_id, username и text из update (с защитой от отсутствующих ключей).
    :param update: элемент из массива result Telegram API
    :return: (chat_id, username, text) как строки или None
    """
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    username = chat.get("username")
    text = message.get("text")

    return (str(chat_id) if chat_id is not None else None, username, text)


def main() -> None:
    """
    Основной цикл polling.
    - Запрашивает обновления у Telegram.
    - Обрабатывает /start <token>.
    - На остальные сообщения отвечает подсказкой.
    """
    last_update_id: Optional[int] = None
    print("Bot polling started...")

    while True:
        try:
            data = get_updates(offset=last_update_id)
        except Exception as e:
            # Чтобы бот не падал от временной сетевой ошибки
            print(f"[WARN] getUpdates failed: {e}")
            time.sleep(3)
            continue

        if data.get("ok"):
            for update in data.get("result", []):
                last_update_id = int(update["update_id"]) + 1

                chat_id, username, text = _extract_message(update)
                if not chat_id or not text:
                    continue

                if text.startswith("/start"):
                    handle_start(chat_id, text, username=username)
                else:
                    send_message(
                        chat_id,
                        "Напишите /start по ссылке из приложения, чтобы привязать аккаунт.",
                    )

        time.sleep(1)


if __name__ == "__main__":
    """
    Entry point.
    Проверяем наличие TELEGRAM_BOT_TOKEN и запускаем polling.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN не задан в .env")
    else:
        main()
