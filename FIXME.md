# Ошибки импорта Модулей

Данный документ описывает возможные проблемы импорта роутеров.

## Проверьте следующие файлы:

1. **app/schemas/** - должен содержать:
   - `__init__.py` (может быть пустым)
   - схемы для ответов

2. **app/services/** - должен содержать:
   - `__init__.py` (может быть пустым)
   - `auth.py` - сервис автентификации

3. **app/repositories/** - навестию (repositories) данных

## Ошибка в логах:

```
WARNING - ⚠ Не удалось импортировать app.api.movies: ...
```

### Причины:

1. В модулю мовис импортирует `MovieResponse`, `MovieDetailResponse`, `MovieCreate` из `app.schemas`
2. В модулю мовис импортирует `get_current_user` из `app.services.auth`

Чтобы проверить, автомно сгенерируйте Пытоне скрипт:

```python
try:
    from app.schemas import MovieResponse
    print("ОК - MovieResponse импортируется")
except ImportError as e:
    print(f"ОШИБКА: {e}")
    print("Нужно создать app/schemas/__init__.py и определить схемы")
```

## Кым удалить:

Темпорарно для тестирования приложения, можно комментировать сложные импорты в роутерах.

Экран ананалитики:

```bash
cd C:\Users\User\Pictures\import
python -c "from app.api import movies; print('OK')"
```

Если выдаст ошибку - видим какая зависимость не работает.
