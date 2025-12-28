"""
Конфигурация приложения accounts.
Приложение отвечает за:
- регистрацию пользователей
- аутентификацию
- token-based авторизацию
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """
    Конфигурация приложения accounts.
    Используется для управления жизненным циклом приложения
    и отображения человекочитаемого имени в Django Admin.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Аутентификация и пользователи"