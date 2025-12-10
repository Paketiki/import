# app/scripts/load_test_data.py
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.database.database import get_db, init_db
from app.services.movies import MovieService
from app.services.users import UserService
from app.services.auth import AuthService
from app.schemas.movies import MovieCreate
from app.schemas.users import UserCreate

async def load_test_data():
    await init_db()
    
    # Получаем сессию БД
    db = await anext(get_db())
    
    # Создаем тестового пользователя
    user_service = UserService(db)
    test_user = await user_service.create_user(UserCreate(
        username="testuser",
        password="test123",
        email="test@example.com"
    ))
    
    # Создаем тестовые фильмы
    movie_service = MovieService(db)
    
    test_movies = [
        MovieCreate(
            title="Побег из Шоушенка",
            year=1994,
            rating=9.3,
            genre="Драма, Криминал",
            poster_url="https://example.com/shawshank.jpg",
            overview="Два заключенных на протяжении многих лет ищут способ обрести свободу и искупить свои грехи.",
            picks=["hits", "classic"]
        ),
        MovieCreate(
            title="Крестный отец",
            year=1972,
            rating=9.2,
            genre="Криминал, Драма",
            poster_url="https://example.com/godfather.jpg",
            overview="Старший сын главы могущественной преступной семьи возвращается домой после Второй мировой войны.",
            picks=["classic"]
        ),
        MovieCreate(
            title="Темный рыцарь",
            year=2008,
            rating=9.0,
            genre="Боевик, Криминал, Драма",
            poster_url="https://example.com/darkknight.jpg",
            overview="Бэтмен противостоит Джокеру, терроризирующему Готэм-Сити.",
            picks=["hits"]
        ),
        MovieCreate(
            title="Интерстеллар",
            year=2014,
            rating=8.6,
            genre="Приключения, Драма, Фантастика",
            poster_url="https://example.com/interstellar.jpg",
            overview="Группа исследователей использует недавно обнаруженный пространственно-временной тоннель.",
            picks=["hits", "new"]
        ),
    ]
    
    for movie_data in test_movies:
        await movie_service.create_movie(movie_data, test_user.id)
    
    print("✅ Тестовые данные успешно загружены!")
    print(f"👤 Тестовый пользователь: testuser / test123")
    print(f"🎬 Загружено фильмов: {len(test_movies)}")

if __name__ == "__main__":
    asyncio.run(load_test_data())