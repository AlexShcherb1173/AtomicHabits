"""
Celery-задачи приложения habits.
Содержит периодические задачи (Celery Beat), которые отправляют напоминания
о привычках в Telegram.
Задача `send_habit_reminders` предполагается к запуску раз в минуту.
Она выбирает привычки, у которых `time` совпадает с текущим временем
(точность до минуты), и отправляет сообщение в Telegram пользователю,
если у него подключён TelegramProfile (is_active=True).
"""

from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from habits.models import Habit
from notifications.telegram import send_telegram_message


@shared_task(name="habits.tasks.send_habit_reminders")
def send_habit_reminders() -> int:
    """
    Отправляет Telegram-напоминания о привычках, которые должны выполняться сейчас.
    Логика:
    1) Берём текущее локальное время и обнуляем секунды/микросекунды.
    2) Находим привычки, у которых поле `time` совпадает с текущей минутой.
    3) Для каждой привычки проверяем наличие у пользователя TelegramProfile:
       - профиль должен существовать;
       - профиль должен быть активным (is_active=True).
    4) Отправляем сообщение через `send_telegram_message`.
    Возвращает:
        int: количество попыток отправки (сколько раз вызвали send_telegram_message).
             Это удобно для тестов/логирования (не равно числу успехов, т.к. telegram
             может вернуть ok=False).
    """
    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)

    # Важно: select_related, чтобы не дёргать БД в цикле.
    # Фильтрация по telegram_profile делается через join, чтобы сразу отсеять тех,
    # у кого нет профиля или он выключен.
    habits = (
        Habit.objects.filter(time=current_time)
        .select_related("user", "place", "related_habit", "user__telegram_profile")
        .filter(
            Q(user__telegram_profile__isnull=False)
            & Q(user__telegram_profile__is_active=True)
        )
    )

    sent_count = 0

    for habit in habits:
        chat_id = habit.user.telegram_profile.chat_id

        text = (
            "⏰ <b>Напоминание о привычке</b>\n\n"
            f"{habit.title}\n\n"
            "Не забудь выполнить привычку и отметить прогресс! 💪"
        )

        send_telegram_message(chat_id, text)
        sent_count += 1

    return sent_count
