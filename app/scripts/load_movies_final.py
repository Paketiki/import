#!/usr/bin/env python3
"""
Комплексный скрипт для загрузки фильмов
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal
from app.models.users import User
from app.services.movie_loader import MovieLoader

def get_or_create_system_user(db):
    """Получает или создает системного пользователя"""
    system_user = db.query(User).filter(
        User.username == "system_loader"
    ).first()
    
    if system_user:
        print(f"Используем существующего системного пользователя: ID={system_user.id}")
        return system_user.id
    
    # Если пользователя нет, создаем его
    try:
        new_user = User(
            username="system_loader",
            email="system@movieapp.com",
            password_hash="system_loader_hash"  # Добавляем обязательное поле
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Создан новый системный пользователь: ID={new_user.id}")
        return new_user.id
    except Exception as e:
        print(f"Ошибка при создании пользователя: {e}")
        return None

def load_movies_safe(use_system_user=True):
    """Безопасная загрузка фильмов"""
    print("=" * 50)
    print("Загрузка фильмов из script.js в базу данных")
    print("=" * 50)
    
    db = SessionLocal()
    try:
        # Определяем ID пользователя
        user_id = None
        if use_system_user:
            user_id = get_or_create_system_user(db)
            if not user_id:
                print("⚠️ Не удалось получить системного пользователя")
                print("⚠️ Будут загружены фильмы без указания created_by")
        
        # Загружаем фильмы
        loader = MovieLoader(db)
        result = loader.load_movies_from_list(
            created_by_user_id=user_id,
            skip_existing=True
        )
        
        # Выводим результаты
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТЫ ЗАГРУЗКИ:")
        print("=" * 50)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return 1
        
        print(f"Total movies in file: {result['total_in_file']}")
        print(f"Successfully loaded: {result['loaded']}")
        print(f"Skipped (already exist): {result['skipped']}")
        
        if result['errors']:
            print(f"\nErrors ({len(result['errors'])}):")
            for i, error in enumerate(result['errors'], 1):
                print(f"  {i}. {error}")
        
        print(f"\nUsed user_id: {user_id if user_id else 'not specified'}")
        
        # Показываем пример загруженных данных
        if result['loaded'] > 0:
            from app.models.movies import Movie
            latest_movies = db.query(Movie).order_by(Movie.id.desc()).limit(3).all()
            print(f"\nLatest added movies:")
            for movie in latest_movies:
                print(f"  • {movie.title} ({movie.release_year})")
        
        return 0
        
    except Exception as e:
        print(f"\nCritical error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    # Параметры загрузки
    USE_SYSTEM_USER = True  # Измените на False, если не хотите создавать пользователя
    
    print("Loading settings:")
    print(f"  • Use system user: {'Yes' if USE_SYSTEM_USER else 'No'}")
    print(f"  • Skip existing movies: Yes")
    
    # Автоматически начинаем загрузку без запроса подтверждения
    sys.exit(load_movies_safe(USE_SYSTEM_USER))