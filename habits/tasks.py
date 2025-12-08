import datetime

from celery import shared_task
from django.utils import timezone

from habits.models import Habit
from notifications.telegram import send_telegram_message


@shared_task
def send_habit_reminders():
    """
    Периодическая задача, которая ищет привычки,
    совпадающие по времени с текущим моментом, и шлёт уведомления в Telegram.
    Запускается, например, каждую минуту Celery Beat'ом.
    """
    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)

    # Найдём все привычки на это время (без учёта periodicity по дате — базовый вариант)
    habits = Habit.objects.filter(time=current_time)

    for habit in habits:
        user = habit.user

        # Проверяем, есть ли у пользователя Telegram-профиль
        telegram_profile = getattr(user, "telegram_profile", None)
        if not telegram_profile or not telegram_profile.is_active:
            continue

        chat_id = telegram_profile.chat_id

        # Текст напоминания
        text = (
            f"⏰ <b>Напоминание о привычке</b>\n\n"
            f"{habit.title}\n\n"
            f"Не забудь выполнить привычку и отметить прогресс! 💪"
        )

        send_telegram_message(chat_id, text)