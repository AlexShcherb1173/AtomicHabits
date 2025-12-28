"""
Конфигурация приложения notifications.
Приложение отвечает за:
- интеграцию с Telegram;
- хранение Telegram-профилей пользователей;
- генерацию одноразовых токенов для привязки Telegram;
- отправку уведомлений (через Celery-задачи).
"""

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """
    Конфигурация Django-приложения notifications.
    """

    name = "notifications"
    verbose_name = "Уведомления (Telegram)"
