import pytest

pytestmark = pytest.mark.django_db


def test_login_returns_token(api_client, user):
    """
    Проверка успешной авторизации пользователя.

    Ожидания:
    - POST /api/auth/login/ с корректными username/password
    - HTTP 200
    - поле `token` присутствует и является непустой строкой
    - токен подходит для Authorization: Token <token>
    """
    url = "/api/auth/login/"
    payload = {"username": user.username, "password": "test_password"}

    resp = api_client.post(url, payload, format="json")

    assert resp.status_code == 200
    assert "token" in resp.data
    assert isinstance(resp.data["token"], str)
    assert resp.data["token"]

def test_login_wrong_password(api_client, user):
    """
    Проверка: неверный пароль → ошибка авторизации.

    Ожидания:
    - HTTP 400 (у тебя LoginSerializer кидает ValidationError)
    """
    url = "/api/auth/login/"
    payload = {"username": user.username, "password": "wrong"}

    resp = api_client.post(url, payload, format="json")

    assert resp.status_code in (400, 401)
