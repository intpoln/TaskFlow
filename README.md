# 📋 TaskFlow

TaskFlow — это REST API для управления задачами, проектами и категориями с полноценной системой аутентификации и авторизации. Проект реализован с использованием современных паттернов проектирования и следует принципам SOLID.

🌐 **Демо**: https://pet-taskflow.ddns.net/docs

## 📋 Содержание

- [Описание](#описание)
- [Технологии](#технологии)
- [Архитектура](#архитектура)
- [Функциональность](#функциональность)
- [Установка и запуск](#установка-и-запуск)
- [API документация](#api-документация)
- [Переменные окружения](#переменные-окружения)
- [Команды для работы](#команды-для-работы)
- [Авторы](#авторы)

## 📖 Описание

TaskFlow — это полнофункциональное REST API, состоящее из:
- **Backend**: REST API на FastAPI с асинхронной поддержкой
- **База данных**: PostgreSQL 18
- **Кэширование**: Redis 8.4
- **Веб-сервер**: Gunicorn + Uvicorn
- **Админ-панель**: SQLAdmin
- **Тестирование**: Pytest

Проект позволяет пользователям:
- Регистрироваться и авторизовываться с использованием JWT токенов
- Создавать и управлять своими проектами
- Создавать задачи с привязкой к проектам и категориям
- Управлять категориями задач
- Искать задачи по названию, категории или проекту
- Изменять статус задач
- Фильтровать задачи по статусу

## 🛠 Технологии

### Backend
- **Python 3.13**
- **FastAPI 0.128.0** — современный асинхронный веб-фреймворк
- **SQLAlchemy 2** — ORM с асинхронной поддержкой
- **PostgreSQL 18** (asyncpg 0.31.0) — реляционная база данных
- **Redis 7.1.0** (fastapi-cache2 0.2.2) — кэширование ответов API
- **Alembic 1.17.2** — миграции базы данных
- **Pydantic 2.12.5** — валидация данных и схемы
- **PyJWT 2.10.1** — JWT токены для аутентификации
- **Passlib[bcrypt]** — хеширование паролей
- **SQLAdmin 0.22.0** — админ-панель
- **Gunicorn 23.0.0** + **Uvicorn 0.40.0** — ASGI сервер
- **Pytest** - тестирование работы кода

### Инфраструктура
- **Docker** — контейнеризация
- **Docker Compose** — оркестрация контейнеров
- **Nginx** — reverse proxy (production)

## 🏗 Архитектура

Проект следует принципам **SOLID** и использует следующие паттерны проектирования:

- **Repository Pattern (вместе с DAO)** — абстракция доступа к данным (`src/repositories/`)
  - Инкапсулирует всю логику работы с БД
  - Централизованная обработка ошибок целостности данных
  - Упрощает тестирование и поддержку

- **Unit of Work (UoW)** — управление транзакциями (`src/uow/`)
  - Координация работы нескольких репозиториев
  - Атомарность операций
  - Управление жизненным циклом сессии БД

- **Service Layer** — бизнес-логика приложения (`src/services/`)
  - Отделение бизнес-логики от доступа к данным
  - Валидация на уровне сервисов
  - Обработка бизнес-исключений

- **Data Mapper** — разделение ORM-моделей и бизнес-логики
  - ORM модели (`src/models/`) отделены от бизнес-логики
  - Pydantic схемы (`src/schemas/`) для API и валидации

### Структура проекта

```
src/
├── api/          # FastAPI роутеры и зависимости
│   └── v1/       # API версионирование
├── models/       # SQLAlchemy ORM модели
├── schemas/      # Pydantic схемы (DTO)
├── repositories/ # Repository Pattern (DAO)
├── services/     # Бизнес-логика (Service Layer)
├── uow/          # Unit of Work
├── core/         # Исключения и базовые классы
├── admin/        # SQLAdmin конфигурация
├── connectors/   # Подключения к внешним сервисам (Redis)
└── scripts/      # Утилиты (создание суперпользователя)
```

## ✨ Функциональность

### Для всех пользователей
- Регистрация и авторизация
- Просмотр API документации (Swagger UI)

### Для авторизованных пользователей
- Создание, редактирование и удаление своих проектов
- Создание, редактирование и удаление своих задач
- Привязка задач к проектам и категориям
- Поиск задач по названию, описанию, категории или проекту
- Изменение статуса задач (TODO, IN_PROGRESS, DONE)
- Установка дедлайнов для задач
- Просмотр списка категорий

### Для суперпользователей
- Полный доступ к админ-панели SQLAdmin
- Создание и управление категориями

### Технические особенности
- 🔒 Защита на уровне БД (composite foreign keys, unique constraints)
- 🔐 JWT-аутентификация с refresh-токенами и user-agent fingerprinting
- 💾 Кэширование API-ответов с учетом пользователя и параметров поиска
- ⚡ Асинхронная обработка запросов
- 🛡️ Централизованная обработка ошибок с кастомными исключениями
- 📝 Автоматические миграции БД при запуске

## 🚀 Установка и запуск

### Предварительные требования

- Docker установлен на вашем компьютере
- Git для клонирования репозитория

### Клонирование репозитория

```bash
git clone https://github.com/intpoln/taskflow.git
cd taskflow
```

### Настройка переменных окружения

Создайте файл `.env` в корне проекта со следующим содержимым (см. раздел [Переменные окружения](#переменные-окружения)):

```env
# База данных
DB_HOST=postgres
DB_PORT=5432
DB_USER=db_user
DB_PASS=db_pass
DB_NAME=taskflow

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# JWT
JWT_SECRET_KEY=your-secret-key-here-min-32-chars
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-here-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
REFRESH_TOKEN_COOKIE_MAX_AGE=604800

# Суперпользователь
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_USERNAME=admin
SUPERUSER_PASSWORD=admin_password
```

### Запуск проекта

1. **Соберите и запустите контейнеры:**

```bash
docker compose up -d --build
```

Проект автоматически:
- Выполнит миграции БД (`alembic upgrade head`)
- Создаст суперпользователя (если его нет)
- Запустит Gunicorn сервер

### Доступ к приложению

После успешного запуска приложение будет доступно по адресам:

- **API Документация (Swagger UI)**: http://localhost:8000/docs
- **API Документация (ReDoc)**: http://localhost:8000/redoc
- **Админ-панель (SQLAdmin)**: http://localhost:8000/admin
- **API Endpoints**: http://localhost:8000/api/v1


### Тестирование приложения

Запустите контейнер с тестовой БД следующей командой: 

```bash
docker compose --env-file .env-test -f docker-compose.test.yml up -d
```

После запуска контейнера с тестовой БД запустите тесты из корневой директории:

```bash
pytest
```


## 📚 API документация

API документация доступна в двух форматах:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Основные эндпоинты

#### Аутентификация
- `POST /api/v1/auth/register` — Регистрация пользователя
- `POST /api/v1/auth/login` — Вход в систему (получение токенов)
- `POST /api/v1/auth/refresh` — Обновление access токена
- `POST /api/v1/auth/logout` — Выход из системы

#### Пользователи
- `GET /api/v1/users` — Список всех пользователей (только суперпользователи)

#### Проекты
- `GET /api/v1/projects` — Список проектов текущего пользователя
- `POST /api/v1/projects` — Создание проекта
- `GET /api/v1/projects/{project_id}` — Детали проекта
- `PUT /api/v1/projects/{project_id}` — Обновление проекта
- `PATCH /api/v1/projects/{project_id}` — Частичное обновление проекта
- `DELETE /api/v1/projects/{project_id}` — Удаление проекта

#### Задачи
- `GET /api/v1/tasks` — Список задач с фильтрацией и поиском
- `POST /api/v1/tasks` — Создание задачи
- `GET /api/v1/tasks/{task_id}` — Детали задачи
- `PUT /api/v1/tasks/{task_id}` — Обновление задачи
- `PATCH /api/v1/tasks/{task_id}` — Частичное обновление задачи
- `DELETE /api/v1/tasks/{task_id}` — Удаление задачи

#### Категории
- `GET /api/v1/categories` — Список всех категорий
- `POST /api/v1/categories` — Создание категории (только суперпользователи)
- `PUT /api/v1/categories/{category_id}` — Обновление категории
- `DELETE /api/v1/categories/{category_id}` — Удаление категории

Полный список эндпоинтов с примерами запросов доступен в Swagger UI.

## 🔐 Переменные окружения

Основные переменные окружения, которые необходимо настроить в файле `.env`:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `DB_HOST` | Хост базы данных | `postgres` |
| `DB_PORT` | Порт базы данных | `5432` |
| `DB_USER` | Пользователь БД | `postgres` |
| `DB_PASS` | Пароль БД | `your_password` |
| `DB_NAME` | Имя базы данных | `taskflow` |
| `REDIS_HOST` | Хост Redis | `redis` |
| `REDIS_PORT` | Порт Redis | `6379` |
| `REDIS_PASSWORD` | Пароль Redis | `your_redis_password` |
| `JWT_SECRET_KEY` | Секретный ключ для access токенов | `your-secret-key-32-chars-min` |
| `JWT_REFRESH_SECRET_KEY` | Секретный ключ для refresh токенов | `your-refresh-secret-key-32-chars-min` |
| `JWT_ALGORITHM` | Алгоритм подписи JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Время жизни access токена (минуты) | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Время жизни refresh токена (дни) | `7` |
| `REFRESH_TOKEN_COOKIE_MAX_AGE` | Время жизни cookie refresh токена (секунды) | `604800` |
| `SUPERUSER_EMAIL` | Email суперпользователя | `admin@example.com` |
| `SUPERUSER_USERNAME` | Username суперпользователя | `admin` |
| `SUPERUSER_PASSWORD` | Пароль суперпользователя | `admin_password` |

## 🛠 Команды для работы

### Управление контейнерами

```bash
# Запуск контейнеров
docker compose up -d

# Остановка контейнеров
docker compose down

# Пересборка контейнеров
docker compose up -d --build

# Просмотр логов
docker compose logs -f taskflow_backend_service
docker compose logs -f postgres
docker compose logs -f redis
```

### Локальная разработка без Docker

1. **Установите зависимости:**

```bash
# Используя uv (рекомендуется)
pip install uv
uv sync

# Или используя pip
pip install -r requirements.txt
```

2. **Настройте переменные окружения:**

Создайте `.env` файл с настройками для локальной разработки (используйте `localhost` вместо имен сервисов). Уберите backend сервис из docker-compose

3. **Запустите миграции:**

```bash
alembic upgrade head
```

4. **Создайте суперпользователя:**

```bash
python -m src.scripts.create_superuser
```

5. **Запустите сервер:**

```bash
python src/main.py
```

## 📄 Лицензия

Этот проект создан в образовательных целях.

## 👤 Автор

**intpoln** - [GitHub профиль](https://github.com/intpoln)