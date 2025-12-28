"""
Тесты бизнес-правил для полезных привычек:
reward ↔ related_habit (взаимоисключающие поля).
Проверяются ограничения:
- Нельзя указывать одновременно reward и related_habit
- Можно указывать только reward
- Можно указывать только related_habit
- related_habit обязан быть приятной привычкой (is_pleasant=True)
Эти правила отражают модель Atomic Habits:
полезная привычка может вознаграждаться либо приятной привычкой,
либо произвольным вознаграждением, но не обоими сразу.
"""

import pytest
from datetime import timedelta, time

from habits.models import Habit

pytestmark = pytest.mark.django_db


HABITS_URL = "/api/habits/"


def base_payload(**overrides):
    """
    Формирует базовый валидный payload для полезной привычки.
    По умолчанию:
    - is_pleasant=False (полезная привычка)
    - reward пустой
    - related_habit отсутствует
    Используется как основа для тестов взаимоисключающих правил.
    """
    data = {
        "action": "Гулять",
        "time": "19:00:00",
        "periodicity": 1,
        "duration": "00:01:00",
        "is_public": False,
        "is_pleasant": False,
        "reward": "",
        "related_habit": None,
    }
    data.update(overrides)
    return data


def test_cannot_set_reward_and_related_habit_together(auth_client, user):
    """
    Проверка: нельзя одновременно указывать reward и related_habit.
    Сценарий:
    - создаётся приятная привычка
    - при создании полезной привычки указываются:
        * reward
        * related_habit
    Ожидаемое поведение:
    - API отклоняет запрос (HTTP 400)
    - ошибка может прийти как field error,
      так и как non_field_errors (зависит от реализации)
    """
    pleasant = Habit.objects.create(
        user=user,
        action="Ванна с пеной",
        time=time(21, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=True,
    )

    payload = base_payload(reward="Десерт", related_habit=pleasant.id)

    resp = auth_client.post(HABITS_URL, payload, format="json")

    assert resp.status_code == 400
    assert (
        ("reward" in resp.data)
        or ("related_habit" in resp.data)
        or ("non_field_errors" in resp.data)
    )


def test_can_set_only_reward(auth_client):
    """
    Проверка: полезная привычка может иметь только reward без related_habit.
    Сценарий:
    - reward задан
    - related_habit отсутствует
    Ожидаемое поведение:
    - привычка успешно создаётся (HTTP 201)
    - reward сохранён
    - related_habit == None
    """
    payload = base_payload(reward="Десерт", related_habit=None)

    resp = auth_client.post(HABITS_URL, payload, format="json")

    assert resp.status_code == 201
    assert resp.data["reward"] == "Десерт"
    assert resp.data["related_habit"] is None


def test_can_set_only_related_habit(auth_client, user):
    """
    Проверка: полезная привычка может иметь только related_habit без reward.
    Сценарий:
    - создаётся приятная привычка
    - она указывается как related_habit
    - reward пустой
    Ожидаемое поведение:
    - привычка успешно создаётся (HTTP 201)
    - related_habit сохранён
    - reward пустая строка
    """
    pleasant = Habit.objects.create(
        user=user,
        action="Чай с лимоном",
        time=time(20, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=True,
    )

    payload = base_payload(reward="", related_habit=pleasant.id)

    resp = auth_client.post(HABITS_URL, payload, format="json")

    assert resp.status_code == 201
    assert resp.data["reward"] == ""
    assert resp.data["related_habit"] == pleasant.id


def test_related_habit_must_be_pleasant(auth_client, user):
    """
    Проверка: related_habit обязан быть приятной привычкой.
    Сценарий:
    - создаётся привычка с is_pleasant=False
    - она передаётся как related_habit
    Ожидаемое поведение:
    - API отклоняет запрос (HTTP 400)
    - ошибка возвращается либо в поле related_habit,
      либо как non_field_errors
    """
    not_pleasant = Habit.objects.create(
        user=user,
        action="Полезная (не pleasant)",
        time=time(10, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=False,
    )

    payload = base_payload(related_habit=not_pleasant.id)

    resp = auth_client.post(HABITS_URL, payload, format="json")

    assert resp.status_code == 400
    assert ("related_habit" in resp.data) or ("non_field_errors" in resp.data)