"""
Celery конфигурация проекта AtomicHabits.
Назначение файла:
- инициализация Celery-приложения
- загрузка настроек из Django settings.py
- автоматическое обнаружение задач (tasks.py) во всех приложениях
Используется для:
- фоновых задач (напоминания о привычках)
- периодических задач (Celery Beat)
- асинхронной обработки без блокировки HTTP-запросов
"""

import os

from celery import Celery

# Указываем Django settings для Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Создаём Celery-приложение
app = Celery("config")

# Загружаем настройки Celery из Django settings
# Все параметры должны начинаться с префикса CELERY_
app.config_from_object("django.conf:settings", namespace="CELERY")

# Автоматически находим tasks.py во всех INSTALLED_APPS
app.autodiscover_tasks()
