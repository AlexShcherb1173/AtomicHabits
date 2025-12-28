"""
Тесты валидации поля `duration` (время выполнения привычки).
Проверяются бизнес-правила:
- duration может быть NULL (необязательное поле)
- duration должно быть строго больше 0 секунд
- duration не должно превышать 120 секунд
- граничные значения (119 и 120 секунд) допустимы
Тесты выполняются через API и проверяют поведение сериализатора и view.
"""

import pytest

pytestmark = pytest.mark.django_db


HABITS_URL = "/api/habits/"


def base_payload(**overrides):
    """
    Формирует базовый валидный payload для создания привычки.
    Используется как основа во всех тестах,
    чтобы проверять только конкретные отклонения от валидных данных.
    :param overrides: поля, которые нужно переопределить
    :return: dict — данные для POST /api/habits/
    """
    data = {
        "action": "Пить воду",
        "time": "12:00:00",
        "periodicity": 1,
        "is_public": False,
        "is_pleasant": False,
        "duration": "00:01:00",  # 60 секунд — валидное значение
    }
    data.update(overrides)
    return data


def test_duration_can_be_null(auth_client):
    """
    Проверка: поле `duration` может быть передано как null.
    Ожидаемое поведение:
    - API отклоняет запрос (400),
      если duration=None не допускается бизнес-логикой проекта
    - В ответе присутствует ошибка по полю `duration`
    """
    payload = base_payload(duration=None)

    response = auth_client.post(HABITS_URL, payload, format="json")

    assert response.status_code == 400
    assert "duration" in response.data


def test_duration_must_be_positive(auth_client):
    """
    Проверка: duration должно быть строго больше 0 секунд.
    Сценарий:
    - Передаётся duration = 00:00:00
    - Это значение считается невалидным
    Ожидаемое поведение:
    - HTTP 400
    - Сообщение об ошибке указывает,
      что значение должно быть больше нуля
    """
    payload = base_payload(duration="00:00:00")

    response = auth_client.post(HABITS_URL, payload, format="json")

    assert response.status_code == 400
    assert "duration" in response.data

    msg = str(response.data["duration"][0]).lower()
    assert "больше" in msg
    assert ("нуля" in msg) or ("0" in msg)


def test_duration_less_than_120_seconds_is_valid(auth_client):
    """
    Проверка: duration меньше 120 секунд считается валидным.
    Сценарий:
    - Передаётся duration = 119 секунд
    - Значение укладывается в допустимый диапазон
    Ожидаемое поведение:
    - Привычка успешно создаётся (201)
    - Значение duration сохраняется без изменений
    """
    payload = base_payload(duration="00:01:59")  # 119 секунд

    response = auth_client.post(HABITS_URL, payload, format="json")

    assert response.status_code == 201
    assert response.data["duration"] == "00:01:59"


def test_duration_equal_120_seconds_is_valid(auth_client):
    """
    Проверка граничного значения: duration ровно 120 секунд допустимо.
    Сценарий:
    - Передаётся duration = 00:02:00
    - Это максимальное допустимое значение
    Ожидаемое поведение:
    - Привычка успешно создаётся (201)
    - duration сохраняется корректно
    """
    payload = base_payload(duration="00:02:00")  # 120 секунд

    response = auth_client.post(HABITS_URL, payload, format="json")

    assert response.status_code == 201
    assert response.data["duration"] == "00:02:00"


def test_duration_more_than_120_seconds_is_invalid(auth_client):
    """
    Проверка: duration больше 120 секунд запрещено.
    Сценарий:
    - Передаётся duration = 121 секунда
    - Значение превышает допустимый максимум
    Ожидаемое поведение:
    - HTTP 400
    - Сообщение об ошибке явно указывает
      на превышение лимита в 120 секунд
    """
    payload = base_payload(duration="00:02:01")

    response = auth_client.post(HABITS_URL, payload, format="json")

    assert response.status_code == 400
    assert "duration" in response.data

    msg = str(response.data["duration"][0])
    assert "не должно превышать 120 секунд" in msg