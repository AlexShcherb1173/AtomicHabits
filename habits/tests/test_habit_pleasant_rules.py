"""
Тесты бизнес-правил для приятных привычек (is_pleasant=True).
Проверяются ограничения:
- Приятная привычка не может иметь вознаграждение (reward)
- Приятная привычка не может быть связана с другой привычкой (related_habit)
Эти правила соответствуют концепции Atomic Habits:
приятная привычка сама является наградой и не требует дополнительных поощрений.
"""

import pytest
from datetime import timedelta, time

from habits.models import Habit

pytestmark = pytest.mark.django_db


HABITS_URL = "/api/habits/"


def base_payload(**overrides):
    """
    Формирует базовый payload для создания приятной привычки.
    По умолчанию:
    - is_pleasant=True
    - без награды
    - без связанной привычки
    Используется как отправная точка для проверки ограничений.
    """
    data = {
        "action": "Сериальчик",
        "time": "22:00:00",
        "periodicity": 1,
        "duration": "00:01:00",
        "is_public": False,
        "is_pleasant": True,
        "reward": "",
        "related_habit": None,
    }
    data.update(overrides)
    return data


def test_pleasant_cannot_have_reward(auth_client):
    """
    Проверка: приятная привычка не может иметь поле `reward`.
    Сценарий:
    - создаётся привычка с is_pleasant=True
    - одновременно передаётся текстовое вознаграждение
    Ожидаемое поведение:
    - API отклоняет запрос (HTTP 400)
    - ошибка возвращается либо в поле `reward`,
      либо как общая ошибка в `non_field_errors`
    """
    payload = base_payload(reward="Награда")

    resp = auth_client.post(HABITS_URL, payload, format="json")

    assert resp.status_code == 400
    assert ("reward" in resp.data) or ("non_field_errors" in resp.data)


def test_pleasant_cannot_have_related_habit(auth_client, user):
    """
    Проверка: приятная привычка не может иметь связанную привычку.
    Сценарий:
    - создаётся другая приятная привычка
    - при создании новой привычки она указывается как related_habit
    Ожидаемое поведение:
    - API отклоняет запрос (HTTP 400)
    - ошибка возвращается либо в поле `related_habit`,
      либо как общая ошибка в `non_field_errors`
    """
    other_pleasant = Habit.objects.create(
        user=user,
        action="Ванна",
        time=time(21, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=True,
    )

    payload = base_payload(related_habit=other_pleasant.id)

    resp = auth_client.post(HABITS_URL, payload, format="json")

    assert resp.status_code == 400
    assert ("related_habit" in resp.data) or ("non_field_errors" in resp.data)
