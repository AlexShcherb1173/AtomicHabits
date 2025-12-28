"""
URL-маршруты приложения notifications.
Содержит API-эндпоинты, связанные с интеграцией уведомлений,
в частности — привязкой Telegram-аккаунта пользователя.
"""

from django.urls import path

from .views import TelegramLinkAPIView

urlpatterns = [
    path(
        "telegram/link/",
        TelegramLinkAPIView.as_view(),
        name="telegram-link",
    ),
]
