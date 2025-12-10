import sys
import os
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import SessionLocal, init_db
from app.models.movies import Movie
from app.models.picks import Pick
from app.models.movie_picks import MoviePick
from app.models.reviews import Review
from app.models.users import User
from app.models.roles import Role

# Данные фильмов из вашего списка
MOVIES_DATA = [
    {
        "id": 1,
        "title": "Побег из Шоушенка",
        "year": 1994,
        "genre": "Драма",
        "rating": 9.3,
        "picks": ["hits", "classic"],
        "poster": "https://picsum.photos/seed/film1/200/300",
        "overview": "Банкир Энди Дюфрейн, обвинённый в убийстве жены и её любовника, попадает в тюрьму Шоушенк.",
        "review": "Фильм о силе надежды и достоинства, который мягко подводит к мощному катарсису и долго не отпускает после финала.",
        "extraReviews": ["Один из тех редких случаев, когда душевность и драматизм идеально уравновешены."],
    },
    {
        "id": 2,
        "title": "Тёмный рыцарь",
        "year": 2008,
        "genre": "Боевик",
        "rating": 9.0,
        "picks": ["hits"],
        "poster": "https://picsum.photos/seed/film2/200/300",
        "overview": "Бэтмен вступает в смертельную игру с Джокером, чья цель — погрузить город в хаос.",
        "review": "Нолан превращает супергеройский фильм в мрачную криминальную драму с одним из лучших злодеев в истории кино.",
        "extraReviews": ["Напряжение не спадает ни на минуту, а моральные дилеммы героев остаются в голове надолго."],
    },
    {
        "id": 3,
        "title": "Начало",
        "year": 2010,
        "genre": "Фантастика",
        "rating": 8.8,
        "picks": ["hits", "new"],
        "poster": "https://picsum.photos/seed/film3/200/300",
        "overview": "Профессиональный вор, специализирующийся на проникновении в сны, получает шанс на искупление.",
        "review": "Интеллектуальный блокбастер, который предлагает зрителю собрать головоломку из снов и воспоминаний.",
        "extraReviews": ["Фильм, к которому хочется возвращаться, чтобы заметить новые детали в каждом уровне сна."],
    },
    {
        "id": 4,
        "title": "Интерстеллар",
        "year": 2014,
        "genre": "Фантастика",
        "rating": 8.6,
        "picks": ["hits", "new"],
        "poster": "https://picsum.photos/seed/film4/200/300",
        "overview": "Команда исследователей отправляется через червоточину в поисках нового дома для человечества.",
        "review": "Космическая драма о родительской любви и цене прогресса, совмещающая научные идеи и искренние эмоции.",
        "extraReviews": ["Редкий пример фильма, где масштаб вселенной не перекрывает человеческую историю."],
    },
    {
        "id": 5,
        "title": "Форрест Гамп",
        "year": 1994,
        "genre": "Драма",
        "rating": 8.9,
        "picks": ["classic"],
        "poster": "https://picsum.photos/seed/film5/200/300",
        "overview": "История простодушного Форреста, который становится свидетелем важнейших событий в истории США.",
        "review": "Трогательная притча о доброте и принятии, в которой хочется улыбаться и плакать одновременно.",
        "extraReviews": ["Фильм, к которому возвращаются как к старому другу — он всегда дарит немного тепла."],
    },
    
    # Добавьте остальные фильмы по аналогии...
]

# Полный список подборок
PICKS_DATA = [
    {"id": 1, "name": "Все фильмы", "slug": "all"},
    {"id": 2, "name": "Хиты", "slug": "hits"},
    {"id": 3, "name": "Новинки", "slug": "new"},
    {"id": 4, "name": "Классика", "slug": "classic"},
]

def load_data():
    """Загружает фильмы и подборки в базу данных"""
    db = SessionLocal()
    
    try:
        print("Начало загрузки данных...")
        
        # Создаем тестового пользователя (если нет)
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            role = db.query(Role).filter(Role.name == "Администратор").first()
            if not role:
                role = Role(name="Администратор", description="Администратор системы")
                db.add(role)
                db.commit()
            
            user = User(
                username="admin",
                email="admin@example.com",
                password_hash="temp_hash",  # В реальном приложении нужно хэшировать
                role_id=role.id
            )
            db.add(user)
            db.commit()
        
        # Создаем подборки
        picks_map = {}
        for pick_data in PICKS_DATA:
            pick = db.query(Pick).filter(Pick.slug == pick_data["slug"]).first()
            if not pick:
                pick = Pick(
                    name=pick_data["name"],
                    slug=pick_data["slug"],
                    description=f"Подборка {pick_data['name']}"
                )
                db.add(pick)
                db.commit()
                db.refresh(pick)
            picks_map[pick_data["slug"]] = pick
            print(f"Создана подборка: {pick.name}")
        
        # Загружаем фильмы
        for movie_data in MOVIES_DATA[:10]:  # Для начала загрузим 10 фильмов
            # Проверяем, существует ли фильм
            existing_movie = db.query(Movie).filter(Movie.id == movie_data["id"]).first()
            
            if existing_movie:
                print(f"Фильм '{movie_data['title']}' уже существует, пропускаем...")
                continue
            
            # Создаем фильм
            movie = Movie(
                id=movie_data["id"],
                title=movie_data["title"],
                year=movie_data["year"],
                genre=movie_data["genre"],
                rating=movie_data["rating"],
                overview=movie_data["overview"],
                poster_url=movie_data["poster"],
                created_by=user.id
            )
            
            db.add(movie)
            db.commit()
            db.refresh(movie)
            
            # Добавляем фильм в подборки
            for pick_slug in movie_data.get("picks", []):
                if pick_slug in picks_map:
                    movie_pick = MoviePick(
                        movie_id=movie.id,
                        pick_id=picks_map[pick_slug].id
                    )
                    db.add(movie_pick)
            
            # Создаем основную рецензию
            if "review" in movie_data:
                review = Review(
                    movie_id=movie.id,
                    user_id=user.id,
                    text=movie_data["review"],
                    rating=movie_data["rating"]
                )
                db.add(review)
                
                # Добавляем дополнительные рецензии
                for extra_review in movie_data.get("extraReviews", []):
                    extra = Review(
                        movie_id=movie.id,
                        user_id=user.id,
                        text=extra_review,
                        rating=movie_data["rating"] - 0.5  # Примерный рейтинг
                    )
                    db.add(extra)
            
            db.commit()
            print(f"Добавлен фильм: {movie.title}")
        
        print("Загрузка данных завершена успешно!")
        
    except Exception as e:
        print(f"Ошибка при загрузке данных: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    load_data()