"""
URL-конфигурация для аутентификации пользователей.
Эндпоинты:
- POST /api/auth/register/ — регистрация нового пользователя
- POST /api/auth/login/    — авторизация и получение Token
Используется Token-based аутентификация (DRF authtoken).
"""

from django.urls import path

from .views import RegisterAPIView, TokenLoginAPIView


urlpatterns = [
    # Регистрация нового пользователя
    # POST /api/auth/register/
    path("register/", RegisterAPIView.as_view(), name="auth-register"),
    # Авторизация пользователя и получение токена
    # POST /api/auth/login/
    path("login/", TokenLoginAPIView.as_view(), name="auth-login"),
]
