"""
Инициализация конфигурационного пакета проекта.
Экспортирует Celery-приложение, чтобы:
- Django автоматически загружал Celery при старте
- worker и beat использовали одно и то же приложение
- можно было импортировать celery_app из config
Используется стандартный паттерн:
from config import celery_app
"""

from .celery_prj import app as celery_app

__all__ = ("celery_app",)
