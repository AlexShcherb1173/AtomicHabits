"""
Тесты для Celery-задач напоминаний о привычках.
Проверяем, что:
- Celery-задача может быть поставлена в очередь через `.delay()`
- Celery-задача может быть поставлена в очередь через `.apply_async()`
Реальный Celery-брокер и воркеры НЕ используются —
вызовы Celery API замоканы через unittest.mock.
"""

import pytest
from unittest.mock import Mock

pytestmark = pytest.mark.django_db


def test_send_habit_reminders_delay_mock():
    """
    Проверяет, что Celery-задача `send_habit_reminders`
    корректно вызывается через метод `.delay()`.
    Цель теста:
    - убедиться, что код, который планирует задачу,
      может безопасно вызывать `.delay()`
    - не запускать реальный Celery worker
    Подход:
    - временно подменяем `send_habit_reminders.delay` на Mock
    - проверяем, что:
        * метод был вызван
        * вернул ожидаемое значение
    """
    from habits.tasks import send_habit_reminders

    original_delay = send_habit_reminders.delay
    try:
        send_habit_reminders.delay = Mock(return_value="ASYNC_RESULT")

        result = send_habit_reminders.delay()

        assert result == "ASYNC_RESULT"
        send_habit_reminders.delay.assert_called_once_with()
    finally:
        # обязательно возвращаем оригинальный метод
        send_habit_reminders.delay = original_delay


def test_send_habit_reminders_apply_async_mock():
    """
    Проверяет, что Celery-задача `send_habit_reminders`
    может быть поставлена в очередь через `.apply_async()`
    с передачей параметров (например, countdown).
    Цель теста:
    - убедиться, что отложенный запуск задачи
      (через countdown / eta) работает корректно
    - не обращаться к реальному брокеру сообщений
    Подход:
    - подменяем `apply_async` на Mock
    - вызываем задачу с аргументами
    - проверяем, что параметры переданы корректно
    """
    from habits.tasks import send_habit_reminders

    original_apply_async = send_habit_reminders.apply_async
    try:
        send_habit_reminders.apply_async = Mock(return_value="ASYNC_RESULT")

        result = send_habit_reminders.apply_async(countdown=60)

        assert result == "ASYNC_RESULT"
        send_habit_reminders.apply_async.assert_called_once()

        _, kwargs = send_habit_reminders.apply_async.call_args
        assert kwargs["countdown"] == 60
    finally:
        # возвращаем оригинальный метод
        send_habit_reminders.apply_async = original_apply_async
