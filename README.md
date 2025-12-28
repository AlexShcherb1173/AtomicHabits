# 🧠 AtomicHabits API

Backend-сервис для трекинга привычек по методологии **Atomic Habits**  
с уведомлениями в **Telegram**, токен-авторизацией и фоновой обработкой задач.

Проект реализован на **Django + Django REST Framework**,  
с асинхронными задачами через **Celery + Redis** и полной API-документацией.

---

## 🚀 Возможности

- 🔐 Token-авторизация (DRF TokenAuthentication)
- 📋 CRUD привычек с бизнес-валидацией
- 🌍 Публичные привычки (read-only)
- ⏰ Напоминания по времени (Celery Beat)
- 🤖 Интеграция с Telegram (deep-link `/start <token>`)
- 📖 Swagger / OpenAPI документация
- ✅ Полное покрытие автотестами (pytest)

---

## 🏗️ Технологии

- Python 3.12+
- Django 6.0
- Django REST Framework
- drf-spectacular (Swagger / OpenAPI 3)
- Celery + Redis
- PostgreSQL
- pytest + APIClient
- requests (Telegram API)

---

## 📂 Структура проекта

AtomicHabits/  
├── accounts/ # Регистрация и логин  
│ ├── api_urls.py  
│ ├── serializers.py  
│ ├── views.py  
│ └── tests/  
│ └── test_auth_api.py  
│  
├── habits/ # Основная бизнес-логика привычек  
│ ├── admin.py  
│ ├── api_urls.py  
│ ├── models.py  
│ ├── serializers.py  
│ ├── validators.py  
│ ├── pagination.py  
│ ├── tasks.py # Celery-задачи  
│ ├── views.py  
│ └── tests/  
│ ├── test_habits_api.py  
│ ├── test_public_habits_api.py  
│ ├── test_habit_duration_validation.py  
│ ├── test_habit_pleasant_rules.py  
│ ├── test_habit_reward_related_validation.py  
│ ├── test_pagination_api.py  
│ ├── test_task_send_habit_reminders_unit.py  
│ ├── test_celery_enqueue_mock.py   
│ ├── test_e2e_habit_reminder_flow.py  
│ └── test_e2e_reminder_skips.py  
│  
├── notifications/ # Telegram-интеграция  
│ ├── models.py  
│ ├── telegram.py  
│ ├── serializers.py  
│ ├── views.py  
│ ├── api_urls.py  
│ └── tests/  
│ ├── test_telegram_link_token.py  
│ └── test_telegram_send_message.py  
│  
├── config/  
│ ├── settings.py  
│ ├── urls.py  
│ ├── celery_prj.py  
│ ├── asgi.py  
│ └── wsgi.py  
│  
├── telegram_bot.py # Отдельный polling-бот  
├── manage.py  
├── pytest.ini  
├── pyproject.toml  
├── requirements.txt  
└── README.md  

---

## 🔐 Авторизация

Используется **TokenAuthentication**.

### Регистрация
POST /api/auth/register/

shell
Копировать код

### Логин (получение токена)
POST /api/auth/login/

css
Копировать код

Ответ:
```json
{
  "token": "abcdef123456"
}
```
### Использование:


Authorization: Token abcdef123456  
Swagger поддерживает кнопку Authorize.  

#### 📖 API Документация
Swagger UI:
👉 http://127.0.0.1:8000/api/docs/

OpenAPI schema:
👉 http://127.0.0.1:8000/api/schema/

Документация описывает:  
авторизацию,  
все эндпоинты,  
примеры запросов/ответов,  
права доступа.  

🧠 Привычки (Habits)  
Бизнес-правила (по ТЗ)  
❌ Нельзя одновременно reward и related_habit  

🔗 related_habit — только pleasant  

😊 Pleasant-привычка:  

не может иметь reward  

не может иметь related_habit  

⏱️ duration: 0 < duration ≤ 120 секунд  

📅 periodicity: от 1 до 7 дней  

👤 CRUD — только над своими привычками  

🌍 Публичные привычки:  

доступны всем  

read-only  

🤖 Telegram-интеграция  
Схема работы  
Пользователь запрашивает ссылку:  

GET /api/telegram/link/  
Получает deep-link:  

php-template  

https://t.me/<BOT>?start=<token>  
Переходит в Telegram  

Бот:  
  
валидирует токен  

привязывает chat_id  

активирует уведомления  

Celery отправляет напоминания  

⏰ Напоминания (Celery + Beat)  
Задача send_habit_reminders  

Запускается каждую минуту  

Фильтрация:  

привычки по текущему времени (с точностью до минуты)  

только с активным Telegram-профилем  

Отправка сообщений через Telegram API  

🧪 Тестирование  
Используется pytest.  

Типы тестов  
✅ Unit-тесты моделей и валидаторов  

✅ API-тесты (DRF APIClient)  

✅ Permission-тесты  

✅ Celery mock (delay, apply_async)  

✅ Telegram API mock (requests.post)  

✅ E2E-тест:   


#### привычка → напоминание → Telegram
Запуск тестов  

Или выборочно:  

pytest habits/tests notifications/tests  
⚙️ Переменные окружения (.env)  
env  

DJANGO_SECRET_KEY=...  
DJANGO_DEBUG=True  
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost  

POSTGRES_DB=AtomicHabits_db  
POSTGRES_USER=postgres  
POSTGRES_PASSWORD=postgres  
POSTGRES_HOST=127.0.0.1  
POSTGRES_PORT=5432  

TELEGRAM_BOT_TOKEN=...  
TELEGRAM_BOT_USERNAME=AtomicHabitsBot  
TELEGRAM_API_URL=https://api.telegram.org  

CORS_ALLOWED_ORIGINS=http://localhost:5173  
## ▶️ Запуск проекта

python -m venv .venv  
source .venv/bin/activate  # или .venv\Scripts\activate  
pip install -r requirements.txt  

python manage.py migrate  
python manage.py runserver  
Redis:  

redis-server  
Celery:  

 celery -A config worker -B -l info  
### 🧩 Статус проекта
✔ Архитектура готова  
✔ API стабильное  
✔ Документация оформлена  
✔ Тесты покрывают бизнес-логику  
✔ Готов к frontend-интеграции и деплою  

### 👨‍💻 Автор
Проект разработан как production-ready backend  
с упором на чистую архитектуру, тестируемость и масштабируемость.  


