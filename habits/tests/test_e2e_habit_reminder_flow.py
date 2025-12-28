"""
E2E-тест сценария напоминаний о привычках без реального Telegram.
Проверяется полный пользовательский сценарий:
1. Пользователь получает одноразовый токен привязки Telegram.
2. Telegram-аккаунт пользователя считается привязанным (эмуляция бота).
3. Создаётся привычка с временем выполнения «сейчас».
4. Запускается Celery-задача напоминаний.
5. Проверяется, что сообщение было отправлено в Telegram
   (через mock, без реального API).
"""

import pytest
from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from habits.models import Habit
from notifications.models import TelegramProfile, TelegramLinkToken

pytestmark = pytest.mark.django_db


def test_e2e_link_token_to_profile_to_reminder(user):
    """
    E2E-тест: «привязка Telegram → привычка → напоминание».
    Цель теста:
    - проверить корректную связку между:
        * токеном привязки Telegram,
        * Telegram-профилем пользователя,
        * привычкой,
        * Celery-задачей напоминаний
    - убедиться, что уведомление отправляется
      только при наличии активного Telegram-профиля

    Важно:
    - реальный Telegram API не используется
    - отправка сообщения замокана
    """

    # 1) Пользователь получает одноразовый токен для привязки Telegram
    link_token = TelegramLinkToken.create_for_user(
        user=user,
        lifetime_minutes=30,
    )

    assert link_token.is_valid() is True

    # 2) Эмуляция поведения Telegram-бота:
    #    пользователь нажал /start <token>, и профиль был привязан
    TelegramProfile.objects.create(
        user=user,
        chat_id="100500",
        username="@alex",
        is_active=True,
    )

    assert user.telegram_profile.chat_id == "100500"

    # 3) Создаём привычку с временем выполнения "сейчас"
    #    (задача фильтрует привычки строго по минуте)
    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)

    habit = Habit.objects.create(
        user=user,
        action="Пить воду",
        time=current_time,
        periodicity=1,
        duration=timedelta(seconds=60),
        is_public=False,
        is_pleasant=False,
    )

    # 4) Запускаем задачу напоминаний и проверяем,
    #    что сообщение "отправилось" в Telegram
    from habits.tasks import send_habit_reminders

    with patch(
        "habits.tasks.send_telegram_message",
        return_value=True,
    ) as send_mock:
        send_habit_reminders()

        # Проверяем, что сообщение было отправлено ровно один раз
        send_mock.assert_called_once()

        # Проверяем корректность аргументов вызова
        chat_id, text = send_mock.call_args.args

        assert chat_id == "100500"
        assert habit.title in text