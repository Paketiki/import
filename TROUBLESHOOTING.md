# Отключение трудностей (Troubleshooting)

## Ошибка: `ImportError: cannot import name 'Base' from 'app.database.database'`

### Проблема

```
File "C:\Users\User\Pictures\import\app\models\base.py", line 2, in <module>
    from app.database.database import Base
ImportError: cannot import name 'Base' from 'app.database.database'
```

### Причина

`Base` (абстрактное базовое класс SQLAlchemy) не был доступен в `app/database/database.py`.

### Решение

убедитесь, что в файле `app/database/database.py` есть строки:

```python
from sqlalchemy.ext.declarative import declarative_base

# Создаем Base
Base = declarative_base()
```

и что `app/models/base.py` импортирует из правильного места:

```python
from app.database.database import Base
```

---

## Ошибка: "Нет модуля app.api"

### Проблема

```
ModuleNotFoundError: No module named 'app.api'
```

### Причина

Папка `app/api` не содержит файл `__init__.py` или роутеры.

### Решение

1. Проверьте структуру:

```bash
dir app\api
```

2. Наоборот, убедитесь, что `app/api/__init__.py` пустой (или содержит только комментарии):

```python
# app/api/__init__.py
# Этот файл может быть пустым
```

---

## Ошибка: "Порт 8000 уже занят"

### Проблема

```
Error: Address already in use
```

### Причина

На порте 8000 уже работает другое приложение.

### Решение

**Вариант 1: Остановить на другом порте**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**Вариант 2: Остановить старые процессы (Windows)**

```bash
netstat -ano | findstr :8000
kill /PID <PID> /F
```

**Вариант 3: Остановить старые процессы (Linux/Mac)**

```bash
lsof -i :8000
kill -9 <PID>
```

---

## Ошибка: "Не найдены movies.db"

### Проблема

```
SqliteOperationalError: unable to open database file
```

### Причина

База данных `movies.db` не где-то расположена или права доступа ограничены.

### Решение

1. Найдите файл:

```bash
ls -la *.db  # Linux/Mac
dir *.db     # Windows
```

2. Прави доступа (Linux/Mac):

```bash
chmod 644 movies.db
```

3. Проверьте поть в `app/database/database.py`:

```python
DATABASE_URL = "sqlite:///./movies.db"  # Работает для локального со сигнатурой
```

---

## Ошибка: "Странные символы в логах"

### Проблема

```
Кодировка символов нарушена в выводе
```

### Причина

Проблема с кодировкой консоли на Windows.

### Решение

```bash
# Установите UTF-8 кодировку для PowerShell
$env:PYTHONIOENCODING="utf-8"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Ошибка: "Module not found: app.schemas"

### Проблема

```
ModuleNotFoundError: No module named 'app.schemas'
```

### Причина

Папка `app/schemas/` не содержит необходимых файлов или `__init__.py`.

### Решение

1. Проверьте, существуют ли файлы:

```bash
dir app\schemas\  # Windows
ls -la app/schemas/  # Linux/Mac
```

2. Создайте `app/schemas/__init__.py`, если его нет:

```python
# app/schemas/__init__.py
# Файл может быть пустым
```

---

## Ошибка: "Что-то на русском не отображается"

### Решение

Проверьте кодировку файла:

```bash
# Windows PowerShell
$env:PYTHONIOENCODING="utf-8"

# Linux/Mac
export PYTHONIOENCODING="utf-8"
```

---

## Не работает что-то еще?

### Checklist:

- [ ] Установлены ли зависимости? `pip install -r requirements.txt`
- [ ] Используется ли Python 3.9+? `python --version`
- [ ] Находитесь ли вы в виртуальном окружении? `.venv` активирован?
- [ ] Находится ли файл `movies.db` в корне проекта?
- [ ] Работает ли `/health` endpoint? `curl http://localhost:8000/health`
- [ ] Видите ли вы логи при запуске?
- [ ] Проверьте файл `main.py` - не содержит ли опечаток?

### Когда ничего не помогает:

1. Удалите кэш Python:

```bash
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

2. Пересоздайте виртуальное окружение:

```bash
rm -rf .venv  # Linux/Mac
rmdir /s /q .venv  # Windows

python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

3. Проверьте журнал ошибок и создайте issue на GitHub с текстом ошибки.
