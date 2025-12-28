"""
Тесты ограничений HTTP-методов для публичного эндпоинта привычек.
Публичный список привычек предназначен ИСКЛЮЧИТЕЛЬНО для чтения.
Любые операции изменения данных (POST / PUT / PATCH / DELETE)
должны быть запрещены.
Эти тесты подтверждают соблюдение требований безопасности:
- публичные данные доступны только для просмотра
- изменение и удаление публичных привычек запрещено
"""

import pytest

pytestmark = pytest.mark.django_db


PUBLIC_URL = "/api/habits/public/"


def test_public_endpoint_post_not_allowed(api_client):
    """
    Проверка: POST-запрос к публичному эндпоинту запрещён.
    Ожидаемое поведение:
    - сервер возвращает 405 Method Not Allowed
    """
    resp = api_client.post(PUBLIC_URL, {}, format="json")
    assert resp.status_code == 405


def test_public_endpoint_put_not_allowed(api_client):
    """
    Проверка: PUT-запрос к публичному эндпоинту запрещён.
    Ожидаемое поведение:
    - сервер возвращает 405 Method Not Allowed
    """
    resp = api_client.put(PUBLIC_URL, {}, format="json")
    assert resp.status_code == 405


def test_public_endpoint_patch_not_allowed(api_client):
    """
    Проверка: PATCH-запрос к публичному эндпоинту запрещён.
    Ожидаемое поведение:
    - сервер возвращает 405 Method Not Allowed
    """
    resp = api_client.patch(PUBLIC_URL, {}, format="json")
    assert resp.status_code == 405


def test_public_endpoint_delete_not_allowed(api_client):
    """
    Проверка: DELETE-запрос к публичному эндпоинту запрещён.
    Ожидаемое поведение:
    - сервер возвращает 405 Method Not Allowed
    """
    resp = api_client.delete(PUBLIC_URL)
    assert resp.status_code == 405
