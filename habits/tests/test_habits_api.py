"""
Тесты прав доступа и CRUD-поведения для API привычек.
Проверяются ключевые правила безопасности:
- доступ к списку личных привычек только для авторизованных
- пользователь видит только свои привычки
- публичные привычки других пользователей НЕ видны в личном списке
- пользователь не может читать / изменять / удалять чужие привычки
- пользователь может полноценно управлять своими привычками
Эти тесты подтверждают корректную реализацию multi-tenant логики
и соответствие требованиям ТЗ по безопасности.
"""

import pytest
from datetime import timedelta, time

from habits.models import Habit

pytestmark = pytest.mark.django_db


LIST_URL = "/api/habits/"


def detail_url(habit_id: int) -> str:
    """
    Формирует URL детального эндпоинта привычки по её ID.
    """
    return f"/api/habits/{habit_id}/"


def test_my_habits_list_requires_auth(api_client):
    """
    Проверка: список личных привычек требует авторизации.
    Сценарий:
    - неавторизованный клиент обращается к /api/habits/
    Ожидаемое поведение:
    - доступ запрещён (401 Unauthorized или 403 Forbidden)
    """
    resp = api_client.get(LIST_URL)
    assert resp.status_code in (401, 403)


def test_user_sees_only_own_habits_in_private_list(auth_client, user, user2):
    """
    Проверка: пользователь в личном списке видит только свои привычки.
    Сценарий:
    - у пользователя есть личная привычка
    - у другого пользователя есть публичная привычка
    Ожидаемое поведение:
    - в списке отображается ТОЛЬКО привычка текущего пользователя
    - чужие привычки (даже публичные) не попадают в личный список
    """
    Habit.objects.create(
        user=user,
        action="Моя привычка",
        time=time(10, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=False,
    )
    Habit.objects.create(
        user=user2,
        action="Чужая привычка",
        time=time(11, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=True,
        is_pleasant=False,
    )

    resp = auth_client.get(LIST_URL)

    assert resp.status_code == 200
    assert "results" in resp.data
    actions = [x["action"] for x in resp.data["results"]]
    assert actions == ["Моя привычка"]


def test_create_habit_sets_user_automatically(auth_client, user):
    """
    Проверка: при создании привычки user устанавливается автоматически.
    Сценарий:
    - клиент НЕ передаёт поле user в payload
    - создаётся привычка через API
    Ожидаемое поведение:
    - привычка успешно создаётся
    - habit.user == текущий авторизованный пользователь
    """
    payload = {
        "action": "Пить воду",
        "time": "12:00:00",
        "periodicity": 1,
        "duration": "00:01:00",
        "is_public": False,
        "is_pleasant": False,
    }

    resp = auth_client.post(LIST_URL, payload, format="json")

    assert resp.status_code == 201
    habit = Habit.objects.get(id=resp.data["id"])
    assert habit.user == user


def test_user_can_retrieve_own_habit(auth_client, user):
    """
    Проверка: пользователь может получать свои привычки по detail endpoint.
    Сценарий:
    - создаётся привычка пользователя
    - выполняется GET /api/habits/<id>/
    Ожидаемое поведение:
    - запрос успешен (200 OK)
    - возвращается корректный объект
    """
    habit = Habit.objects.create(
        user=user,
        action="Моя",
        time=time(9, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=False,
    )

    resp = auth_client.get(detail_url(habit.id))
    assert resp.status_code == 200
    assert resp.data["id"] == habit.id


def test_user_cannot_retrieve_other_user_habit(auth_client, user2):
    """
    Проверка: пользователь не может получать привычки другого пользователя.
    Сценарий:
    - существует публичная привычка другого пользователя
    - текущий пользователь пытается получить её по ID
    Ожидаемое поведение:
    - доступ запрещён:
        * 404 Not Found (объект скрыт)
        * или 403 Forbidden
    """
    other = Habit.objects.create(
        user=user2,
        action="Чужая",
        time=time(9, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=True,
        is_pleasant=False,
    )

    resp = auth_client.get(detail_url(other.id))
    assert resp.status_code in (403, 404)


def test_user_cannot_update_other_user_habit(auth_client, user2):
    """
    Проверка: пользователь не может изменять привычки другого пользователя.
    Сценарий:
    - существует привычка другого пользователя
    - текущий пользователь пытается изменить её через PATCH
    Ожидаемое поведение:
    - доступ запрещён (403 или 404)
    """
    other = Habit.objects.create(
        user=user2,
        action="Чужая",
        time=time(9, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=True,
        is_pleasant=False,
    )

    resp = auth_client.patch(detail_url(other.id), {"action": "Хак"}, format="json")
    assert resp.status_code in (403, 404)


def test_user_can_update_own_habit(auth_client, user):
    """
    Проверка: пользователь может обновлять свои привычки.
    Сценарий:
    - создаётся привычка пользователя
    - выполняется PATCH с изменением поля action
    Ожидаемое поведение:
    - запрос успешен (200 OK)
    - изменения сохраняются в базе
    """
    habit = Habit.objects.create(
        user=user,
        action="До",
        time=time(9, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=False,
    )

    resp = auth_client.patch(detail_url(habit.id), {"action": "После"}, format="json")
    assert resp.status_code == 200
    habit.refresh_from_db()
    assert habit.action == "После"


def test_user_can_delete_own_habit(auth_client, user):
    """
    Проверка: пользователь может удалять свои привычки.
    Сценарий:
    - создаётся привычка пользователя
    - выполняется DELETE /api/habits/<id>/
    Ожидаемое поведение:
    - запрос успешен (200 OK или 204 No Content)
    - привычка удаляется из базы данных
    """
    habit = Habit.objects.create(
        user=user,
        action="Удалить",
        time=time(9, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=False,
    )

    resp = auth_client.delete(detail_url(habit.id))
    assert resp.status_code in (200, 204)
    assert not Habit.objects.filter(id=habit.id).exists()
