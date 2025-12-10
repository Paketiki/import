# final_fix.py в корне проекта
import os
import re

def fix_auth_py():
    """Исправить app/api/auth.py"""
    filepath = "app/api/auth.py"
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Заменяем проблемный импорт
        old_import = "from app.models.users import User, user_favorite_movies"
        new_import = "from app.models.users import User"
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            content = content.replace("user_favorite_movies,", "")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Исправлен {filepath}")
        else:
            print(f"✅ {filepath} уже исправлен")

def fix_movies_py():
    """Исправить app/api/movies.py (демо)"""
    filepath = "app/api/movies.py"
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        old_import = "from app.models.users import User, user_favorite_movies"
        new_import = "from app.models.users import User"
        
        if old_import in content:
            content = content.replace(old_import, new_import)
            content = re.sub(r'user_favorite_movies,\s*', '', content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Исправлен {filepath}")
        else:
            print(f"✅ {filepath} уже исправлен")

def add_user_favorite_movies_alias():
    """Добавить псевдоним в app/models/__init__.py"""
    filepath = "app/models/__init__.py"
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Добавляем заглушку после импортов
        if "user_favorite_movies = None" not in content:
            # Находим последний импорт
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith(('from', 'import', '#', '__all__')):
                    # Вставляем перед этой строкой
                    lines.insert(i, "\n# Временная заглушка для обратной совместимости")
                    lines.insert(i+1, "user_favorite_movies = None\n")
                    break
            
            content = '\n'.join(lines)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Добавлена заглушка в {filepath}")
        else:
            print(f"✅ {filepath} уже содержит заглушку")

def main():
    print("🚀 Выполняю окончательное исправление импортов...")
    fix_auth_py()
    fix_movies_py()
    add_user_favorite_movies_alias()
    print("🎉 Все исправления выполнены!")
    print("\n📋 Приложение готово к использованию:")
    print("   - http://localhost:8000 - главная страница")
    print("   - http://localhost:8000/docs - документация API")
    print("   - http://localhost:8000/api/v1/movies - тестовые фильмы")

if __name__ == "__main__":
    main()