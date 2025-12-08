#!/usr/bin/env python3
"""
Скрипт для загрузки фильмов из script.js в базу данных
"""
import sys
from pathlib import Path
import logging

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal
from app.services.movie_loader import MovieLoader
from app.config import settings
from app.models.users import User

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def get_or_create_system_user(db):
    """Получает или создает системного пользователя"""
    try:
        # Пробуем найти системного пользователя по ID из настроек
        if settings.SYSTEM_USER_ID:
            system_user = db.query(User).filter(User.id == settings.SYSTEM_USER_ID).first()
            if system_user:
                logger.info(f"Найден системный пользователь: {system_user.username} (ID={system_user.id})")
                return system_user.id
        
        # Или создаем нового
        system_user = User(
            username="system_loader",
            email="system@movieapp.com"
        )
        db.add(system_user)
        db.commit()
        db.refresh(system_user)
        logger.info(f"Создан системный пользователь: ID={system_user.id}")
        return system_user.id
        
    except Exception as e:
        logger.error(f"Ошибка при работе с системным пользователем: {e}")
        return None

def load_movies():
    """Основная функция загрузки фильмов"""
    logger.info("=" * 60)
    logger.info(f"Запуск загрузки фильмов из {settings.MOVIES_JS_FILE_PATH}")
    logger.info("=" * 60)
    
    db = SessionLocal()
    try:
        # Определяем ID пользователя для created_by
        created_by_user_id = None
        
        if settings.DEFAULT_CREATED_BY_USER_ID:
            # Проверяем, существует ли пользователь с указанным ID
            user = db.query(User).filter(User.id == settings.DEFAULT_CREATED_BY_USER_ID).first()
            if user:
                created_by_user_id = settings.DEFAULT_CREATED_BY_USER_ID
                logger.info(f"Используем пользователя с ID={created_by_user_id}")
            else:
                logger.warning(f"Пользователь с ID={settings.DEFAULT_CREATED_BY_USER_ID} не найден")
        
        # Если не указан или не найден, создаем/используем системного
        if not created_by_user_id:
            created_by_user_id = get_or_create_system_user(db)
            if created_by_user_id:
                logger.info(f"Используем системного пользователя: ID={created_by_user_id}")
        
        # Загружаем фильмы
        loader = MovieLoader(db)
        result = loader.load_movies_to_db(
            js_file_path=settings.MOVIES_JS_FILE_PATH,
            created_by_user_id=created_by_user_id,
            skip_existing=True
        )
        
        # Логируем результаты
        if "error" in result:
            logger.error(f"Ошибка загрузки: {result['error']}")
            return 1
        
        logger.info("=" * 60)
        logger.info("РЕЗУЛЬТАТЫ ЗАГРУЗКИ:")
        logger.info(f"Всего фильмов в файле: {result['total_in_file']}")
        logger.info(f"Успешно загружено: {result['loaded']}")
        logger.info(f"Пропущено (уже существуют): {result['skipped']}")
        
        if result['errors']:
            logger.warning(f"Найдено ошибок: {len(result['errors'])}")
            for error in result['errors'][:5]:  # Показываем только первые 5 ошибок
                logger.warning(f"  - {error}")
            if len(result['errors']) > 5:
                logger.warning(f"  ... и еще {len(result['errors']) - 5} ошибок")
        
        logger.info("=" * 60)
        
        # Показываем пример загруженных данных
        if result['loaded'] > 0:
            from app.models.movies import Movie
            latest_movies = db.query(Movie).order_by(Movie.id.desc()).limit(3).all()
            logger.info("Последние добавленные фильмы:")
            for movie in latest_movies:
                logger.info(f"  • {movie.title} ({movie.release_year})")
        
        return 0
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    # Парсим аргументы командной строки
    import argparse
    
    parser = argparse.ArgumentParser(description="Загрузка фильмов из JS в базу данных")
    parser.add_argument("--user-id", type=int, help="ID пользователя для поля created_by")
    parser.add_argument("--js-file", type=str, help="Путь к JS файлу с данными")
    parser.add_argument("--force", action="store_true", help="Перезаписать существующие фильмы")
    
    args = parser.parse_args()
    
    # Переопределяем настройки из аргументов
    if args.user_id:
        settings.DEFAULT_CREATED_BY_USER_ID = args.user_id
    
    if args.js_file:
        settings.MOVIES_JS_FILE_PATH = args.js_file
    
    sys.exit(load_movies())