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


### Deploy & CI/CD (Production)

Проект AtomicHabits использует GitHub Actions +   
Docker Compose для автоматического деплоя на удалённый   
Linux-сервер по SSH.

Docker управляет контейнерами  

systemd (опционально) — автозапуском  

GitHub Actions — сборкой, тестами и доставкой образа на сервер  

SCP + docker load — доставкой Docker-образа (без registry)  

#### Требования к серверу

Удалённый сервер (рекомендуется Ubuntu 20.04+):  

Docker ≥ 24  

Docker Compose v2  

SSH-доступ по ключу  

Открытые порты:  

80 — nginx  

443 — (если планируется HTTPS)  

Пользователь с правами sudo  

#### Установка Docker и Docker Compose
sudo apt update  
sudo apt install -y ca-certificates curl gnupg  
curl -fsSL https://get.docker.com | sudo sh  
sudo usermod -aG docker $USER  
newgrp docker  
  
docker --version  
docker compose version  

#### Структура на сервере

Проект разворачивается в каталоге:  
  
/opt/atomichabits  
  
Минимально ожидаемая структура:  

/opt/atomichabits  
├── docker-compose.yml  
├── docker/  
│   ├── django/  
│   │    └── Dockerfile  
│   │    └── entrypoint.sh  
│   └── nginx/  
│       └── nginx.conf  
├── .env.docker          # ❗ хранится только на сервере  
├── atomichabits_latest.tar  
└── .tmp/                # временные файлы деплоя  
  
#### Подготовка SSH
1. Создай SSH-ключ (локально)  
ssh-keygen -t ed25519 -C "github-deploy-atomichabits"  

По умолчанию ключ будет в:  

~/.ssh/id_ed25519  
  
2. Добавь публичный ключ на сервер  
ssh-copy-id user@SERVER_IP  
  
3. Проверь вход  
ssh user@SERVER_IP  

#### GitHub Secrets
  
В репозитории GitHub открой:  
  
Settings → Secrets and variables → Actions → New repository secret  
  
Добавь следующие secrets:  
  
Имя	-------------------------Описание  
SSH_HOST---------------	IP или домен сервера  
SSH_PORT---------------	Обычно 22  
SSH_USER---------------	Пользователь на сервере  
SSH_PRIVATE_KEY----	Приватный SSH-ключ (id_ed25519)  
DEPLOY_PATH-----------	/opt/atomichabits  
ENV_DOCKER	------------Полное содержимое .env.docker  

Важно:
SSH_PRIVATE_KEY добавляется целиком, включая строки:  

-----BEGIN OPENSSH PRIVATE KEY-----  
...
-----END OPENSSH PRIVATE KEY-----  

#### Конфигурация окружения (.env.docker)
  
Файл не хранится в git и создаётся только на сервере  
(или передаётся через GitHub Secret ENV_DOCKER).  
  
nano /opt/atomichabits/.env.docker  

Пример:

DJANGO_SECRET_KEY=super-secret-key  
DJANGO_DEBUG=False  
DJANGO_ALLOWED_HOSTS=example.com,www.example.com  

POSTGRES_DB=AtomicHabits_db  
POSTGRES_USER=postgres  
POSTGRES_PASSWORD=postgres  
POSTGRES_HOST=db  
POSTGRES_PORT=5432  
  
REDIS_HOST=redis  
REDIS_PORT=6379  
  
TIME_ZONE=Europe/Amsterdam  
LANGUAGE_CODE=ru  
  
TELEGRAM_BOT_TOKEN=  
TELEGRAM_BOT_USERNAME=  
TELEGRAM_API_URL=https://api.telegram.org  

#### CI/CD Workflow (GitHub Actions)

Workflow выполняет:  
  
Checkout кода  
  
Линтинг (ruff)  
  
Запуск тестов (pytest + coverage)  
  
Проверку сборки Docker-образа  
  
Сборку production-образа  
  
docker save → .tar  
  
SCP-копирование на сервер  
  
docker load  
 
docker compose up -d  
  
Выполнение миграций  
  
##### Триггер workflow

Workflow запускается автоматически:  
  
при push в ветку feature  
  
(при необходимости можно добавить workflow_dispatch)  
  
#### Деплой (как это работает)
На GitHub Actions  
  
Docker-образ собирается локально  

Сохраняется как atomichabits_latest.tar  
  
Копируется на сервер по SCP  
  
Загружается через docker load  
  
Запускается через docker compose  
  
Вручную на сервере (если нужно)    
cd /opt/atomichabits  
docker compose up -d  
  
#### Проверка после деплоя
Контейнеры  
docker compose ps  

Ожидаемый статус:  
  
web — Up  
  
nginx — Up 
  
db — Healthy  
  
redis — Healthy  
  
celery — Up  
  
celery_beat — Up  
  
Проверка API  
curl http://SERVER_IP/  

Swagger:  
  
http://SERVER_IP/api/schema/swagger-ui/  

#### Тесты и Celery в CI  
  
В CI используется режим:  

CELERY_TASK_ALWAYS_EAGER=True  
CELERY_TASK_EAGER_PROPAGATES=True  
  
Это позволяет:
  
запускать тесты без Redis  
  
выполнять Celery-задачи синхронно  
  
избежать падений pipeline  
 
Важно помнить

❌ .env.docker никогда не коммитится
❌ секреты не хранятся в репозитории
✅ деплой полностью автоматизирован
✅ Docker-образы доставляются без registry
✅ volumes не монтируют несуществующие файлы
✅ проект поднимается одной командой

### 👨‍💻 Автор
Проект разработан как production-ready backend  
с упором на чистую архитектуру, тестируемость и масштабируемость.  


