"""
Тесты бизнес-правил привычек (Habits).
Проверяются ключевые ограничения доменной логики:
- взаимоисключаемость reward и related_habit
- ограничения по длительности выполнения
- требования к pleasant-привычкам
- корректность выбора связанной привычки
- ограничения на периодичность выполнения
Все проверки выполняются через API,
что гарантирует валидацию на уровне DRF-сериализаторов.
"""

import pytest
from datetime import timedelta, time

from habits.models import Habit

pytestmark = pytest.mark.django_db


def test_reward_and_related_habit_mutually_exclusive(auth_client, user):
    """
    Нельзя одновременно указать reward и related_habit.
    Сценарий:
    - создаётся pleasant-привычка
    - при создании новой привычки указываются и reward, и related_habit
    Ожидаемое поведение:
    - API возвращает 400 Bad Request
    - ошибка присутствует минимум в одном из полей:
      reward или related_habit
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

    payload = {
        "action": "Гулять",
        "time": "19:00:00",
        "periodicity": 1,
        "duration": "00:01:00",
        "is_public": False,
        "is_pleasant": False,
        "related_habit": pleasant.id,
        "reward": "Десерт",  # запрещённая комбинация
    }

    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400
    assert "reward" in resp.data or "related_habit" in resp.data


def test_duration_must_be_le_120_seconds(auth_client):
    """
    Длительность выполнения привычки не должна превышать 120 секунд.
    Сценарий:
    - отправляется duration = 3 минуты (180 секунд)
    Ожидаемое поведение:
    - API возвращает 400 Bad Request
    - ошибка присутствует в поле duration
    """
    payload = {
        "action": "Планка",
        "time": "07:00:00",
        "periodicity": 1,
        "duration": "00:03:00",  # 180 секунд
        "is_public": False,
        "is_pleasant": False,
    }

    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400
    assert "duration" in resp.data


def test_related_habit_must_be_pleasant(auth_client, user):
    """
    Связанная привычка должна быть pleasant.
    Сценарий:
    - создаётся не pleasant-привычка
    - она передаётся как related_habit
    Ожидаемое поведение:
    - API возвращает 400 Bad Request
    - ошибка присутствует в поле related_habit
    """
    not_pleasant = Habit.objects.create(
        user=user,
        action="Полезная привычка",
        time=time(10, 0),
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=False,
    )

    payload = {
        "action": "Ещё одна",
        "time": "11:00:00",
        "periodicity": 1,
        "duration": "00:01:00",
        "is_public": False,
        "is_pleasant": False,
        "related_habit": not_pleasant.id,
    }

    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400
    assert "related_habit" in resp.data


def test_pleasant_habit_cannot_have_reward_or_related_habit(auth_client, user):
    """
    Pleasant-привычка не может иметь reward или related_habit.
    Сценарий:
    - создаётся pleasant-привычка
    - указывается reward
    Ожидаемое поведение:
    - API возвращает 400 Bad Request
    """
    payload = {
        "action": "Сериальчик",
        "time": "22:00:00",
        "periodicity": 1,
        "duration": "00:01:00",
        "is_public": False,
        "is_pleasant": True,
        "reward": "Ещё награда",  # запрещено
    }

    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400


def test_periodicity_cannot_be_more_than_7_days(auth_client):
    """
    Периодичность выполнения привычки ограничена максимум 7 днями.
    Сценарий:
    - передаётся periodicity = 14 дней
    Ожидаемое поведение:
    - API возвращает 400 Bad Request
    - ошибка присутствует в поле periodicity
    """
    payload = {
        "action": "Раз в две недели",
        "time": "12:00:00",
        "periodicity": 14,  # запрещено
        "duration": "00:01:00",
        "is_public": False,
        "is_pleasant": False,
    }

    resp = auth_client.post("/api/habits/", payload, format="json")
    assert resp.status_code == 400
    assert "periodicity" in resp.data