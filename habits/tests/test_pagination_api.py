"""
Тесты пагинации для списка привычек пользователя.
Проверяется, что:
- список привычек возвращается с пагинацией
- размер страницы ограничен 5 элементами
- общее количество (`count`) соответствует числу привычек
- вторая страница содержит оставшиеся элементы
Эти тесты подтверждают корректную настройку пагинации
в соответствии с требованиями ТЗ.
"""

import pytest
from datetime import timedelta, time

from habits.models import Habit

pytestmark = pytest.mark.django_db


LIST_URL = "/api/habits/"


def test_my_habits_pagination_page_size_5(auth_client, user):
    """
    Проверка пагинации списка привычек пользователя (page size = 5).
    Сценарий:
    - у пользователя создаётся 7 привычек
    - выполняется запрос к первой странице списка
    - затем выполняется запрос ко второй странице
    Ожидаемое поведение:
    - `count` равен общему количеству привычек (7)
    - первая страница содержит ровно 5 элементов
    - вторая страница содержит оставшиеся 2 элемента
    """
    for i in range(7):
        Habit.objects.create(
            user=user,
            action=f"Привычка {i}",
            time=time(10, 0),
            periodicity=1,
            duration=timedelta(seconds=60),
            is_public=False,
            is_pleasant=False,
        )

    # Первая страница
    resp = auth_client.get(LIST_URL)
    assert resp.status_code == 200
    assert resp.data["count"] == 7
    assert len(resp.data["results"]) == 5

    # Вторая страница
    resp2 = auth_client.get(f"{LIST_URL}?page=2")
    assert resp2.status_code == 200
    assert len(resp2.data["results"]) == 2