# app/database/db_manager.py
from .database import engine, Base, init_db as db_init_db
from sqlalchemy.orm import Session

def init_db():
    """Публичная функция для инициализации БД"""
    return db_init_db()

def create_tables():
    """Создание таблиц в БД"""
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы базы данных созданы")

def drop_tables():
    """Удаление всех таблиц (только для разработки!)"""
    if __name__ == "__main__":  # Защита от случайного запуска
        Base.metadata.drop_all(bind=engine)
        print("⚠️ Все таблицы удалены")

def get_session() -> Session:
    """Получение новой сессии БД"""
    from .database import SessionLocal
    return SessionLocal()

# Если файл запускается напрямую
if __name__ == "__main__":
    create_tables()