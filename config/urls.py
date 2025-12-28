"""
Главная URL-конфигурация проекта AtomicHabits.
Здесь регистрируются:
- Django admin
- API авторизации (регистрация / логин)
- API привычек и мест
- API Telegram-интеграции
- OpenAPI схема и документация (Swagger / Redoc)
Все API-эндпоинты доступны по префиксу `/api/`.
"""

from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    # ============================================================
    # Admin
    # ============================================================
    path("admin/", admin.site.urls),
    # ============================================================
    # Auth API
    # ============================================================
    # Регистрация и получение токена
    path("api/auth/", include("accounts.api_urls")),
    # ============================================================
    # Habits API
    # ============================================================
    # CRUD привычек, мест + публичные привычки
    path("api/", include("habits.api_urls")),
    # ============================================================
    # Notifications API
    # ============================================================
    # Telegram-интеграция (привязка аккаунта)
    path("api/", include("notifications.api_urls")),
    # ============================================================
    # OpenAPI / Swagger
    # ============================================================
    # Машинно-читаемая OpenAPI схема
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Swagger UI
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Redoc UI
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
