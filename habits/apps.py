"""
Конфигурация приложения habits.
Приложение отвечает за:
- управление привычками пользователей
- бизнес-логику привычек (reward, related_habit, periodicity и т.д.)
- публичные и приватные списки привычек
"""

from django.apps import AppConfig


class HabitsConfig(AppConfig):
    """
    Конфигурация Django-приложения habits.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "habits"
    verbose_name = "Привычки"
