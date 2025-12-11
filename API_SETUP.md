# Настройка FastAPI с movies.db

## Овервью

Этот скрипт описывает, как все роутеры FastAPI подключены к главному приложению для работы с базой данных `movies.db`.

## Структура проекта

```
project/
├── main.py              # Маин файл приложения (УПДЕЙТНО ОБНОВЛЕН)
├── movies.db           # База данных SQLite
├── app/
│   ├── __init__.py
│   ├── config.py       # Конфигурация приложения
│   ├── api/            # Модули роутеров
│   │   ├── __init__.py
│   │   ├── auth.py         # Автентификация
│   │   ├── movies.py       # Процедуры с фильмами
│   │   ├── movies_real.py  # Процедуры с реальными фильмами
│   │   ├── reviews.py      # Процедуры с рецензиями
│   │   ├── users.py        # Процедуры с пользователями
│   │   ├── picks.py        # Топики и подборки
│   │   ├── movie_picks.py  # Связь фильма и подборки
│   │   ├── movie_stats.py  # Статистика фильмов
│   │   ├── roles.py        # Роли пользователей
│   │   ├── dependencies.py # Зависимости API
│   │   ├── sample.py
│   │   └── test.py
│   ├── database/      # Модули данных
│   ├── models/         # ORM модели
│   ├── schemas/        # Pydantic схемы
│   ├── services/       # Бизнес-логика
│   ├── repositories/   # Препозитории
│   ├── utils/          # Утилиты
│   ├── exceptions/     # Ошибки
│   ├── scripts/        # Псрпы администратора
│   └── dependencies.py
├── static/          # Статические ресурсы
├── templates/       # HTML шаблоны
└── requirements.txt # Зависимости проекта
```

## Подключенные роутеры

### 1. **Автентификация** (`/api/v1/auth`)
- `POST /api/v1/auth/login` - Вход в систему
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/logout` - Выход из системы

### 2. **Фильмы** (`/api/v1/movies`)
- `GET /api/v1/movies` - Получить список фильмов
- `GET /api/v1/movies/{id}` - Получить фильм по ID
- `POST /api/v1/movies` - Создать новый фильм
- `PUT /api/v1/movies/{id}` - Обновить фильм
- `DELETE /api/v1/movies/{id}` - Удалить фильм
- `GET /api/v1/movies/genres/list` - Получить список жанров

### 3. **Фильмы (Real)** (`/api/v1/movies-real`)
- Наполняютя теми же концептами как в роутере фильмов

### 4. **Рецензии** (`/api/v1/reviews`)
- `GET /api/v1/reviews` - Получить рецензии
- `GET /api/v1/reviews/{id}` - Получить рецензию по ID
- `POST /api/v1/reviews` - Написать рецензию
- `PUT /api/v1/reviews/{id}` - Обновить рецензию
- `DELETE /api/v1/reviews/{id}` - Удалить рецензию

### 5. **Пользователи** (`/api/v1/users`)
- `GET /api/v1/users` - Получить всех пользователей
- `GET /api/v1/users/{id}` - Получить пользователя по ID
- `GET /api/v1/users/me` - Получить текущего пользователя
- `PUT /api/v1/users/{id}` - Обновить пользователя
- `DELETE /api/v1/users/{id}` - Удалить пользователя

### 6. **Подборки** (`/api/v1/picks`)
- `GET /api/v1/picks` - Получить все подборки
- `GET /api/v1/picks/{id}` - Получить подборку по ID
- `POST /api/v1/picks` - Создать новую подборку
- `PUT /api/v1/picks/{id}` - Обновить подборку
- `DELETE /api/v1/picks/{id}` - Удалить подборку

### 7. **Связь фильма и подборки** (`/api/v1/movie-picks`)
- `GET /api/v1/movie-picks` - Получить все связи
- `POST /api/v1/movie-picks` - Создать новую связь
- `DELETE /api/v1/movie-picks/{id}` - Удалить связь

### 8. **Статистика фильмов** (`/api/v1/movie-stats`)
- `GET /api/v1/movie-stats` - Получить статистику
- `GET /api/v1/movie-stats/{movie_id}` - Получить статистику для конкретного фильма

### 9. **Роли** (`/api/v1/roles`)
- `GET /api/v1/roles` - Получить все роли
- `GET /api/v1/roles/{id}` - Получить роль по ID

## Как запустить приложение

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Запуск на Windows (Powershell)

```powershell
python main.py
```

или

```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Запуск на Linux/Mac

```bash
python main.py
```

или

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Навигация

Когда сервер будет работают, посетите:

- **Главная**: http://localhost:8000/
- **Проверка здоровья**: http://localhost:8000/health
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## Конфигурация базы данных

Основная база данных - **SQLite** (файл `movies.db`).

Эту базу можно использовать с DBeaver или другими графическими тоолами для SQLite.

### Примарные таблицы:

- **movies** - информация о фильмах
- **users** - данные пользователей
- **reviews** - рецензии пользователей
- **picks** - подборки и топики
- **movie_picks** - связь между фильмами и подборками
- **roles** - роли пользователей

## Ноты

1. Все роутеры вида открыты для вломены разработки (CORS `allow_origins=["*"]`). Для production используйте ограничения.

2. Автоматические миграции базы данных в папке `migrations` (по утилите Alembic).

3. Логи выводятся в консоль во время запуска приложения.

4. Об использовании JWT токенов см. роутер `auth.py`.
