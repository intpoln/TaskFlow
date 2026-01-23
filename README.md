<div align="center">

# TaskFlow

**REST API для управления задачами и проектами**

[![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-8.4-DC382D?logo=redis&logoColor=white)](https://redis.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Demo](https://pet-taskflow.ddns.net/docs) • [API Docs](https://pet-taskflow.ddns.net/docs) • [Admin Panel](https://pet-taskflow.ddns.net/admin)

</div>

---

## О проекте

TaskFlow — полнофункциональный REST API для управления задачами, проектами и категориями. Проект демонстрирует применение современных практик backend-разработки: чистую архитектуру, паттерны проектирования и production-ready инфраструктуру.

### Ключевые особенности

- **JWT + OAuth 2.0** — аутентификация через логин/пароль и Google
- **CRUD операции** — управление проектами, задачами и категориями  
- **Поиск и фильтрация** — по названию, статусу, категории, проекту
- **Кэширование** — Redis для оптимизации производительности
- **Фоновые задачи** — Celery + RabbitMQ для email-уведомлений
- **Админ-панель** — SQLAdmin для управления данными
- **CI/CD** — автоматические тесты, сборка и деплой

---

## Технологический стек

<table>
<tr>
<td width="50%">

### Backend
| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.13 | Язык программирования |
| FastAPI | 0.128 | Веб-фреймворк |
| SQLAlchemy | 2.0 | ORM (async) |
| Pydantic | 2.12 | Валидация данных |
| Alembic | 1.17 | Миграции БД |
| Celery | 5.6 | Фоновые задачи |
| Pytest | 9.0 | Тестирование |

</td>
<td width="50%">

### Инфраструктура
| Технология | Версия | Назначение |
|------------|--------|------------|
| PostgreSQL | 18 | База данных |
| Redis | 8.4 | Кэширование |
| RabbitMQ | 3.13 | Message broker |
| Docker | - | Контейнеризация |
| Gunicorn | 23.0 | WSGI/ASGI сервер |
| Nginx | - | Reverse proxy |
| GitLab CI | - | CI/CD pipeline |

</td>
</tr>
</table>

### Дополнительные библиотеки

- **python-jose** — JWT токены
- **passlib[bcrypt]** — хеширование паролей
- **httpx** — HTTP клиент
- **fastapi-cache2** — кэширование ответов API
- **SQLAdmin** — админ-панель
- **MailerSend** — отправка email

---

## Архитектура

Проект построен на принципах **Clean Architecture** и **SOLID**:

```
src/
├── api/              # API слой (роутеры, зависимости)
│   └── v1/           # Версионирование API
├── services/         # Бизнес-логика (Service Layer)
├── repositories/     # Доступ к данным (Repository + DAO)
├── uow/              # Управление транзакциями (Unit of Work)
├── models/           # ORM модели (SQLAlchemy)
├── schemas/          # DTO (Pydantic)
├── core/             # Кастомные исключения
├── tasks/            # Celery задачи
├── integrations/     # Внешние сервисы (Email)
├── admin/            # SQLAdmin конфигурация
└── connectors/       # Подключения (Redis)
tests/                # Тесты
```

### Применённые паттерны

| Паттерн | Расположение | Описание |
|---------|--------------|----------|
| **Repository** | `repositories/` | Абстракция доступа к данным |
| **Unit of Work** | `uow/` | Координация транзакций между репозиториями |
| **Service Layer** | `services/` | Инкапсуляция бизнес-логики |
| **Dependency Injection** | `api/dependencies.py` | Внедрение зависимостей через FastAPI |
| **DTO (Data Transfer Object)** | `schemas/` | Pydantic схемы для API |

---

## Функциональность

### Аутентификация и авторизация

- Регистрация с email-подтверждением (MailerSend)
- JWT аутентификация (access + refresh токены)
- OAuth 2.0 через Google
- User-agent fingerprinting для безопасности
- Разграничение прав (user / superuser)

### API возможности

| Ресурс | Операции | Особенности |
|--------|----------|-------------|
| **Проекты** | CRUD | Привязка к пользователю |
| **Задачи** | CRUD + поиск | Статусы (TODO, IN_PROGRESS, DONE), дедлайны |
| **Категории** | CRUD | Управление только для superuser |
| **Пользователи** | Просмотр | Только для superuser |

### Технические особенности

- Асинхронная обработка всех запросов
- Кэширование с учётом пользователя и параметров
- Централизованная обработка ошибок
- Автоматические миграции при запуске
- Healthcheck для всех сервисов

---

## Быстрый старт

### Требования

- Docker и Docker Compose
- Git

### Установка

```bash
# Клонирование репозитория
git clone https://github.com/intpoln/taskflow.git
cd taskflow

# Создание .env файла (см. .env.example)
cp .env.example .env
# Отредактируйте .env, заполнив необходимые значения

# Запуск
docker compose up -d --build
```

### Доступ

| Сервис | URL |
|--------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| Admin Panel | http://localhost:8000/admin |
| API | http://localhost:8000/v1 |

---

## Конфигурация

### Основные переменные окружения

```env
# База данных
DB_HOST=postgres
DB_PORT=5432
DB_USER=taskflow
DB_PASS=your_password
DB_NAME=taskflow

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest
RABBITMQ_DEFAULT_VHOST=/

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars
JWT_REFRESH_SECRET_KEY=your-refresh-key-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# OAuth 2.0 (Google)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Email (MailerSend)
MAILERSEND_API_KEY=your_mailersend_api_key
MAILERSEND_FROM_EMAIL=noreply@yourdomain.com

# Superuser
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_USERNAME=admin
SUPERUSER_PASSWORD=secure_password
```

---

## API Endpoints

### Аутентификация (`/v1/auth`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| POST | `/register` | Регистрация |
| POST | `/login` | Вход |
| POST | `/refresh` | Обновление токена |
| POST | `/logout` | Выход |

### OAuth (`/oauth`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/google` | Начало OAuth flow |
| GET | `/google/callback` | Callback от Google |

### Проекты (`/v1/projects`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/` | Список проектов |
| POST | `/` | Создать проект |
| GET | `/{id}` | Получить проект |
| PUT | `/{id}` | Обновить проект |
| PATCH | `/{id}` | Частичное обновление |
| DELETE | `/{id}` | Удалить проект |

### Задачи (`/v1/tasks`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/` | Список с фильтрацией |
| POST | `/` | Создать задачу |
| GET | `/{id}` | Получить задачу |
| PUT | `/{id}` | Обновить задачу |
| PATCH | `/{id}` | Частичное обновление |
| DELETE | `/{id}` | Удалить задачу |

### Категории (`/v1/categories`)

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/` | Список категорий |
| POST | `/` | Создать (superuser) |
| PUT | `/{id}` | Обновить (superuser) |
| DELETE | `/{id}` | Удалить (superuser) |

---

## Тестирование

```bash
# Запуск тестовой БД
docker compose --env-file .env-test -f docker-compose.test.yml up -d

# Запуск тестов
pytest
```

---

## CI/CD Pipeline

Проект использует **GitLab CI/CD** с тремя стадиями:

```yaml
stages:
  - test      # Запуск pytest
  - build     # Сборка Docker образа
  - deploy    # Деплой на сервер
```

Pipeline автоматически запускается при push в ветку `main`.

---

## Локальная разработка

```bash
# Установка зависимостей (рекомендуется uv)
pip install uv
uv sync

# Или через pip
pip install -r requirements.txt

# Миграции
alembic upgrade head

# Создание superuser (данные из .env)
python -m src.scripts.create_superuser

# Запуск dev-сервера
python src/main.py
```

---

## Структура Docker

```yaml
services:
  backend:     # FastAPI приложение (Gunicorn + Uvicorn)
  redis:       # Кэширование
  rabbitmq:    # Message broker для Celery
  celery:      # Worker для фоновых задач
```

---

## Демо

Проект задеплоен и доступен для тестирования:

**https://pet-taskflow.ddns.net**

- [Swagger UI](https://pet-taskflow.ddns.net/docs) — интерактивная документация
- [Admin Panel](https://pet-taskflow.ddns.net/admin) — админ-панель

---

## Автор

**intpoln** — [GitHub](https://github.com/intpoln)

---

<div align="center">

Made with FastAPI

</div>
