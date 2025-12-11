# Быстрый старт (Quick Start)

## Шаг 1: Установка пакетов

```bash
# Windows (Powershell)
pip install -r requirements.txt

# Linux/Mac
pip install -r requirements.txt
```

## Шаг 2: Запуск сервера

```bash
# Опция 1: Прямыми выводом
 python main.py

# Опция 2: Через uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Шаг 3: Тестирование API

Откройте браузер и навигируйте:

### 1. Проверка статуса API
```
GET http://localhost:8000/health
```

**Ответ:**
```json
{
  "status": "ok",
  "message": "КиноВзор API работает нормально",
  "version": "1.0.0"
}
```

### 2. Получение списка фильмов
```
GET http://localhost:8000/api/v1/movies
```

### 3. Получение списка жанров
```
GET http://localhost:8000/api/v1/movies/genres/list
```

### 4. Получение конкретного фильма
```
GET http://localhost:8000/api/v1/movies/1
```

## Шаг 4: Контроль API документация

**Swagger UI (Interactive API Documentation):**
```
http://localhost:8000/api/docs
```

**ReDoc (Alternative Documentation):**
```
http://localhost:8000/api/redoc
```

**OpenAPI JSON Schema:**
```
http://localhost:8000/api/openapi.json
```

## Примеры запросов с curl

### Получение всех фильмов
```bash
curl http://localhost:8000/api/v1/movies
```

### Получение фильмов с фильтров
```bash
curl "http://localhost:8000/api/v1/movies?genre=drama&rating_min=7.5"
```

### Поиск фильмов
```bash
curl "http://localhost:8000/api/v1/movies?search=Titanic"
```

### Получение списка с фильтром по подборке
```bash
curl "http://localhost:8000/api/v1/movies?pick=best-of-2024"
```

## Проблемы и решения

### Проблема: Порт 8000 уже занят

```bash
# Используйте другой порт
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Проблема: Модуль его не найден или ошибка импорта

```bash
# Это может быть, потому что структура папок app/ еще не полна
# Обыкновенно, если все роутеры имеют атрибут `router`
# Оставьте сами обйявления роутеров
```

## Полезные команды

### Остановка сервера
```bash
Ctrl + C  # Тажете Ctrl + C в терминале
```

### Проверъте что зависимости установлены
```bash
pip list | findstr fastapi  # Windows
pip list | grep fastapi     # Linux/Mac
```

## Ничего отиследить

Если что-то не работает, напишите иссю в репозитории включая:

1. Ос (Вындоус, Mac, Linux)
2. Версию Python (`python --version`)
3. Полнотекст ошибки
4. Шаги, которые вас тревожат

## Это не всё!

Для большими детали см. **API_SETUP.md**
