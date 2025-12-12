import os

from app.database.database import engine, SessionLocal
from app.database.base import Base  # Импортируем Base из base.py
from app.utils.security import get_password_hash

# Импортируем ВСЕ модели, чтобы они зарегистрировались в metadata
# ВАЖНО: это нужно, чтобы все FK были видны SQLAlchemy
from app.models.users import User  # noqa: F401
from app.models.roles import Role  # noqa: F401
from app.models.picks import Pick  # noqa: F401
from app.models.movies import Movie  # noqa: F401
from app.models.reviews import Review  # noqa: F401
from app.models.movie_picks import MoviePick  # noqa: F401
from app.models.favorites import Favorite  # noqa: F401

MOVIES_DATA = [
    {
        "id": 1,
        "title": "Побег из Шоушенка",
        "year": 1994,
        "genre": "Драма",
        "rating": 9.3,
        "poster_url": "",
        "overview": "Банкир Энди Дюфрейн, обвинённый в убийстве жены и её любовника, попадает в тюрьму Шоушенк.",
        "picks": ["hits", "classic"],
    },
    {
        "id": 2,
        "title": "Тёмный рыцарь",
        "year": 2008,
        "genre": "Боевик",
        "rating": 9.0,
        "poster_url": "",
        "overview": "Бэтмен вступает в смертельную игру с Джокером, чья цель — погружить город в хаос.",
        "picks": ["hits", "new"],
    },
    {
        "id": 3,
        "title": "Начало",
        "year": 2010,
        "genre": "Фантастика",
        "rating": 8.8,
        "poster_url": "",
        "overview": "Профессиональный вор, специализирующийся на проникновении в сны, получает шанс на искупление.",
        "picks": ["hits", "classic"],
    },
    {
        "id": 4,
        "title": "Интерстеллар",
        "year": 2014,
        "genre": "Фантастика",
        "rating": 8.6,
        "poster_url": "",
        "overview": "Команда исследователей отправляется через чёрную дыру в поисках нового дома для человечества.",
        "picks": ["new", "classic"],
    },
    {
        "id": 5,
        "title": "Форрест Гамп",
        "year": 1994,
        "genre": "Драма",
        "rating": 8.9,
        "poster_url": "",
        "overview": "История простодушного Форреста, который становится свидетелем важнейших событий в истории УСА.",
        "picks": ["hits", "classic"],
    },
    {
        "id": 6,
        "title": "Матрица",
        "year": 1999,
        "genre": "Фантастика",
        "rating": 8.7,
        "poster_url": "",
        "overview": "Программист Нео узнаёт, что реальность — всего лишь симуляция, созданная машинами.",
        "picks": ["new", "classic"],
    },
]

PICKS_DATA = [
    {"id": 1, "name": "Хиты", "slug": "hits", "description": "Самые популярные фильмы"},
    {"id": 2, "name": "Новинки", "slug": "new", "description": "Новые поступления"},
    {"id": 3, "name": "Классика", "slug": "classic", "description": "Великие классические фильмы"},
]

DEMO_USERS = [
    {
        "id": 1,
        "username": "user",
        "email": "user@example.com",
        "password": "1234",
        "is_active": True,
        "is_superuser": False,
    },
    {
        "id": 2,
        "username": "moderator",
        "email": "moderator@example.com",
        "password": "1234",
        "is_active": True,
        "is_superuser": True,
    },
]


def reset_and_seed_db(db_path: str = "movies.db") -> None:
    """Полностью пересоздать базу и заполнить её начальными фильмами и подборками."""
    # 1. Удаляем старую БД, если есть
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ Удалена старая база данных {db_path}")

    # 2. Создаем таблицы
    # ВАЖНО: все модели уже зарегистрированы в единых Base родителях
    Base.metadata.create_all(bind=engine)
    print("✓ Таблицы созданы")

    # 3. Заполняем данными
    db = SessionLocal()
    try:
        # Добавляем демо-пользователей
        for user_data in DEMO_USERS:
            user = User(
                id=user_data["id"],
                username=user_data["username"],
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                is_active=user_data["is_active"],
                is_superuser=user_data["is_superuser"],
            )
            db.add(user)
        db.commit()
        print(f"✓ Добавлено {len(DEMO_USERS)} пользователей (demo: user/1234, moderator/1234)")

        # Сначала добавляем подборки
        slug_to_id = {}
        for pick_data in PICKS_DATA:
            pick = Pick(**pick_data)
            db.add(pick)
        db.commit()
        print(f"✓ Добавлено {len(PICKS_DATA)} подборок")

        # Маппим slug → id для связей
        for pick in db.query(Pick).all():
            slug_to_id[pick.slug] = pick.id

        # Теперь добавляем фильмы
        for item in MOVIES_DATA:
            movie = Movie(
                id=item["id"],
                title=item["title"],
                overview=item["overview"],
                year=item["year"],
                genre=item["genre"],
                rating=item["rating"],
                poster_url=item["poster_url"],
                created_by=None,
            )
            db.add(movie)
            db.flush()

            # Добавляем связи с подборками (равно 2 на каждый фильм)
            for slug in item.get("picks", []):
                pick_id = slug_to_id.get(slug)
                if pick_id:
                    db.add(MoviePick(movie_id=movie.id, pick_id=pick_id))

        db.commit()
        print(f"✓ Добавлено {len(MOVIES_DATA)} фильмов (each in 2 picks)")
        print("\n✅ База данных успешно пересоздана и заполнена!")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка при заполнении БД: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    reset_and_seed_db()
