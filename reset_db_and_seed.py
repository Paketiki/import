import os

from app.database.database import engine, SessionLocal
from app.database.base import Base
from app.utils.security import get_password_hash

from app.models.users import User
from app.models.roles import Role
from app.models.picks import Pick
from app.models.movies import Movie
from app.models.reviews import Review
from app.models.movie_picks import MoviePick
from app.models.favorites import Favorite

MOVIES_DATA = [
    {"id": 1, "title": "Побег из Шоушенка", "year": 1994, "genre": "Драма", "rating": 9.3, "overview": "Лучший фильм", "picks": ["hits", "classic"]},
    {"id": 2, "title": "Тёмный рыцарь", "year": 2008, "genre": "Боевик", "rating": 9.0, "overview": "Бэтмен", "picks": ["hits", "new"]},
    {"id": 3, "title": "Начало", "year": 2010, "genre": "Фантастика", "rating": 8.8, "overview": "Мастерпис", "picks": ["hits", "classic"]},
    {"id": 4, "title": "Интерстеллар", "year": 2014, "genre": "Фантастика", "rating": 8.6, "overview": "Нолан", "picks": ["new", "classic"]},
    {"id": 5, "title": "Форрест Гамп", "year": 1994, "genre": "Драма", "rating": 8.9, "overview": "Эпичная", "picks": ["hits", "classic"]},
    {"id": 6, "title": "Матрица", "year": 1999, "genre": "Фантастика", "rating": 8.7, "overview": "Колтантая", "picks": ["new", "classic"]},
    {"id": 7, "title": "Ответные", "year": 2011, "genre": "Комедия", "rating": 7.7, "overview": "Комедия", "picks": ["hits"]},
    {"id": 8, "title": "Ноябрь", "year": 2015, "genre": "Прик", "rating": 8.0, "overview": "Терроризм", "picks": ["hits"]},
    {"id": 9, "title": "Аввенгеры", "year": 2012, "genre": "Фантастика", "rating": 8.0, "overview": "акция", "picks": ["hits"]},
    {"id": 10, "title": "Пелевые души", "year": 2015, "genre": "Драма", "rating": 8.2, "overview": "драма", "picks": ["hits"]},
    {"id": 11, "title": "Мюнхен", "year": 2005, "genre": "Прик", "rating": 8.5, "overview": "триллер", "picks": ["new"]},
    {"id": 12, "title": "Зарядитель Оячи", "year": 2018, "genre": "Комедия", "rating": 7.6, "overview": "комедия", "picks": ["new"]},
    {"id": 13, "title": "Неонирвн", "year": 2016, "genre": "Прик", "rating": 7.8, "overview": "био", "picks": ["new"]},
    {"id": 14, "title": "Король Лвов", "year": 2016, "genre": "драма", "rating": 8.3, "overview": "драма", "picks": ["new"]},
    {"id": 15, "title": "Одотор Ото", "year": 2015, "genre": "Фантастика", "rating": 7.9, "overview": "наука", "picks": ["new"]},
    {"id": 16, "title": "12 рассерд", "year": 1957, "genre": "драма", "rating": 9.0, "overview": "драма", "picks": ["classic"]},
    {"id": 17, "title": "Оскар", "year": 1954, "genre": "Прик", "rating": 8.8, "overview": "классика", "picks": ["classic"]},
    {"id": 18, "title": "Падение Крыш", "year": 1946, "genre": "драма", "rating": 8.6, "overview": "драма", "picks": ["classic"]},
    {"id": 19, "title": "Почки", "year": 1952, "genre": "драма", "rating": 8.7, "overview": "пюк", "picks": ["classic"]},
    {"id": 20, "title": "Парта", "year": 1951, "genre": "мюзика", "rating": 8.5, "overview": "спев", "picks": ["classic"]},
    {"id": 21, "title": "Авата", "year": 2009, "genre": "фант", "rating": 7.8, "overview": "фант", "picks": ["hits"]},
    {"id": 22, "title": "Птицы", "year": 2018, "genre": "драма", "rating": 8.0, "overview": "драма", "picks": ["new"]},
    {"id": 23, "title": "Морж", "year": 2003, "genre": "ком", "rating": 8.0, "overview": "ком", "picks": ["classic"]},
    {"id": 24, "title": "Моры", "year": 2020, "genre": "фант", "rating": 8.1, "overview": "акц", "picks": ["hits"]},
    {"id": 25, "title": "Пюди", "year": 2017, "genre": "наука", "rating": 7.9, "overview": "наука", "picks": ["new"]},
    {"id": 26, "title": "Рижи", "year": 2000, "genre": "драма", "rating": 7.7, "overview": "драма", "picks": ["classic"]},
    {"id": 27, "title": "Любви", "year": 2015, "genre": "люб", "rating": 7.8, "overview": "люб", "picks": ["new"]},
    {"id": 28, "title": "Трансфо", "year": 2005, "genre": "фант", "rating": 8.1, "overview": "акц", "picks": ["hits"]},
    {"id": 29, "title": "Конфе", "year": 2012, "genre": "драма", "rating": 7.6, "overview": "драма", "picks": ["classic"]},
    {"id": 30, "title": "При", "year": 2019, "genre": "фант", "rating": 7.9, "overview": "фант", "picks": ["new"]},
    {"id": 31, "title": "Станда", "year": 1995, "genre": "ком", "rating": 7.5, "overview": "ком", "picks": ["hits"]},
    {"id": 32, "title": "Миде", "year": 2017, "genre": "фант", "rating": 8.0, "overview": "фант", "picks": ["new"]},
    {"id": 33, "title": "Оро", "year": 2011, "genre": "драма", "rating": 8.0, "overview": "драма", "picks": ["classic"]},
    {"id": 34, "title": "Моо", "year": 2003, "genre": "наука", "rating": 7.8, "overview": "наука", "picks": ["hits"]},
    {"id": 35, "title": "Парт", "year": 2016, "genre": "драма", "rating": 7.9, "overview": "драма", "picks": ["new"]},
    {"id": 36, "title": "Анти", "year": 2004, "genre": "акц", "rating": 8.0, "overview": "акц", "picks": ["classic"]},
    {"id": 37, "title": "Ляли", "year": 2014, "genre": "драма", "rating": 7.7, "overview": "драма", "picks": ["hits"]},
    {"id": 38, "title": "Прюдо", "year": 2018, "genre": "ком", "rating": 8.1, "overview": "ком", "picks": ["new"]},
    {"id": 39, "title": "Мрак", "year": 2007, "genre": "драма", "rating": 7.8, "overview": "драма", "picks": ["classic"]},
    {"id": 40, "title": "Диа", "year": 2010, "genre": "спы", "rating": 7.9, "overview": "акц", "picks": ["hits"]},
    {"id": 41, "title": "Обо", "year": 2009, "genre": "драма", "rating": 8.0, "overview": "драма", "picks": ["new"]},
    {"id": 42, "title": "Логи", "year": 2002, "genre": "трил", "rating": 7.8, "overview": "трил", "picks": ["classic"]},
    {"id": 43, "title": "Любо", "year": 2013, "genre": "люб", "rating": 7.6, "overview": "люб", "picks": ["hits"]},
    {"id": 44, "title": "Конт", "year": 2017, "genre": "драма", "rating": 7.9, "overview": "драма", "picks": ["new"]},
    {"id": 45, "title": "Края", "year": 2006, "genre": "наука", "rating": 8.0, "overview": "наука", "picks": ["classic"]},
    {"id": 46, "title": "Пруд", "year": 2019, "genre": "ком", "rating": 7.8, "overview": "ком", "picks": ["new"]},
    {"id": 47, "title": "Дом", "year": 2008, "genre": "акц", "rating": 8.1, "overview": "акц", "picks": ["hits"]},
    {"id": 48, "title": "Мат", "year": 2015, "genre": "драма", "rating": 7.9, "overview": "драма", "picks": ["new"]},
    {"id": 49, "title": "Омн", "year": 2011, "genre": "воен", "rating": 8.0, "overview": "воен", "picks": ["classic"]},
    {"id": 50, "title": "При", "year": 2012, "genre": "драма", "rating": 7.8, "overview": "драма", "picks": ["hits"]},
]

