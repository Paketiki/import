import os

from app.database import database as db_sync
from app.database import base as db_base

# Импортируем модели, чтобы они зарегистрировались в metadata
from app.models import movies as _movies  # noqa: F401
from app.models import picks as _picks  # noqa: F401
from app.models import movie_picks as _movie_picks  # noqa: F401
from app.models import users as _users  # noqa: F401

from app.models.movies import Movie
from app.models.picks import Pick
from app.models.movie_picks import MoviePick


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
        "overview": "Бэтмен вступает в смертельную игру с Джокером, чья цель — погрузить город в хаос.",
        "picks": ["hits"],
    },
    # ... остальные фильмы из списка пользователя нужно дописать по аналогии
]

PICKS_DATA = [
    {"id": 1, "name": "Хиты", "slug": "hits", "description": "Самые популярные фильмы"},
    {"id": 2, "name": "Новинки", "slug": "new", "description": "Новые поступления"},
    {"id": 3, "name": "Классика", "slug": "classic", "description": "Великие классические фильмы"},
]


def reset_and_seed_db(db_path: str = "movies.db") -> None:
    """Полностью пересоздать базу и заполнить её начальными фильмами и подборками."""
    # 1. Удаляем старую БД, если есть
    if os.path.exists(db_path):
        os.remove(db_path)

    # 2. Создаём таблицы для двух разных Base
    db_sync.Base.metadata.create_all(bind=db_sync.engine)
    db_base.Base.metadata.create_all(bind=db_sync.engine)

    # 3. Заполняем данными
    db = db_sync.SessionLocal()
    try:
        # Подборки
        slug_to_id = {}
        for pick_data in PICKS_DATA:
            pick = Pick(**pick_data)
            db.add(pick)
        db.commit()

        for pick in db.query(Pick).all():
            slug_to_id[pick.slug] = pick.id

        # Фильмы
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

            for slug in item.get("picks", []):
                pick_id = slug_to_id.get(slug)
                if pick_id:
                    db.add(MoviePick(movie_id=movie.id, pick_id=pick_id))

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    reset_and_seed_db()
    print("База данных пересоздана и заполнена начальными фильмами.")
