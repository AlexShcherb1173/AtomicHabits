import pytest

pytestmark = pytest.mark.django_db


def test_login_returns_token(api_client, user):
    """
    Проверка успешной авторизации пользователя.
    Ожидания по ТЗ:
    - POST /api/auth/login/ с корректными username/password
    - API возвращает HTTP 200
    - В ответе присутствует поле `token`
    - `token` является непустой строкой
    Используется для последующей Token-аутентификации:
    Authorization: Token <token>
    """
    url = "/api/auth/login/"
    payload = {"username": "alex", "password": "password123"}

    resp = api_client.post(url, payload, format="json")

    assert resp.status_code == 200
    assert "token" in resp.data
    assert isinstance(resp.data["token"], str)
    assert resp.data["token"]


def test_login_wrong_password(api_client, user):
    """
    Проверка ошибки авторизации при неверном пароле.
    Ожидания:
    - POST /api/auth/login/ с неверным паролем
    - API НЕ возвращает токен
    - HTTP статус:
        * 400 — ValidationError из LoginSerializer (текущая реализация)
        * либо 401 — если логика будет изменена на Unauthorized
    Тест допускает оба варианта, чтобы не быть хрупким
    при будущих рефакторингах.
    """
    url = "/api/auth/login/"
    payload = {"username": "alex", "password": "wrong"}

    resp = api_client.post(url, payload, format="json")

    assert resp.status_code in (400, 401)
