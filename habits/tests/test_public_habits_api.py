"""
Тесты публичного списка привычек.
Проверяются требования:
- публичный список доступен без авторизации
- возвращаются только привычки с признаком is_public=True
- приватные привычки никогда не попадают в публичный список
Эти тесты подтверждают корректную изоляцию пользовательских данных
и безопасность публичного API.
"""

import pytest
from datetime import timedelta, time

from habits.models import Habit

pytestmark = pytest.mark.django_db


PUBLIC_URL = "/api/habits/public/"


def test_public_list_allows_anonymous(api_client, user, user2):
    """
    Проверка: публичный список привычек доступен анонимным пользователям.
    Сценарий:
    - создаётся публичная привычка другого пользователя
    - неавторизованный клиент выполняет GET-запрос
    Ожидаемое поведение:
    - запрос успешен (200 OK)
    - в ответе присутствует список результатов
    - возвращается ровно одна публичная привычка
    """
    Habit.objects.create(
        user=user2,
        action="Публичная привычка",
        time=time(12, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=True,
        is_pleasant=False,
    )

    resp = api_client.get(PUBLIC_URL)

    assert resp.status_code == 200
    assert "results" in resp.data
    assert len(resp.data["results"]) == 1


def test_public_list_returns_only_public(api_client, user, user2):
    """
    Проверка: публичный список возвращает только публичные привычки.
    Сценарий:
    - создаётся приватная привычка (is_public=False)
    - создаётся публичная привычка (is_public=True)
    - выполняется GET-запрос к публичному эндпоинту
    Ожидаемое поведение:
    - запрос успешен (200 OK)
    - в результатах присутствует только публичная привычка
    - приватные привычки полностью скрыты
    """
    Habit.objects.create(
        user=user2,
        action="Скрытая привычка",
        time=time(10, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=False,
    )
    Habit.objects.create(
        user=user2,
        action="Публичная привычка",
        time=time(11, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=True,
        is_pleasant=False,
    )

    resp = api_client.get(PUBLIC_URL)

    assert resp.status_code == 200
    actions = [x["action"] for x in resp.data["results"]]
    assert actions == ["Публичная привычка"]
