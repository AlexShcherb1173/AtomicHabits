"""
ASGI конфигурация проекта AtomicHabits.
Используется для:
- асинхронных серверов (Uvicorn, Daphne, Hypercorn)
- WebSocket (в будущем, при необходимости)
- масштабируемых production-развёртываний

Подробнее:
https://docs.djangoproject.com/en/stable/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Устанавливаем настройки Django по умолчанию для ASGI-серверов
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# ASGI-приложение, которое будет использовать сервер
application = get_asgi_application()
