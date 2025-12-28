"""
Тесты Celery-задачи отправки напоминаний о привычках.
Проверяется корректная интеграция:
- Habit → Celery task → Telegram sender
без реального обращения к Telegram API (используется mock).
Цель теста — убедиться, что при совпадении времени привычки
задача формирует корректное сообщение и вызывает отправку.
"""

import pytest
from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from habits.models import Habit
from notifications.models import TelegramProfile

pytestmark = pytest.mark.django_db


def test_send_habit_reminders_calls_send_telegram_message(user):
    """
    Проверка: Celery-задача вызывает send_telegram_message
    при наличии активного Telegram-профиля и подходящей привычки.
    Сценарий:
    - у пользователя есть активный TelegramProfile
    - существует привычка, время которой совпадает с текущей минутой
    - выполняется задача send_habit_reminders()
    Ожидаемое поведение:
    - функция send_telegram_message вызывается ровно один раз
    - используется корректный chat_id
    - текст сообщения содержит:
        * динамический title привычки
        * маркер «Напоминание о привычке»
    """
    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)

    # Активный Telegram-профиль пользователя
    TelegramProfile.objects.create(
        user=user,
        chat_id="777000",
        is_active=True,
    )

    # Привычка, подходящая под текущее время
    habit = Habit.objects.create(
        user=user,
        action="Сделать зарядку",
        time=current_time,
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=False,
    )

    from habits.tasks import send_habit_reminders

    # Мокаем реальную отправку сообщений в Telegram
    with patch("habits.tasks.send_telegram_message", return_value=True) as send_mock:
        send_habit_reminders()

        send_mock.assert_called_once()
        called_chat_id, called_text = send_mock.call_args.args

        assert called_chat_id == "777000"
        assert habit.title in called_text
        assert "Напоминание о привычке" in called_text
