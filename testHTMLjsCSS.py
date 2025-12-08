# Временный код для проверки структуры
import os
from pathlib import Path

current_dir = Path(__file__).parent
print("Текущая директория:", current_dir)
print("\nСодержимое проекта:")
for item in current_dir.iterdir():
    print(f"  - {item.name} {'(dir)' if item.is_dir() else ''}")

# Проверяем папки
print("\nПроверка папок:")
print(f"templates существует: {(current_dir / 'templates').exists()}")
print(f"static существует: {(current_dir / 'static').exists()}")

if (current_dir / 'templates').exists():
    print("\nФайлы в templates:")
    for file in (current_dir / 'templates').iterdir():
        print(f"  - {file.name}")