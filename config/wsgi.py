"""
WSGI-конфигурация проекта AtomicHabits.
Этот модуль предоставляет WSGI-приложение,
которое используется WSGI-серверами (Gunicorn, uWSGI и т.п.)
для запуска Django в продакшене.
Документация:
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Указываем Django, какой settings-модуль использовать
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# WSGI-приложение
application = get_wsgi_application()
