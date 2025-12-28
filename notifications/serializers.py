"""
Сериализаторы приложения notifications.
Используются для:
- возврата данных, связанных с Telegram-интеграцией;
- формирования deep-link для привязки Telegram-аккаунта пользователя.
"""

from rest_framework import serializers


class TelegramLinkSerializer(serializers.Serializer):
    """
    Сериализатор для возврата ссылки привязки Telegram.
    Используется в API, которое:
    - генерирует одноразовый токен;
    - формирует deep-link вида:
      https://t.me/<BOT_USERNAME>?start=<token>;
    - возвращает эту ссылку фронтенду.

    Поле `link` — только для чтения.
    """

    link = serializers.CharField(
        read_only=True,
        help_text="Deep-link для привязки Telegram-аккаунта пользователя.",
    )