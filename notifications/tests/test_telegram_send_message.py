"""
Тесты функции отправки сообщений в Telegram.
Проверяют поведение функции send_telegram_message:
- успешную отправку сообщения,
- обработку ответа Telegram API с ok=false,
- поведение при отсутствии токена,
- корректную обработку исключений requests.
"""

import pytest
from unittest.mock import Mock, patch

pytestmark = pytest.mark.django_db


def test_send_telegram_message_success(settings):
    """
    Успешная отправка сообщения в Telegram.
    Сценарий:
    - TELEGRAM_BOT_TOKEN и TELEGRAM_API_URL заданы,
    - requests.post возвращает JSON с {"ok": True}.
    Ожидается:
    - функция возвращает True,
    - запрос выполнен ровно один раз,
    - URL, payload и timeout сформированы корректно.
    """
    settings.TELEGRAM_BOT_TOKEN = "test_token"
    settings.TELEGRAM_API_URL = "https://api.telegram.org"

    from notifications.telegram import send_telegram_message

    with patch("notifications.telegram.requests.post") as mock_post:
        fake_response = Mock()
        fake_response.json.return_value = {"ok": True}
        mock_post.return_value = fake_response

        result = send_telegram_message(chat_id="123456", text="Тест")

        assert result is True

        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        # Проверяем URL Telegram API
        assert args[0] == "https://api.telegram.org/bottest_token/sendMessage"

        # Проверяем тело запроса
        assert kwargs["json"] == {
            "chat_id": "123456",
            "text": "Тест",
            "parse_mode": "HTML",
        }

        # Проверяем таймаут
        assert kwargs["timeout"] == 10


def test_send_telegram_message_api_returns_ok_false(settings):
    """
    Telegram API вернул ok=false.
    Сценарий:
    - запрос выполнен успешно,
    - но Telegram API сигнализирует об ошибке.
    Ожидается:
    - функция возвращает False.
    """
    settings.TELEGRAM_BOT_TOKEN = "test_token"
    settings.TELEGRAM_API_URL = "https://api.telegram.org"

    from notifications.telegram import send_telegram_message

    with patch("notifications.telegram.requests.post") as mock_post:
        fake_response = Mock()
        fake_response.json.return_value = {"ok": False}
        mock_post.return_value = fake_response

        result = send_telegram_message(chat_id="123", text="Ошибка")

        assert result is False


def test_send_telegram_message_no_token(settings):
    """
    Отправка сообщения без TELEGRAM_BOT_TOKEN.
    Сценарий:
    - токен бота не задан в настройках.
    Ожидается:
    - функция возвращает False,
    - HTTP-запрос в Telegram API не выполняется.
    """
    settings.TELEGRAM_BOT_TOKEN = ""
    settings.TELEGRAM_API_URL = "https://api.telegram.org"

    from notifications.telegram import send_telegram_message

    with patch("notifications.telegram.requests.post") as mock_post:
        result = send_telegram_message(chat_id="123", text="Тест")

        assert result is False
        mock_post.assert_not_called()


def test_send_telegram_message_request_exception(settings):
    """
    Обработка исключения при выполнении HTTP-запроса.
    Сценарий:
    - requests.post выбрасывает исключение (например, ошибка сети).
    Ожидается:
    - функция корректно перехватывает исключение,
    - возвращает False,
    - приложение не падает.
    """
    settings.TELEGRAM_BOT_TOKEN = "test_token"
    settings.TELEGRAM_API_URL = "https://api.telegram.org"

    from notifications.telegram import send_telegram_message

    with patch(
        "notifications.telegram.requests.post",
        side_effect=Exception("Network error"),
    ):
        result = send_telegram_message(chat_id="123", text="Тест")

        assert result is False
