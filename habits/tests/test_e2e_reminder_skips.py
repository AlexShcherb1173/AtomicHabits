"""
Тесты негативных сценариев для Celery-задачи напоминаний о привычках.
Проверяется, что напоминания НЕ отправляются:
- если у пользователя нет Telegram-профиля
- если Telegram-профиль существует, но отключён (is_active=False)
Реальный Telegram API не используется — отправка сообщений замокана.
"""

import pytest
from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from habits.models import Habit
from notifications.models import TelegramProfile

pytestmark = pytest.mark.django_db


def test_task_skips_when_no_telegram_profile(user):
    """
    Проверка: если у пользователя НЕТ Telegram-профиля,
    напоминание о привычке не отправляется.
    Сценарий:
    1. Создаётся привычка с временем выполнения «сейчас».
    2. У пользователя отсутствует TelegramProfile.
    3. Запускается Celery-задача напоминаний.
    4. Проверяется, что send_telegram_message НЕ был вызван.
    Ожидаемое поведение:
    - задача корректно пропускает пользователя
    - ошибок не возникает
    """

    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)

    Habit.objects.create(
        user=user,
        action="Без телеги",
        time=current_time,
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=False,
    )

    from habits.tasks import send_habit_reminders

    with patch("habits.tasks.send_telegram_message") as send_mock:
        send_habit_reminders()

        send_mock.assert_not_called()


def test_task_skips_when_telegram_profile_inactive(user):
    """
    Проверка: если Telegram-профиль пользователя существует,
    но отключён (is_active=False), напоминание не отправляется.
    Сценарий:
    1. Пользователю создаётся TelegramProfile с is_active=False.
    2. Создаётся привычка с временем выполнения «сейчас».
    3. Запускается Celery-задача напоминаний.
    4. Проверяется, что send_telegram_message НЕ был вызван.
    Ожидаемое поведение:
    - система уважает настройку пользователя
    - уведомления не отправляются при отключённой интеграции
    """

    TelegramProfile.objects.create(
        user=user,
        chat_id="123",
        is_active=False,
    )

    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)

    Habit.objects.create(
        user=user,
        action="Телега отключена",
        time=current_time,
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=False,
    )

    from habits.tasks import send_habit_reminders

    with patch("habits.tasks.send_telegram_message") as send_mock:
        send_habit_reminders()

        send_mock.assert_not_called()