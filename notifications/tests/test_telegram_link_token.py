"""
Тесты модели TelegramLinkToken.
Проверяют корректность логики одноразовых токенов,
используемых для привязки Telegram-аккаунта пользователя:
- валидность нового токена,
- инвалидирование после использования,
- инвалидирование после истечения срока действия.
"""

import pytest
from datetime import timedelta

from django.utils import timezone

from notifications.models import TelegramLinkToken

pytestmark = pytest.mark.django_db


def test_link_token_is_valid_initially(user):
    """
    Новый токен привязки Telegram должен быть валиден сразу после создания.
    Ожидается:
    - is_valid() возвращает True,
    - токен не помечен как использованный,
    - срок действия ещё не истёк.
    """
    token = TelegramLinkToken.create_for_user(user=user, lifetime_minutes=30)

    assert token.is_valid() is True


def test_link_token_becomes_invalid_when_used(user):
    """
    Токен должен становиться невалидным после использования.
    Сценарий:
    - создаём валидный токен,
    - помечаем его как использованный (is_used=True),
    - проверяем, что is_valid() возвращает False.
    """
    token = TelegramLinkToken.create_for_user(user=user, lifetime_minutes=30)
    token.is_used = True
    token.save()
    token.refresh_from_db()

    assert token.is_valid() is False


def test_link_token_becomes_invalid_when_expired(user):
    """
    Токен должен становиться невалидным после истечения срока действия.
    Сценарий:
    - создаём токен,
    - вручную устанавливаем expires_at в прошлое,
    - проверяем, что is_valid() возвращает False.
    """
    token = TelegramLinkToken.create_for_user(user=user, lifetime_minutes=30)
    token.expires_at = timezone.now() - timedelta(seconds=1)
    token.save()
    token.refresh_from_db()

    assert token.is_valid() is False