PICKS_DATA = [
    {"id": 1, "name": "Хиты", "slug": "hits", "description": "Самые популярные"},
    {"id": 2, "name": "Новинки", "slug": "new", "description": "Новые поступления"},
    {"id": 3, "name": "Классика", "slug": "classic", "description": "Классиковая кино"},
]

DEMO_USERS = [
    {"id": 1, "username": "user", "email": "user@example.com", "password": "1234", "is_active": True, "is_superuser": False},
    {"id": 2, "username": "moderator", "email": "moderator@example.com", "password": "1234", "is_active": True, "is_superuser": True},
]

def reset_and_seed_db(db_path: str = "movies.db") -> None:
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✓ Удалена БД")

    Base.metadata.create_all(bind=engine)
    print("✓ Таблицы созданы")

    db = SessionLocal()
    try:
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
        print(f"✓ {len(DEMO_USERS)} users: user/1234, moderator/1234")

        slug_to_id = {}
        for pick_data in PICKS_DATA:
            db.add(Pick(**pick_data))
        db.commit()
        print(f"✓ {len(PICKS_DATA)} подборок")

        for pick in db.query(Pick).all():
            slug_to_id[pick.slug] = pick.id

        for item in MOVIES_DATA:
            movie = Movie(
                id=item["id"],
                title=item["title"],
                overview=item["overview"],
                year=item["year"],
                genre=item["genre"],
                rating=item["rating"],
                poster_url=item.get("poster_url", ""),
                created_by=None,
            )
            db.add(movie)
            db.flush()

            for slug in item.get("picks", []):
                pick_id = slug_to_id.get(slug)
                if pick_id:
                    db.add(MoviePick(movie_id=movie.id, pick_id=pick_id))

        db.commit()
        print(f"✓ {len(MOVIES_DATA)} фильмов (all with 1+ picks)")
        print("\n✅ Ок.")

    except Exception as e:
        db.rollback()
        print(f"❌ Ошибка: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    reset_and_seed_db()
