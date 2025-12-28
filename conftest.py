"""
Глобальные pytest-фикстуры для проекта AtomicHabits.

Важно:
- conftest.py импортируется pytest ДО инициализации Django.
- Поэтому любые импорты Django/DRF (get_user_model, APIClient, Token и т.д.)
  делаем только ВНУТРИ фикстур.
"""

import pytest


@pytest.fixture
def api_client():
    """
    Неаутентифицированный DRF APIClient.
    Импорт DRF выполняем внутри фикстуры, когда Django уже поднят pytest-django.
    """
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def user(db):
    """
    Тестовый пользователь.
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(username="test_user", password="test_password")


@pytest.fixture
def user2(db):
    """
    Второй тестовый пользователь (для проверки прав доступа, чужих привычек и т.п.).
    """
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.create_user(username="user2", password="test_password")


@pytest.fixture
def auth_client(api_client, user):
    """
    DRF-клиент с Token-аутентификацией под user.
    """
    from rest_framework.authtoken.models import Token

    token, _ = Token.objects.get_or_create(user=user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return api_client